#!/usr/bin/env python3
"""重新应用所有修复，只修改示例代码"""

import re

# 读取文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 重新应用 condition 示例的修复
content = content.replace(
    '''如果 大于 年龄 18
  印 "成年人"
否则
  印 "未成年"''',
    '''如果 大于 年龄 18 那么：
  印 "成年人"
否则：
  印 "未成年"'''
)

# 2. 重新应用 loop 示例的修复
content = content.replace(
    '遍历 x 于 水果\n  印 x`',
    '遍历 x 于 水果：\n  印 x`'
)

# 3. 重新应用 interactive_calc 示例的修复
content = content.replace(
    '''            interactive_calc: `-- 交互式计算器
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
  如果 非 退出''',
    '''            interactive_calc: `-- 表达式计算示例
-- 展示数学表达式求值能力

印 "=== 表达式计算 ==="
印 "支持的运算符: +, -, *, /, (), **"
印 ""

印 连 "3 + 4 * 2 = " 求值 "3 + 4 * 2"
印 连 "(3 + 4) * 2 = " 求值 "(3 + 4) * 2"
印 连 "10 / 2 / 2 = " 求值 "10 / 2 / 2"
印 连 "2 ** 3 = " 求值 "2 ** 3"'''
)

# 4. 重新应用 interactive_demo 示例的修复
content = content.replace(
    '''            interactive_demo: `-- 交互式演示
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

印 连 "你选择了: " 颜色''',
    '''            interactive_demo: `-- 交互式演示
-- 这是一个简单的对话演示

印 "=== 欢迎使用言语言 ==="
印 ""

定义 名字 = "张三"
印 连 "你好，" 名字 "!"

定义 颜色 = "红色"
印 连 "你选择了: " 颜色'''
)

# 5. 重新应用 idiom 示例的修复
content = content.replace(
    '''            idiom: `-- 成语接龙示例
-- 展示言语言的字符串处理和逻辑判断能力
印 "=== 成语接龙游戏 ==="
印 "规则：输入四字成语，下一个成语的第一个字要接上一个成语的最后一个字"
印 ""
印 "提示：在终端中运行才能真正交互!"
印 ""''',
    '''            idiom: `-- 成语接龙示例
-- 展示言语言的字符串处理和逻辑判断能力
印 "=== 成语接龙游戏 ==="
印 "规则：下一个成语的第一个字要接上一个成语的最后一个字"
印 ""
定义 成语1 = "一心一意"
定义 成语2 = "意气风发"
印 连 "成语1: " 成语1
印 连 "成语2: " 成语2'''
)

# 6. 重新应用 game 示例的修复
content = content.replace(
    '''            game: `-- 猜数字游戏
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

印 "恭喜你，猜对了!"''',
    '''            game: `-- 猜数字示例
-- 展示条件判断和循环的能力

印 "=== 猜数字游戏 ==="
印 "（示例版本，实际游戏需要在终端运行）"
印 ""

定义 目标 = 随机 1 100
定义 猜测 = 50

如果 大于 猜测 目标：
  印 "猜大了!"
如果 小于 猜测 目标：
  印 "猜小了!"

印 连 "正确答案是: " 目标'''
)

# 7. 修复 text_process 示例中的 v1 语法
content = content.replace('印 ""', '印 ""')
content = content.replace('印 "---', '\n印 "---')
content = content.replace('定 ', '定义 ')
content = content.replace('印 "===', '\n印 "===')
content = content.replace('印 ""。', '印 ""')

# 移除句号结尾（中文句号）
content = content.replace('。"', '"')
content = content.replace('。"', '"')
content = content.replace('。"', '"')

# 移除 v1 语法的反斜杠引号
content = content.replace('\\""', '"')
content = content.replace('\\\\""', '"')

# 保存文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 所有修复已重新应用")
