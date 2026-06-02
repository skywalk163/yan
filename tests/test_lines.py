import sys
sys.path.insert(0, 'yan')
from yan.lexer import Lexer

# Test each line individually
lines = [
    '印10加5。',
    '印10减5。',
    '印10乘5。',
    '印10除5。',
]

for line in lines:
    lexer = Lexer()
    tokens = list(lexer.tokenize(line))
    print(f'{repr(line)}:')
    for i, tok in enumerate(tokens):
        print(f'  {i}: {tok.type.name} = {repr(tok.value)}')
    print()
