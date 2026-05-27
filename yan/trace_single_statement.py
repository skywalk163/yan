#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 测试代码 - 单条打印语句
code = '''印 "Hello"。'''

print("Testing single print statement...")
print(f"Code: {code}")
print()

try:
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    print(f"Tokens: {tokens}")
    
    parser = Parser()
    ast = parser.parse(tokens)
    print(f"AST: {ast}")
    print(f"Statements: {ast.statements}")
    
    codegen = WASMCodeGen()
    
    # 先生成代码来收集全局变量
    code_bytes = codegen._gen_code_section(ast)
    
    print(f"\nGenerated code bytes (hex): {code_bytes.hex()}")
    
    # 解析 Code 段结构
    offset = 0
    print("\nParsing Code section structure:")
    
    # 函数数量
    func_count = code_bytes[offset]
    print(f"Function count: {func_count}")
    offset += 1
    
    for i in range(func_count):
        # 函数体大小
        size = 0
        shift = 0
        while offset < len(code_bytes):
            b = code_bytes[offset]
            size |= (b & 0x7f) << shift
            offset += 1
            if not (b & 0x80):
                break
            shift += 7
        
        print(f"\nFunction {i} body size: {size} bytes")
        
        # 函数体
        body = code_bytes[offset:offset+size]
        print(f"Function {i} body (hex): {body.hex()}")
        
        # 反汇编
        print("Disassembly:")
        body_offset = 0
        while body_offset < len(body):
            byte = body[body_offset]
            print(f"  0x{body_offset:04x}: 0x{byte:02x} ", end='')
            
            if byte == 0x41:  # i32.const
                body_offset += 1
                val = 0
                shift = 0
                while body_offset < len(body):
                    b = body[body_offset]
                    val |= (b & 0x7f) << shift
                    body_offset += 1
                    if not (b & 0x80):
                        break
                    shift += 7
                print(f"i32.const {val}")
                
            elif byte == 0x10:  # call
                body_offset += 1
                idx = 0
                shift = 0
                while body_offset < len(body):
                    b = body[body_offset]
                    idx |= (b & 0x7f) << shift
                    body_offset += 1
                    if not (b & 0x80):
                        break
                    shift += 7
                print(f"call {idx}")
                
            elif byte == 0x0b:  # end
                print("end")
                body_offset += 1
                
            elif byte == 0x00:  # local count 0
                print("local 0")
                body_offset += 1
                
            else:
                print(f"unknown")
                body_offset += 1
        
        offset += size
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()