import subprocess
import sys

# 运行 idiom_game.yan 并提供输入
proc = subprocess.Popen(
    [sys.executable, 'main.py', 'examples/idiom_game.yan'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    cwd='g:\\dumategithub\\newlisp\\yan',
    text=True,
    encoding='utf-8'
)

# 提供输入序列
inputs = "一心一意\n帮\n退出\n"
output, _ = proc.communicate(input=inputs)

print(output)
