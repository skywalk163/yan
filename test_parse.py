from yan.lexer import Lexer, TokenType
from yan.parser import Parser
from yan.lexer import TokenType as LexerTokenType

code = """定 绝对 = 函 x：
  当 x 小于 0：
    返回 负 x
  返回 x
"""

lexer = Lexer()
tokens = lexer.tokenize(code)
parser = Parser(syntax_version=2)

parser.tokens = tokens
parser.pos = 0
parser.user_verbs = set()
parser.indent_stack = [0]  # 初始化 indent_stack
parser._reset_verbs_cache()
parser._collect_user_verbs()
parser._reset_verbs_cache()
parser.pos = 0

# 检查第一个 token
token = parser._current()
print("First token:", token.type, repr(token.value))
print("TokenType.WORD:", TokenType.WORD)
print("token.type == TokenType.WORD:", token.type == TokenType.WORD)

# 检查 _current() 返回的值
current_token = parser._current()
print("current_token:", current_token.type, repr(current_token.value))
print("current_token == token:", current_token == token)
print("current_token.value:", repr(current_token.value))
print("current_token.value == '定':", current_token.value == '定')

# 检查 _check_word
print("_check_word('定'):", parser._check_word('定'))

# 检查 parser 使用的 TokenType
from yan.parser import TokenType as ParserTokenType
print("测试文件 TokenType.WORD:", TokenType.WORD)
print("parser 模块 TokenType.WORD:", ParserTokenType.WORD)
print("两个 TokenType 是否相同:", TokenType.WORD is ParserTokenType.WORD)
print("parser 中的 TokenType:", type(parser).__module__, type(parser))
# 检查 _check_word 内部的值
ct = parser._current()
print("parser._current().type:", ct.type)
print("parser._current().type == TokenType.WORD:", ct.type == TokenType.WORD)
print("parser._current().type is TokenType.WORD:", ct.type is TokenType.WORD)
print("token.type.value:", token.type.value)
print("token.value == '定':", token.value == '定')

# 尝试解析
try:
    ast = parser.parse_v2(tokens)
    print("Parse successful!")
    print("AST:", ast)
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
