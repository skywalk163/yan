#!/usr/bin/env python3
"""
标准库扩展测试
"""

import sys
sys.path.insert(0, '../')

from yan_test import suite, test, run, print_summary
from yan_assertions import *

@suite("JSON库测试")
class JSONTest:
    @test("解析JSON字符串")
    def test_parse(self):
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'yan', '-e', '引 JSON；印 JSON.解析("{\"name\": \"测试\"}")'],
            capture_output=True, text=True, cwd='../'
        )
        assert '"name"' in result.stdout
    
    @test("生成JSON字符串")
    def test_generate(self):
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'yan', '-e', '引 JSON；印 JSON.生成({"name": "测试"})'],
            capture_output=True, text=True, cwd='../'
        )
        assert '"name"' in result.stdout

@suite("正则库测试")
class RegexTest:
    @test("匹配测试")
    def test_match(self):
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'yan', '-e', '引 正则；印 正则.匹配("^hello", "hello world")'],
            capture_output=True, text=True, cwd='../'
        )
        assert 'True' in result.stdout
    
    @test("替换测试")
    def test_replace(self):
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'yan', '-e', '引 正则；印 正则.替换("\\d+", "X", "abc123def")'],
            capture_output=True, text=True, cwd='../'
        )
        assert 'abcXdef' in result.stdout

@suite("日期库测试")
class DateTest:
    @test("获取当前时间")
    def test_current_time(self):
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'yan', '-e', '引 日期；印 日期.当前时间()'],
            capture_output=True, text=True, cwd='../', timeout=10
        )
        assert result.returncode == 0
    
    @test("格式化日期")
    def test_format(self):
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'yan', '-e', '引 日期；印 日期.格式化(日期.当前时间(), "%Y-%m-%d")'],
            capture_output=True, text=True, cwd='../', timeout=10
        )
        assert len(result.stdout.strip()) == 10  # YYYY-MM-DD

if __name__ == '__main__':
    report = run()
    print_summary(report)
    exit(1 if report['failed'] > 0 else 0)
