import subprocess
import sys

# 测试输入
test_inputs = ["一心一意", "意气风发", "发愤图强", "退出"]

# 创建子进程
proc = subprocess.Popen(
    [sys.executable, "main.py", "examples/idiom_game.yan"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    cwd="."
)

# 逐行发送输入
for user_input in test_inputs:
    print(f"发送: {user_input}")
    proc.stdin.write(user_input + "\n")
    proc.stdin.flush()

# 关闭输入
proc.stdin.close()

# 读取输出
output = proc.stdout.read()
print(output)

proc.wait()
