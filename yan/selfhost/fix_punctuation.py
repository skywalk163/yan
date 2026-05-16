"""
修复全角句号问题
将 "．" 替换为 "。"
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILES = [
    'ast.yan',
    'codegen.yan', 
    'compiler.yan',
    'lexer.yan',
    'parser.yan',
]

for filename in FILES:
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '．' in content:
        print(f'修复: {filename}')
        new_content = content.replace('．', '。')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f'  ✓ 已替换全角句号')

print('完成！')
