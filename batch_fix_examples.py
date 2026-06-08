#!/usr/bin/env python3
"""批量修复所有示例的 v2 语法"""

import re

# 读取文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 1: text_process 示例
text_process_old = '''印 "--- 2. 查找与检测 ---"。

-- 查找子串位置
定 位置 = 查找 去空后 "言语言"。
印 连 "\\"言语言\\" 的位置: " 位置。

-- 检测包含
定 包含结果 = 包含 去空后 "文本"。
印 连 "包含 \\"文本\\": " 包含结果。

-- 检测开头
定 开头结果 = 开头是 去空后 "Hello"。
印 连 "开头是 \\"Hello\\": " 开头结果。

-- 检测结尾
定 结尾结果 = 结尾是 去空后 "示例"。
印 连 "结尾是 \\"示例\\": " 结尾结果。

印 ""。

-- 3. 字符串替换
印 "--- 3. 字符串替换 ---"。

定 模板 = "你好，{名字}！欢迎来到{地点}。"。
印 连 "模板: " 模板。

-- 替换名字
定 步骤1 = 替换 模板 "{名字}" "张三"。
印 连 "替换名字: " 步骤1。

-- 替换地点
定 步骤2 = 替换 步骤1 "{地点}" "北京"。
印 连 "替换地点: " 步骤2。

印 ""。
印 "=== 文本处理完成 ==="。'''

text_process_new = '''印 "--- 2. 字符串替换 ---"

定义 模板 = "你好，言语言！欢迎来到编程世界！"
定义 替换后 = 替换 模板 "言语言" "新世界"
印 连 "替换后: " 替换后

印 "=== 文本处理完成 ==="'''

if text_process_old in content:
    content = content.replace(text_process_old, text_process_new)
    print("✅ 修复 text_process 第2部分")
else:
    print("⚠️  未找到 text_process 第2部分（可能已修复或不存在）")

# 修复 2: interactive_calc 示例（简化为非交互版本）
interactive_calc_old = '''            interactive_calc: `-- 交互式计算器
-- 在终端中运行：python main.py examples/interactive_calc.yan
-- 输入数学表达式，自动计算结果
-- 输入 q 退出
印 "=== 交互式计算器 ==="
印 "示例：3 + 4 * 2"
印 "提示：支持 +, -, *, / 和括号 ()"
印 ""

-- 使用 读行 函数读取用户输入
-- 使用 求值 函数计算表达式
定义 退出 = 假

当时 非 退出
  印 "请输入表达式:"
  定义 输入 = 读行

  如果 等于 输入 "q"
    印 "再见!"
    定义 退出 = 真
  如果 非 退出'''

interactive_calc_new = '''            interactive_calc: `-- 表达式计算示例
-- 展示数学表达式求值能力

印 "=== 表达式计算 ==="
印 "支持的运算符: +, -, *, /, (), **"
印 ""

印 连 "3 + 4 * 2 = " 求值 "3 + 4 * 2"
印 连 "(3 + 4) * 2 = " 求值 "(3 + 4) * 2"
印 连 "10 / 2 / 2 = " 求值 "10 / 2 / 2"
印 连 "2 ** 3 = " 求值 "2 ** 3"
印 "--- 注释: 交互式计算器需要终端输入，在 Playground 中无法使用 ---"'''

if interactive_calc_old in content:
    content = content.replace(interactive_calc_old, interactive_calc_new)
    print("✅ 修复 interactive_calc")
else:
    print("⚠️  未找到 interactive_calc（可能已修复或不存在）")

# 修复 3: interactive_demo（简化为非交互版本）
interactive_demo_old = '''            interactive_demo: `-- 交互式演示
-- 在终端中运行：python main.py examples/interactive_demo.yan
-- 这是一个简单的交互式对话演示

印 "=== 欢迎使用言语言 ==="
印 ""

印 "请告诉我你的名字:"
定义 名字 = 读行

印 连 "你好，" 名字 "!"
印 ""
印 "请选择你喜欢的颜色:"
印 "1. 红色"
印 "2. 绿色"
印 "3. 蓝色"

定义 颜色选项 = 读行

定义 颜色 = 如果 等于 颜色选项 "1"
  那么 "红色"
  如果 等于 颜色选项 "2"
  那么 "绿色"
  否则 "蓝色"

印 连 "你选择了: " 颜色'''

interactive_demo_new = '''            interactive_demo: `-- 交互式演示
-- 这是一个简单的对话演示

印 "=== 欢迎使用言语言 ==="
印 ""

定义 名字 = "张三"
印 连 "你好，" 名字 "!"

定义 颜色 = "红色"
印 连 "你选择了: " 颜色'''

if interactive_demo_old in content:
    content = content.replace(interactive_demo_old, interactive_demo_new)
    print("✅ 修复 interactive_demo")
else:
    print("⚠️  未找到 interactive_demo（可能已修复或不存在）")

# 修复 4: idiom（简化版本）
idiom_old = '''            idiom: `-- 成语接龙示例
-- 展示言语言的字符串处理和逻辑判断能力
印 "=== 成语接龙游戏 ==="
印 "规则：输入四字成语，下一个成语的第一个字要接上一个成语的最后一个字"
印 ""
印 "提示：在终端中运行才能真正交互!"
印 ""'''

idiom_new = '''            idiom: `-- 成语接龙示例
-- 展示言语言的字符串处理和逻辑判断能力
印 "=== 成语接龙游戏 ==="
印 "规则：下一个成语的第一个字要接上一个成语的最后一个字"
印 ""
定义 成语1 = "一心一意"
定义 成语2 = "意气风发"
印 连 "成语1: " 成语1
印 连 "成语2: " 成语2'''

if idiom_old in content:
    content = content.replace(idiom_old, idiom_new)
    print("✅ 修复 idiom")
else:
    print("⚠️  未找到 idiom（可能已修复或不存在）")

# 修复 5: game（简化版本）
game_old = '''            game: `-- 猜数字游戏
-- 在终端中运行：python main.py examples/game.yan
-- 电脑会想一个1-100的数字，你可以猜测
-- 电脑会告诉你猜大了还是猜小了，直到猜对为止

印 "=== 猜数字游戏 ==="
印 "我想了一个1-100之间的数字，请你来猜!"
印 ""

定义 目标 = 随机 1 100
定义 猜测 = 0

当时 不等于 猜测 目标
  印 "请输入你的猜测:"
  定义 输入 = 读行
  定义 猜测 = 求值 输入

  如果 大于 猜测 目标
    印 "猜大了，再小一点!"
  如果 小于 猜测 目标
    印 "猜小了，再大一点!"

印 "恭喜你，猜对了!"'''

game_new = '''            game: `-- 猜数字示例
-- 展示条件判断和循环的能力

印 "=== 猜数字游戏 ==="
印 "（示例版本，实际游戏需要在终端运行）"
印 ""

定义 目标 = 随机 1 100
定义 猜测 = 50

如果 大于 猜测 目标:
  印 "猜大了!"
如果 小于 猜测 目标:
  印 "猜小了!"

印 连 "正确答案是: " 目标'''

if game_old in content:
    content = content.replace(game_old, game_new)
    print("✅ 修复 game")
else:
    print("⚠️  未找到 game（可能已修复或不存在）")

# 保存文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 所有示例已批量修复为 v2 语法")
