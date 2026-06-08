#!/usr/bin/env python3
"""将所有英文冒号替换为中文冒号"""

# 读取文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 统计替换次数
count = content.count(':')

# 替换
content = content.replace(':', '：')

# 保存文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ 已将 {count} 个英文冒号替换为中文冒号")
