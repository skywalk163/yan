import sys
sys.path.insert(0, '.')

# 创建一个简单的测试界面
from parser import Parser
from lexer import Lexer
from codegen import PythonCodeGen
import runtime

# 读取游戏代码
with open('examples/idiom_game.yan', 'r', encoding='utf-8') as f:
    game_source = f.read()

# 解析和编译
lexer = Lexer()
tokens = lexer.tokenize(game_source)
parser = Parser()
ast = parser.parse(tokens)

# 生成代码
gen = PythonCodeGen()
code = gen.generate(ast)

# 设置内置函数
setup_builtins()

# 替换 input 函数
import builtins
original_input = builtins.input

# 测试输入
test_inputs = iter([
    "一心一意",
    "意气风发",
    "发愤图强",
    "退出"
])

def mock_input(prompt=""):
    try:
        user_input = next(test_inputs)
        print(user_input)  # 打印输入
        return user_input
    except StopIteration:
        raise EOFError()

builtins.input = mock_input

# 执行代码
exec(code, {'__name__': '__main__'})

print("\n测试完成！")
