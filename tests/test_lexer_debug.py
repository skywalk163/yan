import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer

# Test the problematic line
source = '印10减5。'
lexer = Lexer()
tokens = list(lexer.tokenize(source))
print('Tokens for "印10减5。":')
for i, tok in enumerate(tokens):
    print(f'{i}: {tok.type.name} = {repr(tok.value)}')

# Test the whole file
print('\n\n--- First 10 tokens of the file ---')
with open('yan/examples/basic.yan', 'r', encoding='utf-8') as f:
    content = f.read()

lexer2 = Lexer()
tokens2 = list(lexer2.tokenize(content))
print('Tokens:')
for i, tok in enumerate(tokens2[:20]):
    print(f'{i}: {tok.type.name} = {repr(tok.value)}')
