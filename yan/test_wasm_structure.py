#!/usr/bin/env python3
import requests
import json
import base64

# 测试 WASM 编译和解析
url = "http://localhost:5000/api/compile-wasm"
data = {"code": '印 "Hello, WASM!"。\n定 x = 42。\n印数 x。'}
headers = {"Content-Type": "application/json"}

print("Testing WASM compilation...")

try:
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    
    if result["success"]:
        print("✅ WASM compilation successful")
        wasm_base64 = result["wasm"]
        wasm_bytes = base64.b64decode(wasm_base64)
        
        print(f"\nWASM size: {len(wasm_bytes)} bytes")
        print(f"WASM hex (first 64 bytes): {wasm_bytes[:64].hex()}")
        
        # 检查魔法字节
        if wasm_bytes[:4] != b'\x00asm':
            print("❌ Invalid WASM magic bytes")
            exit(1)
        print("✅ WASM magic bytes OK")
        
        # 解析 WASM 结构
        offset = 8  # 跳过魔法字节和版本
        
        while offset < len(wasm_bytes):
            if offset + 1 > len(wasm_bytes):
                print(f"❌ Unexpected end at offset {offset}")
                break
                
            section_id = wasm_bytes[offset]
            offset += 1
            
            if section_id == 0:
                break
                
            # 读取长度（varuint7）
            size = 0
            shift = 0
            while offset < len(wasm_bytes):
                byte = wasm_bytes[offset]
                offset += 1
                size |= (byte & 0x7f) << shift
                if not (byte & 0x80):
                    break
                shift += 7
                
            section_names = {
                1: 'Type', 2: 'Import', 3: 'Function', 5: 'Memory',
                6: 'Global', 7: 'Export', 9: 'Element', 10: 'Code', 11: 'Data'
            }
            name = section_names.get(section_id, f'Unknown({section_id})')
            
            print(f"\nSection {section_id} ({name}): {size} bytes")
            
            # 检查是否有足够的数据
            if offset + size > len(wasm_bytes):
                print(f"❌ ERROR: Section {name} needs {size} bytes but only {len(wasm_bytes) - offset} available!")
                print(f"   Offset: {offset}, WASM length: {len(wasm_bytes)}")
                break
                
            offset += size
        
        print("\n✅ WASM structure validation completed")
        
    else:
        print(f"❌ WASM compilation failed: {result['error']}")
        
except Exception as e:
    print(f"❌ Error: {e}")