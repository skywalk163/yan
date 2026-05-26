#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
言语言代码格式化工具
使用方法:
    python yan_fmt.py <输入文件> [输出文件]
    python yan_fmt.py --inplace <文件>
"""
import argparse
import sys
import os


class YanFormatter:
    def __init__(self, indent_size=2, max_line_length=80):
        self.indent_size = indent_size
        self.max_line_length = max_line_length

    def format_file(self, input_path, output_path=None):
        """格式化文件"""
        with open(input_path, 'r', encoding='utf-8') as f:
            code = f.read()

        formatted = self.format_code(code)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted)
            print(f"已格式化: {input_path} -> {output_path}")
        else:
            return formatted

    def format_code(self, code):
        """格式化代码"""
        lines = code.split('\n')
        formatted_lines = []
        current_indent = 0

        for line in lines:
            trimmed = line.strip()

            if not trimmed:
                formatted_lines.append('')
                continue

            # 处理缩进调整
            new_indent = self._calculate_indent(trimmed, current_indent)
            
            # 应用缩进
            indent = ' ' * (new_indent * self.indent_size)
            formatted_lines.append(indent + trimmed)

            current_indent = new_indent

        return '\n'.join(formatted_lines)

    def _calculate_indent(self, trimmed_line, current_indent):
        """计算缩进级别"""
        # 块开始关键字（增加缩进）
        block_start_keywords = ['函数', '如果', '遍历', '当满足', '结构', '套', '测', '导入']
        # 块中间关键字（保持当前缩进）
        block_middle_keywords = ['那么', '否则']
        # 块结束（减少缩进）
        block_end_keywords = ['。']

        # 检查是否应该减少缩进
        should_decrease = False
        for keyword in block_end_keywords:
            if trimmed_line == keyword:
                should_decrease = True
                break

        # 先减少缩进（如果需要）
        indent = max(0, current_indent - (1 if should_decrease else 0))

        # 检查是否应该增加缩进
        should_increase = False
        for keyword in block_start_keywords:
            if trimmed_line.startswith(keyword):
                should_increase = True
                break

        # 检查中间关键字（保持当前）
        for keyword in block_middle_keywords:
            if trimmed_line.startswith(keyword):
                return current_indent

        if should_increase:
            return indent + 1

        return indent


def main():
    parser = argparse.ArgumentParser(description='言语言代码格式化工具')
    parser.add_argument('input_file', help='输入文件路径')
    parser.add_argument('output_file', nargs='?', help='输出文件路径')
    parser.add_argument('--inplace', '-i', action='store_true', help='原地修改文件')
    parser.add_argument('--indent-size', type=int, default=2, help='缩进大小')
    parser.add_argument('--max-line', type=int, default=80, help='最大行长度')

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"错误: 文件不存在: {args.input_file}")
        return 1

    formatter = YanFormatter(
        indent_size=args.indent_size,
        max_line_length=args.max_line
    )

    if args.inplace:
        formatter.format_file(args.input_file, args.input_file)
    else:
        output_path = args.output_file if args.output_file else None
        if output_path:
            formatter.format_file(args.input_file, output_path)
        else:
            formatted = formatter.format_file(args.input_file)
            print(formatted)

    return 0


if __name__ == '__main__':
    sys.exit(main())
