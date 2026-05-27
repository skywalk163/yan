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

print("Testing WASM generation with detailed hex dump...")
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
    print("\nWASM hex dump:")
    
    # 按字节打印，每行16字节
    for i in range(0, len(wasm_bytes), 16):
        line = wasm_bytes[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in line)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in line)
        print(f"0x{i:04x}: {hex_str.ljust(47)} | {ascii_str}")
    
    # 检查偏移量 96 附近
    print(f"\n\nChecking offset 96 (0x{96:04x}):")
    offset = 96
    if offset < len(wasm_bytes):
        print(f"Byte at 0x{offset:04x}: 0x{wasm_bytes[offset]:02x}")
        # 显示周围的字节
        start = max(0, offset - 8)
        end = min(len(wasm_bytes), offset + 8)
        print(f"Context (0x{start:04x}-0x{end:04x}):")
        for i in range(start, end):
            print(f"  0x{i:04x}: 0x{wasm_bytes[i]:02x}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()