from lexer import Lexer

lexer = Lexer()
keywords = lexer.keywords

# 检查包含 '列' 的关键字
列_keywords = [kw for kw in keywords if '列' in kw]
print('包含"列"的关键字:')
for kw in sorted(列_keywords, key=len, reverse=True):
    print(f'  {kw}')

# 检查是否包含 '列表'
print(f'\n是否包含"列表": {"列表" in keywords}')
