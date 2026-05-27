#!/usr/bin/env python3
"""测试 WASM Type Section 编码"""

import sys
sys.path.insert(0, '.')
from codegen_wasm import WASMCodeGen, WASMBuilder

# 创建一个简单的测试 AST 节点
class MockNode:
    def __init__(self):
        self.statements = []

class MockExpr:
    def __init__(self, value):
        self.value = value

class MockFunc:
    def __init__(self, params):
        self.params = params

# 测试代码生成器
codegen = WASMCodeGen()
codegen.functions = [('move', MockFunc(['d', 'from', 'to']))]
codegen.global_vars = {}
codegen.next_global_index = 0

# 生成 types
types_bytes = codegen._gen_types()
print("Type Section bytes (hex):", types_bytes.hex())
print("Type Section length:", len(types_bytes))

# 解析
print("\n解析:")
i = 0
if i < len(types_bytes):
    type_count = 0
    shift = 0
    while i < len(types_bytes):
        b = types_bytes[i]
        type_count |= (b & 0x7f) << shift
        i += 1
        if (b & 0x80) == 0:
            break
        shift += 7
    print(f"Type count: {type_count}")

j = 0
for t in range(type_count):
    print(f"\nType {t}:")
    if j >= len(types_bytes):
        break
    print(f"  Byte {j}: 0x{types_bytes[j]:02x} (type_form)", end="")
    if types_bytes[j] == 0x60:
        print(" (function)")
    else:
        print(" (INVALID!)")
        break
    j += 1

    # param_count
    if j >= len(types_bytes):
        break
    param_count = 0
    shift = 0
    while j < len(types_bytes):
        b = types_bytes[j]
        param_count |= (b & 0x7f) << shift
        j += 1
        if (b & 0x80) == 0:
            break
        shift += 7
    print(f"  Byte {j}: param_count = {param_count}")
    j += 1

    # param_types
    for p in range(param_count):
        if j >= len(types_bytes):
            break
        print(f"  Byte {j}: param_type = 0x{types_bytes[j]:02x}")
        j += 1

    # return_count
    if j >= len(types_bytes):
        break
    return_count = 0
    shift = 0
    while j < len(types_bytes):
        b = types_bytes[j]
        return_count |= (b & 0x7f) << shift
        j += 1
        if (b & 0x80) == 0:
            break
        shift += 7
    print(f"  Byte {j}: return_count = {return_count}")
    j += 1

    # return_types
    for r in range(return_count):
        if j >= len(types_bytes):
            break
        print(f"  Byte {j}: return_type = 0x{types_bytes[j]:02x}")
        j += 1