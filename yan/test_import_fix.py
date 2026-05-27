#!/usr/bin/env python3
"""检查修复后的 Import Section"""

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

# 计算正确的 import entry 大小
# import 0: 07 65 6e 76 05 70 72 69 6e 74 00 00 = 12 bytes
# import 1: 07 65 6e 76 08 70 72 69 6e 74 5f 6e 75 6d 00 01 = 16 bytes
# import 2: 07 65 6e 76 0a 70 72 69 6e 74 5f 66 6c 6f 61 74 00 02 = 18 bytes
# total = 12 + 16 + 18 = 46 bytes
# + 1 byte for count = 47 bytes

print("\n预期:")
print("  import 0: 12 bytes (module 'env' + field 'print' + kind=0 + type=0)")
print("  import 1: 16 bytes (module 'env' + field 'print_num' + kind=0 + type=1)")
print("  import 2: 18 bytes (module 'env' + field 'print_float' + kind=0 + type=2)")
print("  total: 46 bytes + 1 byte count = 47 bytes")

# 检查实际 hex
expected_hex = '0307656e760570696e74000007656e76087072696e745f6e756d000107656e760a7072696e745f666c6f61740002'
print(f"\nExpected hex: {expected_hex}")
print(f"Actual hex:   {imports.hex()}")
print(f"Match: {imports.hex() == expected_hex}")