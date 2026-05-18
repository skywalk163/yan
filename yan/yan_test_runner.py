#!/usr/bin/env python3
"""
言语言测试运行器 - 命令行测试工具
"""

import argparse
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from yan_test import (
    run_discovered_tests,
    generate_json_report,
    generate_html_report,
    generate_junit_report
)

def main():
    parser = argparse.ArgumentParser(description='言语言测试运行器')
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='测试文件搜索目录（默认当前目录）'
    )
    parser.add_argument(
        '-p', '--pattern',
        default='test_*.py',
        help='测试文件匹配模式（默认 test_*.py）'
    )
    parser.add_argument(
        '-o', '--output',
        help='报告输出文件路径'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'html', 'junit'],
        default='text',
        help='报告格式（默认 text）'
    )
    
    args = parser.parse_args()
    
    # 运行测试
    print(f"在目录 '{args.directory}' 中查找测试文件...")
    report = run_discovered_tests(args.pattern, args.directory)
    
    # 生成报告
    if args.format == 'json':
        report_content = generate_json_report(report, args.output)
    elif args.format == 'html':
        report_content = generate_html_report(report, args.output)
    elif args.format == 'junit':
        report_content = generate_junit_report(report, args.output)
    else:
        from yan_test import print_summary
        print_summary(report)
        return
    
    # 如果没有指定输出文件，打印到控制台
    if not args.output:
        print(report_content)
    else:
        print(f"报告已保存到: {args.output}")
    
    # 返回退出码
    if report['failed'] > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
