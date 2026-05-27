#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 包含函数定义的代码
code = '''定 问候 = 函 名
  连 "你好，" 名 "！"。

印 问候 "世界"。'''

print("Debugging WASM with function...")
print(f"Code:\n{code}")
print()

try:
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    
    parser = Parser()
    ast = parser.parse(tokens)
    
    codegen = WASMCodeGen()
    code_bytes = codegen._gen_code_section(ast)
    
    print(f"Code section (hex): {code_bytes.hex()}")
    print()
    
    # 解析 Code 段
    offset = 0
    func_count = code_bytes[offset]
    print(f"Function count: {func_count}")
    offset += 1
    
    func_names = ['问候', 'main']
    
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
        
        print(f"\n=== Function {i} ({func_names[i] if i < len(func_names) else 'unknown'}) ===")
        print(f"Body size: {size} bytes")
        
        body = code_bytes[offset:offset+size]
        offset += size
        
        # 反汇编
        body_offset = 0
        stack_size = 0
        
        while body_offset < len(body):
            byte = body[body_offset]
            print(f"0x{body_offset:04x}: 0x{byte:02x} ", end='')
            
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
                stack_size += 1
                
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
                stack_size -= 1  # 假设消耗1个参数
                
            elif byte == 0x6a:  # i32.add
                print("i32.add")
                body_offset += 1
                stack_size -= 1
                
            elif byte == 0x0b:  # end
                print(f"end (stack: {stack_size})")
                body_offset += 1
                
            elif byte == 0x00:  # local count 0
                print("local 0")
                body_offset += 1
                
            else:
                print(f"unknown")
                body_offset += 1
                
            if byte not in [0x0b, 0x00]:
                print(f"      Stack: {stack_size}")
                
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()