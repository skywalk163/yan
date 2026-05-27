#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 测试代码 - 简单的算术运算
code = '''印数 加 1 2。'''

print("Testing arithmetic operation...")
print(f"Code: {code}")
print()

try:
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    print(f"Tokens: {tokens}")
    
    parser = Parser()
    ast = parser.parse(tokens)
    print(f"AST: {ast}")
    
    codegen = WASMCodeGen()
    code_bytes = codegen._gen_code_section(ast)
    
    print(f"\nGenerated code (hex): {code_bytes.hex()}")
    
    # 解析 Code 段
    offset = 0
    func_count = code_bytes[offset]
    offset += 1
    print(f"Function count: {func_count}")
    
    for i in range(func_count):
        size = 0
        shift = 0
        while offset < len(code_bytes):
            b = code_bytes[offset]
            size |= (b & 0x7f) << shift
            offset += 1
            if not (b & 0x80):
                break
            shift += 7
        
        body = code_bytes[offset:offset+size]
        print(f"\nFunction {i} body (hex): {body.hex()}")
        
        # 反汇编
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
                
            elif byte == 0x6a:  # i32.add
                print("i32.add")
                body_offset += 1
                
            elif byte == 0x0b:  # end
                print("end")
                body_offset += 1
                
            elif byte == 0x00:  # local 0
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