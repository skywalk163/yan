#!/usr/bin/env python3
"""
言语言代码格式化工具
"""

import sys
import re
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FormatOptions:
    indent_size: int = 4
    max_line_length: int = 120
    spaces_before_comment: int = 1
    align_assignments: bool = False


class YanFormatter:
    """言语言代码格式化器"""

    def __init__(self, options: FormatOptions = None):
        self.options = options or FormatOptions()
        self.indent_level = 0

    def format(self, source: str) -> str:
        """格式化代码"""
        lines = source.split('\n')
        result = []
        self.indent_level = 0

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped or stripped.startswith('--'):
                result.append(line)
                i += 1
                continue

            if stripped.startswith('套'):
                result.append(self._indent() + stripped)
                self.indent_level += 1
                i += 1
                continue

            if stripped.startswith('测'):
                result.append(self._indent() + stripped)
                i += 1
                continue

            if stripped == '。':
                dedent = False
                if result and result[-1].strip().startswith('测'):
                    dedent = True

                if result and result[-1].strip() == '。':
                    result.append(self._indent() + stripped)
                elif result and not result[-1].strip().endswith('。'):
                    result.append(self._indent() + stripped)
                else:
                    result.append(self._indent() + stripped)

                if dedent and self.indent_level > 1:
                    self.indent_level -= 1
                i += 1
                continue

            if stripped.startswith('若') or stripped.startswith('当'):
                if '则' in stripped or stripped.endswith(':'):
                    result.append(self._indent() + stripped)
                    self.indent_level += 1
                else:
                    result.append(self._indent() + stripped)
                i += 1
                continue

            if stripped.startswith('遍历') or stripped.startswith('函'):
                result.append(self._indent() + stripped)
                self.indent_level += 1
                i += 1
                continue

            if stripped == '则':
                self.indent_level = max(0, self.indent_level - 1)
                result.append(self._indent() + stripped)
                self.indent_level += 1
                i += 1
                continue

            formatted = self._format_line(stripped)
            result.append(self._indent() + formatted)
            i += 1

        return '\n'.join(result)

    def _indent(self) -> str:
        """生成缩进"""
        return ' ' * self.indent_level * self.options.indent_size

    def _format_line(self, line: str) -> str:
        """格式化单行代码"""
        line = line.strip()

        line = re.sub(r'\s+', ' ', line)

        line = re.sub(r'\s*([，。；：])\s*', r'\1', line)

        line = re.sub(r'\(\s+', '(', line)
        line = re.sub(r'\s+\)', ')', line)

        return line

    def format_file(self, file_path: str) -> bool:
        """格式化文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            formatted = self.format(source)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted)

            return True
        except Exception as e:
            print(f"格式化失败: {e}", file=sys.stderr)
            return False


class YanLinter:
    """言语言静态检查工具"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def lint(self, source: str) -> List[Tuple[str, int, int, str]]:
        """检查代码并返回问题列表"""
        issues = []
        lines = source.split('\n')

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            if not stripped or stripped.startswith('--'):
                continue

            issues.extend(self._check_syntax(line_num, line, stripped))
            issues.extend(self._check_style(line_num, line, stripped))
            issues.extend(self._check_potential_bugs(line_num, line, stripped))

        return issues

    def _check_syntax(self, line_num: int, line: str, stripped: str) -> List[Tuple[str, int, int, str]]:
        """检查语法问题"""
        issues = []

        if '"' in stripped:
            quote_count = stripped.count('"')
            if quote_count % 2 != 0:
                issues.append(('error', line_num, 0, '未闭合的字符串'))

        if '{{' in stripped:
            open_count = stripped.count('{{')
            close_count = stripped.count('}}')
            if open_count != close_count:
                issues.append(('error', line_num, 0, '未闭合的代码块'))

        if stripped.startswith('若'):
            if '则' not in stripped:
                issues.append(('error', line_num, 0, '条件语句缺少「则」'))

        if stripped.startswith('遍历'):
            if '于' not in stripped:
                issues.append(('error', line_num, 0, '遍历语句缺少「于」'))

        if stripped.startswith('定'):
            if '=' not in stripped and '。' not in stripped:
                issues.append(('error', line_num, 0, '变量定义缺少值'))

        return issues

    def _check_style(self, line_num: int, line: str, stripped: str) -> List[Tuple[str, int, int, str]]:
        """检查代码风格问题"""
        issues = []

        if stripped and not stripped.endswith('。') and not stripped.endswith('：'):
            if not any(stripped.startswith(k) for k in ['引', '出', '定', '函', '若', '遍历', '当', '套', '测', '则']):
                if '。' not in stripped:
                    pass

        if len(line) > 120:
            issues.append(('warning', line_num, 0, f'行长度超过120字符 ({len(line)}字符)'))

        if re.match(r'^\s+$', line):
            issues.append(('warning', line_num, 0, '只包含空白的行'))

        return issues

    def _check_potential_bugs(self, line_num: int, line: str, stripped: str) -> List[Tuple[str, int, int, str]]:
        """检查潜在bug"""
        issues = []

        undefined_pattern = r'(?<![引出定函])((?!引|出|定|函)\b\w+)\s+((?!引|出|定|函)\b\w+)\s*='
        for match in re.finditer(undefined_pattern, stripped):
            var_name = match.group(1)
            if var_name not in ['若', '则', '遍历', '于', '当', '套', '测']:
                pass

        if re.search(r'\b\w+\s*=\s*\w+\s*=\s*', stripped):
            issues.append(('warning', line_num, 0, '连续赋值，可能不是预期行为'))

        if re.search(r'除\s+0', stripped):
            issues.append(('error', line_num, 0, '除以零'))

        if re.search(r'长\s*$', stripped) or re.search(r'\b长\s+[^列]', stripped):
            issues.append(('warning', line_num, 0, '「长」函数期望列表参数'))

        return issues

    def lint_file(self, file_path: str) -> List[Tuple[str, int, int, str]]:
        """检查文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            return self.lint(source)
        except Exception as e:
            return [('error', 0, 0, f'无法读取文件: {e}')]

    def print_report(self, issues: List[Tuple[str, int, int, str]]):
        """打印检查报告"""
        if not issues:
            print("✅ 代码检查通过，没有发现问题")
            return

        error_count = sum(1 for i in issues if i[0] == 'error')
        warning_count = sum(1 for i in issues if i[0] == 'warning')

        print(f"📋 检查报告")
        print(f"   错误: {error_count}")
        print(f"   警告: {warning_count}")
        print()

        for level, line_num, col, message in issues:
            prefix = "❌" if level == 'error' else "⚠️"
            location = f"第 {line_num} 行" if line_num > 0 else "未知位置"
            print(f"   {prefix} {location}: {message}")


def main():
    """主函数"""
    args = sys.argv[1:]

    if not args:
        print("言语言代码工具")
        print("用法:")
        print("  python yan_fmt.py 格式化 <文件>")
        print("  python yan_fmt.py 检查 <文件>")
        return

    command = args[0]

    if command == "格式化" or command == "format":
        if len(args) < 2:
            print("错误: 请指定要格式化的文件")
            return

        formatter = YanFormatter()
        success = formatter.format_file(args[1])
        if success:
            print(f"✅ {args[1]} 格式化完成")

    elif command == "检查" or command == "check" or command == "lint":
        if len(args) < 2:
            print("错误: 请指定要检查的文件")
            return

        linter = YanLinter()
        issues = linter.lint_file(args[1])
        linter.print_report(issues)

    elif command == "帮助" or command == "help":
        print("言语言代码工具")
        print()
        print("命令:")
        print("  格式化 <文件>  - 格式化代码")
        print("  检查 <文件>    - 检查代码")
        print("  帮助           - 显示帮助")

    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
