#!/usr/bin/env python3
"""完整修复所有示例的 v2 语法"""

import re

# 读取文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("开始修复...")

# 1. 修复 data_process
if 'data_process:' in content:
    old = '''            data_process: `-- 数据处理示例
-- 展示言语言的列表处理能力
印 "=== 列表数据处理 ==="

-- 创建数字列表
定 数字 = 列 85 72 91 68 95 55 78 63
印 "原始数字："
印 数字

-- 计算总和
定 总和 = 0
定 i = 0
当 小 i 长 数字：
  定 当前 = 取 数字 i
  定 总和 = 加 总和 当前
  定 i = 加 i 1

印 连 "总和: " 总和

-- 计算平均
定 平均 = 除 总和 长 数字
印 连 "平均: " 平均

-- 找出最大值
定 最大 = 0
定 i = 0
当 小 i 长 数字：
  定 当前 = 取 数字 i
  若 大 当前 最大：
    定 最大 = 当前

  定 i = 加 i 1

印 连 "最大值: " 最大

-- 字符串操作
印 "=== 字符串处理 ==="
定 名字 = "言语言"
印 连 "你好，" 名字 "！"'''

    new = '''            data_process: `-- 数据处理示例
-- 展示言语言的列表处理能力

印 "=== 列表数据处理 ==="

-- 创建数字列表
定义 数字 = 列表 85 72 91 68 95 55 78 63
印 "原始数字："
印 数字

-- 计算总和
定义 总和 = 0
定义 i = 0
当时 小于 i 长度 数字:
  定义 当前 = 取 数字 i
  定义 总和 = 加 总和 当前
  定义 i = 加 i 1

印 连 "总和: " 总和

-- 计算平均
定义 平均 = 除 总和 长度 数字
印 连 "平均: " 平均

-- 找出最大值
定义 最大 = 0
定义 i = 0
当时 小于 i 长度 数字:
  定义 当前 = 取 数字 i
  如果 大于 当前 最大:
    定义 最大 = 当前
  定义 i = 加 i 1

印 连 "最大值: " 最大'''

    if old in content:
        content = content.replace(old, new)
        print("✅ 修复 data_process")

# 2. 修复 text_process
if 'text_process:' in content:
    # 找到整个 text_process 示例并替换
    start = content.find('text_process:')
    if start != -1:
        end = content.find('`,\n\n            interactive_calc:', start)
        if end != -1:
            end += 3  # 包含结束的反引号和逗号
        
        new_text_process = ''''''            text_process: `-- 文本处理示例
-- 展示言语言的字符串操作能力

印 "=== 文本处理示例 ==="
印 ""

-- 1. 基本字符串操作
印 "--- 1. 基本字符串操作 ---"

定义 文本 = "Hello, 言语言!"
印 连 "原始文本: " 文本

-- 字符串长度
定义 长度值 = 长度 文本
印 连 "长度: " 长度值

-- 转换大小写
定义 小写文本 = 小写 文本
印 连 "小写: " 小写文本

定义 大写文本 = 大写 文本
印 连 "大写: " 大写文本

-- 2. 字符串替换
印 "--- 2. 字符串替换 ---"

定义 模板 = "你好，言语言！欢迎来到编程世界！"
定义 替换后 = 替换 模板 "言语言" "新世界"
印 连 "替换后: " 替换后'''

            content = content[:start] + new_text_process + content[end:]
            print("✅ 修复 text_process")

# 3. 修复 interactive_calc
if 'interactive_calc:' in content:
    start = content.find('interactive_calc:')
    if start != -1:
        end = content.find('`,\n\n            interactive_demo:', start)
        if end != -1:
            end += 3
        
        new_interactive_calc = '''            interactive_calc: `-- 表达式计算示例
-- 展示数学表达式求值能力

印 "=== 表达式计算 ==="
印 "支持的运算符: +, -, *, /, (), **"
印 ""

印 连 "3 + 4 * 2 = " 求值 "3 + 4 * 2"
印 连 "(3 + 4) * 2 = " 求值 "(3 + 4) * 2"
印 连 "10 / 2 / 2 = " 求值 "10 / 2 / 2"
印 连 "2 ** 3 = " 求值 "2 ** 3"'''

            content = content[:start] + new_interactive_calc + content[end:]
            print("✅ 修复 interactive_calc")

# 4. 修复 interactive_demo
if 'interactive_demo:' in content:
    start = content.find('interactive_demo:')
    if start != -1:
        end = content.find('`,\n\n            bubble:', start)
        if end != -1:
            end += 3
        
        new_interactive_demo = '''            interactive_demo: `-- 交互式程序示例
-- 展示言语言的输入输出功能

印 "=== 交互式程序 ==="
印 ""
印 "欢迎使用言语言交互式示例！"
印 ""

-- 1. 简单的输入输出
印 "--- 1. 简单输入输出 ---"
定义 名字 = "示例用户"
印 连 "你好，" 名字 "！很高兴认识你！"
印 ""

-- 2. 数字计算
印 "--- 2. 数字计算 ---"
定义 数1 = 10
定义 数2 = 5
定义 和 = 加 数1 数2
印 连 数1 " + " 数2 " = " 和
印 ""'''

            content = content[:start] + new_interactive_demo + content[end:]
            print("✅ 修复 interactive_demo")

# 5. 修复 idiom
if 'idiom:' in content:
    start = content.find('idiom:')
    if start != -1:
        end = content.find('`,\n\n            quick_sort:', start)
        if end != -1:
            end += 3
        
        new_idiom = '''            idiom: `-- 成语接龙示例
-- 展示言语言的字符串处理能力

印 "=== 成语接龙游戏 ==="
印 "规则：下一个成语的第一个字要接上一个成语的最后一个字"
印 ""

定义 成语1 = "一心一意"
定义 成语2 = "意气风发"
印 连 "成语1: " 成语1
印 连 "成语2: " 成语2

-- 取出最后一个字
定义 尾字 = 取 成语1 减 长度 成语1 1
印 连 "成语1的尾字: " 尾字

-- 取出第一个字
定义 首字 = 取 成语2 0
印 连 "成语2的首字: " 首字'''

            content = content[:start] + new_idiom + content[end:]
            print("✅ 修复 idiom")

# 6. 修复 bubble
if 'bubble:' in content:
    start = content.find('bubble:')
    if start != -1:
        end = content.find('`,\n\n            idiom:', start)
        if end != -1:
            end += 3
        
        new_bubble = '''            bubble: `-- 冒泡排序
定义 冒泡排序 = 函数 arr:
  定义 n = 长度 arr
  遍历 i 于 范围 n:
    定义 已交换 = 假
    定义 j = 0
    当时 小于 j 减 n 加 i 1:
      定义 当前 = 取 arr j
      定义 下一个 = 取 arr 加 j 1
      如果 大于 当前 下一个:
        定义 tmp = 当前
        定义 arr = 设 arr j 下一个
        定义 arr = 设 arr 加 j 1 tmp
        定义 已交换 = 真
      定义 j = 加 j 1
    如果 不 已交换:
      返回 arr
  返回 arr

定义 原始 = 列表 64 34 25 12 22 11 90
印 连 "原始数组: " 原始
定义 排序后 = 冒泡排序 原始
印 连 "排序后: " 排序后'''

            content = content[:start] + new_bubble + content[end:]
            print("✅ 修复 bubble")

# 保存文件
with open(r'G:\dumategithub\newlisp\yan\playground\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 所有示例已修复并保存")
