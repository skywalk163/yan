#!/usr/bin/env python3
"""检查 Import Section 生成"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from codegen_wasm import WASMCodeGen

codegen = WASMCodeGen()

# 模拟有用户函数的情况
class MockFunc:
    def __init__(self, params):
        self.params = params

codegen.functions = [('move', MockFunc(['n', 'from', 'to', 'aux']))]

imports = codegen._gen_imports()
print(f"Import Section ({len(imports)} bytes): {imports.hex()}")

# 解析 Import Section
print("\n解析:")
i = 0
import_count = 0
shift = 0
while i < len(imports):
    b = imports[i]
    import_count |= (b & 0x7f) << shift
    i += 1
    if (b & 0x80) == 0:
        break
    shift += 7
print(f"Import count: {import_count}")

for idx in range(import_count):
    print(f"\nImport {idx}:")
    entry_start = i

    # module_len
    module_len = 0
    shift = 0
    while i < len(imports):
        b = imports[i]
        module_len |= (b & 0x7f) << shift
        i += 1
        if (b & 0x80) == 0:
            break
        shift += 7
    print(f"  module_len: {module_len}")

    # module_name
    module_name = imports[i:i+module_len].decode('utf-8', errors='replace')
    print(f"  module_name: '{module_name}'")
    i += module_len

    # field_len
    field_len = 0
    shift = 0
    while i < len(imports):
        b = imports[i]
        field_len |= (b & 0x7f) << shift
        i += 1
        if (b & 0x80) == 0:
            break
        shift += 7
    print(f"  field_len: {field_len}")

    # field_name
    field_name = imports[i:i+field_len].decode('utf-8', errors='replace')
    print(f"  field_name: '{field_name}'")
    i += field_len

    # import_kind
    if i < len(imports):
        import_kind = imports[i]
        print(f"  import_kind: {import_kind}")
        i += 1

    # type_idx
    if i < len(imports):
        type_idx = 0
        shift = 0
        while i < len(imports):
            b = imports[i]
            type_idx |= (b & 0x7f) << shift
            i += 1
            if (b & 0x80) == 0:
                break
            shift += 7
        print(f"  type_idx: {type_idx}")

    entry_end = i
    print(f"  Entry size: {entry_end - entry_start} bytes")
    print(f"  Entry hex: {imports[entry_start:entry_end].hex()}")

print(f"\nTotal bytes used: {i} / {len(imports)}")
print(f"Difference: {len(imports) - i} bytes")