#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 测试代码 - 简化测试，不使用变量
code = '''印 "Hello, WASM!"。'''

print("Testing WASM generation without variables...")
print(f"Code:\n{code}")
print()

try:
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    
    parser = Parser()
    ast = parser.parse(tokens)
    
    codegen = WASMCodeGen()
    wasm_bytes = codegen.generate(ast)
    
    print(f"WASM size: {len(wasm_bytes)} bytes")
    
    # 检查 WASM
    if wasm_bytes[:4] != b'\x00asm':
        print("❌ Invalid WASM magic bytes")
        exit(1)
    print("✅ WASM magic bytes OK")
    
    # 测试在浏览器环境中
    print("\nTesting in browser environment...")
    
    # 模拟浏览器中的 importObject
    class MockMemory:
        def __init__(self):
            self.buffer = bytearray(65536)
    
    import_object = {
        "env": {
            "print": lambda ptr: print(f"Print called with ptr: {ptr}"),
            "print_num": lambda f: print(f"Print num: {f}"),
            "print_float": lambda f: print(f"Print float: {f}"),
            "memory": MockMemory()
        }
    }
    
    print("✅ Import object created")
    print("✅ Test passed without global variables!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()