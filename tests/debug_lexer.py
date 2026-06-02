#!/usr/bin/env python3
# 调试词法分析器问题
import sys
sys.path.insert(0, 'yan')

from yan.lexer import Lexer

with open('yan/examples/basic.yan', 'r', encoding='utf-8') as f:
    source = f.read()

print("源代码（第38-49行）：")
lines = source.splitlines()
for i, line in enumerate(lines[37:49], start=38):
    print(f"{i}: {repr(line)}")

print("\n开始词法分析...")
try:
    lexer = Lexer()
    tokens = list(lexer.tokenize(source))
    print(f"\n成功生成 {len(tokens)} 个 token")
    # 打印前50个 token
    for tok in tokens[:50]:
        print(f"  {tok}")
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()