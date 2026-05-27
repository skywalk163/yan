#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 测试代码
code = '''印 "Hello, WASM!"。
定 x = 42。
印数 x。'''

print("Debugging WASM instructions...")
print(f"Code:\n{code}")
print()

try:
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    
    parser = Parser()
    ast = parser.parse(tokens)
    
    codegen = WASMCodeGen()
    
    # 先生成代码来收集全局变量
    code_bytes = codegen._gen_code_section(ast)
    
    print("Generated instructions (hex):")
    print(code_bytes.hex())
    
    print("\n\nDisassembling:")
    offset = 0
    while offset < len(code_bytes):
        byte = code_bytes[offset]
        print(f"0x{offset:04x}: 0x{byte:02x} ", end='')
        
        if byte == 0x41:  # i32.const
            # 读取后面的 varuint
            offset += 1
            val = 0
            shift = 0
            while offset < len(code_bytes):
                b = code_bytes[offset]
                val |= (b & 0x7f) << shift
                offset += 1
                if not (b & 0x80):
                    break
                shift += 7
            print(f"i32.const {val}")
            
        elif byte == 0x10:  # call
            offset += 1
            idx = 0
            shift = 0
            while offset < len(code_bytes):
                b = code_bytes[offset]
                idx |= (b & 0x7f) << shift
                offset += 1
                if not (b & 0x80):
                    break
                shift += 7
            print(f"call {idx}")
            
        elif byte == 0x24:  # global.set
            offset += 1
            idx = 0
            shift = 0
            while offset < len(code_bytes):
                b = code_bytes[offset]
                idx |= (b & 0x7f) << shift
                offset += 1
                if not (b & 0x80):
                    break
                shift += 7
            print(f"global.set {idx}")
            
        elif byte == 0x23:  # global.get
            offset += 1
            idx = 0
            shift = 0
            while offset < len(code_bytes):
                b = code_bytes[offset]
                idx |= (b & 0x7f) << shift
                offset += 1
                if not (b & 0x80):
                    break
                shift += 7
            print(f"global.get {idx}")
            
        elif byte == 0x0b:  # end
            print("end")
            offset += 1
            
        elif byte == 0x00:  # local count
            print("local count 0")
            offset += 1
            
        else:
            print(f"unknown opcode")
            offset += 1
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()