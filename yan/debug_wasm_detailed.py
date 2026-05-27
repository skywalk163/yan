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

print("Testing WASM generation with detailed analysis...")
print(f"Code:\n{code}")
print()

try:
    # 编译流程
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    print("✅ Lexer done")
    
    parser = Parser()
    ast = parser.parse(tokens)
    print("✅ Parser done")
    
    codegen = WASMCodeGen()
    wasm_bytes = codegen.generate(ast)
    print(f"✅ Codegen done")
    print(f"WASM size: {len(wasm_bytes)} bytes")
    
    # 十六进制输出
    hex_str = wasm_bytes.hex()
    print(f"\nWASM hex dump (grouped by section):")
    
    # 解析段结构
    offset = 0
    
    # 魔法字节和版本
    print(f"[0x{offset:04x}] Magic: {hex_str[offset*2:offset*2+8]}")
    offset += 4
    print(f"[0x{offset:04x}] Version: {hex_str[offset*2:offset*2+8]}")
    offset += 4
    
    section_names = {
        0x01: 'Type',
        0x02: 'Import',
        0x03: 'Function',
        0x05: 'Memory',
        0x06: 'Global',
        0x07: 'Export',
        0x09: 'Element',
        0x0a: 'Code',
        0x0b: 'Data',
    }
    
    while offset < len(wasm_bytes):
        section_id = wasm_bytes[offset]
        offset += 1
        
        if section_id == 0:
            break
            
        # 读取长度（varuint）
        size = 0
        shift = 0
        size_bytes = []
        while offset < len(wasm_bytes):
            byte = wasm_bytes[offset]
            size_bytes.append(byte)
            offset += 1
            size |= (byte & 0x7f) << shift
            if not (byte & 0x80):
                break
            shift += 7
        
        section_name = section_names.get(section_id, f'Unknown({section_id})')
        hex_start = (offset - len(size_bytes) - 1) * 2
        hex_end = offset * 2 + size * 2
        
        print(f"\n[0x{(offset - len(size_bytes) - 1):04x}] Section {section_id} ({section_name}):")
        print(f"  Size: {size} bytes")
        print(f"  Size encoding: {bytes(size_bytes).hex()}")
        
        # 检查是否有足够的数据
        if offset + size > len(wasm_bytes):
            print(f"  ❌ ERROR: Needs {size} bytes but only {len(wasm_bytes) - offset} available!")
            break
        
        # 显示段内容的十六进制
        content_hex = hex_str[offset*2:(offset+size)*2]
        print(f"  Content: {content_hex}")
        
        offset += size
    
    if offset == len(wasm_bytes):
        print("\n✅ WASM structure is valid!")
    else:
        print(f"\n❌ WASM structure is INCOMPLETE! Expected end at {len(wasm_bytes)}, got to {offset}")
        
    # 检查段顺序
    print("\n=== Section Order Analysis ===")
    print("Expected order: Type(1) -> Import(2) -> Function(3) -> Global(6) -> Element(9) -> Code(10) -> Data(11) -> Export(7)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()