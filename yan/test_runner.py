"""
言语言测试运行器
"""

import sys
import os
import glob
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen
from runtime import YanAssertionError, ALL_BUILTINS


@dataclass
class TestResult:
    """测试结果"""
    name: str
    passed: bool
    error: Optional[str] = None
    duration: float = 0.0
    classname: str = ""


@dataclass
class TestSuiteResult:
    """测试套件结果"""
    name: str
    tests: List[TestResult] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    duration: float = 0.0
    errors: int = 0
    skipped: int = 0


@dataclass
class TestDiscovery:
    """测试发现配置"""
    patterns: List[str] = field(default_factory=lambda: ["**/*.yan", "**/test_*.yan"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["**/node_modules/**", "**/.venv/**"])
    root_dir: str = "."


class TestRunner:
    """测试运行器"""

    def __init__(self, verbose: bool = False, discovery: TestDiscovery = None):
        self.verbose = verbose
        self.discovery = discovery or TestDiscovery()
        self.results: List[TestSuiteResult] = []
        self.start_time: datetime = None
        self.end_time: datetime = None

    def discover_tests(self, root_dir: str = None) -> List[str]:
        """自动发现测试文件

        Args:
            root_dir: 根目录，默认为当前目录

        Returns:
            发现的测试文件路径列表
        """
        if root_dir is None:
            root_dir = self.discovery.root_dir

        discovered_files = []

        for pattern in self.discovery.patterns:
            search_path = os.path.join(root_dir, pattern)
            matches = glob.glob(search_path, recursive=True)

            for filepath in matches:
                if self._should_exclude(filepath):
                    continue
                if filepath not in discovered_files:
                    discovered_files.append(filepath)

        return sorted(discovered_files)

    def _should_exclude(self, filepath: str) -> bool:
        """检查文件是否应该被排除"""
        for exclude_pattern in self.discovery.exclude_patterns:
            if exclude_pattern.startswith("**/"):
                parts = exclude_pattern[4:].split("/")
                if all(part in filepath for part in parts if part):
                    return True
            elif exclude_pattern in filepath:
                return True
        return False

    def run_file(self, filepath: str) -> TestSuiteResult:
        """运行测试文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        lexer = Lexer()
        tokens = lexer.tokenize(source)
        parser = Parser()
        ast = parser.parse(tokens)

        return self._run_program(ast, filepath)

    def _run_program(self, program, filename: str) -> TestSuiteResult:
        """运行程序中的测试"""
        from nodes import Test, TestSuite

        suite_name = os.path.basename(filename)
        tests = []
        passed = 0
        failed = 0
        start_time = datetime.now()

        for stmt in program.statements:
            if isinstance(stmt, TestSuite):
                suite_result = self._run_test_suite(stmt)
                self.results.append(suite_result)
                tests.extend(suite_result.tests)
                passed += suite_result.passed
                failed += suite_result.failed
            elif isinstance(stmt, Test):
                result = self._run_test(stmt)
                tests.append(result)
                if result.passed:
                    passed += 1
                else:
                    failed += 1

        duration = (datetime.now() - start_time).total_seconds()
        return TestSuiteResult(suite_name, tests, passed, failed, duration)

    def _run_test_suite(self, suite) -> TestSuiteResult:
        """运行测试套件"""
        from nodes import Test
        from codegen import PythonCodeGen

        tests = []
        passed = 0
        failed = 0
        start_time = datetime.now()

        env = {}
        for name, (func, arity) in ALL_BUILTINS.items():
            func_name = func.__name__ if hasattr(func, '__name__') else str(func)
            env[func_name] = func
            env[name] = func

        gen = PythonCodeGen()

        if suite.setup:
            try:
                self._execute_node(suite.setup, env, gen)
            except Exception as e:
                if self.verbose:
                    print(f"前置钩子失败: {e}")
                return TestSuiteResult(suite.name, [], 0, len(suite.tests))

        for test in suite.tests:
            result = self._run_test(test, env, gen)
            result.classname = suite.name
            tests.append(result)
            if result.passed:
                passed += 1
            else:
                failed += 1

        if suite.teardown:
            try:
                self._execute_node(suite.teardown, env, gen)
            except Exception as e:
                if self.verbose:
                    print(f"后置钩子失败: {e}")

        duration = (datetime.now() - start_time).total_seconds()
        return TestSuiteResult(suite.name, tests, passed, failed, duration)

    def _run_test(self, test, env=None, gen=None) -> TestResult:
        """运行单个测试"""
        start_time = datetime.now()

        try:
            self._execute_node(test.body, env, gen)
            duration = (datetime.now() - start_time).total_seconds()
            return TestResult(test.name, True, None, duration)
        except YanAssertionError as e:
            duration = (datetime.now() - start_time).total_seconds()
            return TestResult(test.name, False, str(e), duration)
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return TestResult(test.name, False, f"运行时错误: {e}", duration)

    def _execute_node(self, node, env=None, gen=None):
        """执行 AST 节点"""
        from nodes import Program, Test, TestSuite, Define, Call, Word, Num, Str, Bool, Nil, Block, If, ForEach, While
        from codegen import PythonCodeGen
        import runtime

        if gen is None:
            gen = PythonCodeGen()
        code = gen.generate(Program([node]))

        if env is None:
            env = {}
            for name, (func, arity) in ALL_BUILTINS.items():
                func_name = func.__name__ if hasattr(func, '__name__') else str(func)
                env[func_name] = func
                env[name] = func

        exec(code, env, env)
        return env, gen

    def run_all(self, root_dir: str = None) -> bool:
        """运行所有发现的测试

        Args:
            root_dir: 测试文件根目录

        Returns:
            所有测试是否通过
        """
        self.start_time = datetime.now()
        test_files = self.discover_tests(root_dir)

        if self.verbose:
            print(f"发现 {len(test_files)} 个测试文件")

        for filepath in test_files:
            if self.verbose:
                print(f"运行: {filepath}")
            self.run_file(filepath)

        self.end_time = datetime.now()
        return self.print_report()

    def print_report(self) -> bool:
        """打印测试报告"""
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_tests = total_passed + total_failed

        print("\n" + "=" * 60)
        print("测试报告")
        print("=" * 60)

        for suite in self.results:
            print(f"\n套件: {suite.name}")
            print("-" * 40)

            for test in suite.tests:
                status = "[PASS]" if test.passed else "[FAIL]"
                print(f"  {status} {test.name}")
                if not test.passed and test.error:
                    error_lines = test.error.split('\n')
                    for line in error_lines:
                        print(f"      {line}")

        print("\n" + "=" * 60)
        print(f"总计: {total_tests} 个测试")
        print(f"  通过: {total_passed}")
        print(f"  失败: {total_failed}")
        print("=" * 60)

        return total_failed == 0

    def generate_html_report(self, output_path: str = "test_report.html") -> str:
        """生成 HTML 测试报告

        Args:
            output_path: 输出文件路径

        Returns:
            HTML 报告内容
        """
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_tests = total_passed + total_failed
        total_duration = sum(s.duration for s in self.results)

        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>言语言测试报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .stat {{
            background: rgba(255,255,255,0.2);
            padding: 15px 25px;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .passed {{ color: #10b981; }}
        .failed {{ color: #ef4444; }}
        .suite {{
            background: white;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .suite-header {{
            background: #f8fafc;
            padding: 15px 20px;
            border-bottom: 1px solid #e2e8f0;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .suite-name {{
            font-weight: bold;
            font-size: 1.1em;
            color: #334155;
        }}
        .suite-stats {{
            display: flex;
            gap: 15px;
            font-size: 0.9em;
        }}
        .test {{
            padding: 12px 20px;
            border-bottom: 1px solid #f1f5f9;
            display: flex;
            align-items: center;
        }}
        .test:last-child {{
            border-bottom: none;
        }}
        .test-status {{
            width: 60px;
            font-weight: bold;
        }}
        .test-name {{
            flex: 1;
            color: #475569;
        }}
        .test-duration {{
            color: #94a3b8;
            font-size: 0.85em;
        }}
        .test-error {{
            background: #fef2f2;
            color: #dc2626;
            padding: 10px 20px 10px 80px;
            font-family: monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .summary {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .timestamp {{
            color: #64748b;
            font-size: 0.9em;
        }}
        .chart {{
            display: flex;
            height: 30px;
            border-radius: 5px;
            overflow: hidden;
            margin: 15px 0;
        }}
        .chart-passed {{
            background: #10b981;
            transition: width 0.3s ease;
        }}
        .chart-failed {{
            background: #ef4444;
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 言语言测试报告</h1>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_tests}</div>
                    <div class="stat-label">总测试数</div>
                </div>
                <div class="stat">
                    <div class="stat-value passed">{total_passed}</div>
                    <div class="stat-label">通过</div>
                </div>
                <div class="stat">
                    <div class="stat-value failed">{total_failed}</div>
                    <div class="stat-label">失败</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_duration:.2f}s</div>
                    <div class="stat-label">耗时</div>
                </div>
            </div>
        </div>

        <div class="chart">
            <div class="chart-passed" style="width: {total_passed / total_tests * 100 if total_tests > 0 else 0}%"></div>
            <div class="chart-failed" style="width: {total_failed / total_tests * 100 if total_tests > 0 else 0}%"></div>
        </div>
"""

        for suite in self.results:
            suite_stats = f'<span class="passed">✓ {suite.passed}</span> / <span class="failed">✗ {suite.failed}</span>'
            html_template += f"""
        <div class="suite">
            <div class="suite-header">
                <span class="suite-name">{suite.name}</span>
                <span class="suite-stats">{suite_stats} · {suite.duration:.2f}s</span>
            </div>
"""
            for test in suite.tests:
                status_icon = "✓" if test.passed else "✗"
                status_class = "passed" if test.passed else "failed"
                html_template += f"""
            <div class="test">
                <span class="test-status {status_class}">{status_icon}</span>
                <span class="test-name">{test.name}</span>
                <span class="test-duration">{test.duration*1000:.1f}ms</span>
            </div>
"""
                if not test.passed and test.error:
                    error_html = self._escape_html(test.error)
                    html_template += f"""
            <div class="test-error">{error_html}</div>
"""
            html_template += """
        </div>
"""

        end_time = self.end_time or datetime.now()
        start_time = self.start_time or datetime.now()
        html_template += f"""
        <div class="summary">
            <p class="timestamp">测试时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)

        return html_template

    def _escape_html(self, text: str) -> str:
        """转义 HTML 特殊字符"""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))

    def generate_junit_report(self, output_path: str = "test_report.xml") -> str:
        """生成 JUnit XML 测试报告

        Args:
            output_path: 输出文件路径

        Returns:
            JUnit XML 报告内容
        """
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_tests = total_passed + total_failed
        total_duration = sum(s.duration for s in self.results)

        testsuite = Element('testsuite')
        testsuite.set('name', 'yan-tests')
        testsuite.set('tests', str(total_tests))
        testsuite.set('failures', str(total_failed))
        testsuite.set('errors', '0')
        testsuite.set('skipped', '0')
        testsuite.set('time', f"{total_duration:.3f}")

        start_time = self.start_time or datetime.now()
        testsuite.set('timestamp', start_time.strftime('%Y-%m-%dT%H:%M:%S'))

        for suite in self.results:
            testcase = None
            for test in suite.tests:
                testcase = SubElement(testsuite, 'testcase')
                testcase.set('classname', suite.name)
                testcase.set('name', test.name)
                testcase.set('time', f"{test.duration:.3f}")

                if not test.passed:
                    failure = SubElement(testcase, 'failure')
                    failure.set('type', 'AssertionError')
                    failure.text = test.error or "Test failed"

        xml_str = tostring(testsuite, encoding='unicode')

        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")

        pretty_xml = "\n".join(pretty_xml.split("\n")[1:])

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

        return pretty_xml

    def generate_json_report(self) -> dict:
        """生成 JSON 测试报告

        Returns:
            JSON 格式的测试报告
        """
        import json

        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_tests = total_passed + total_failed
        total_duration = sum(s.duration for s in self.results)

        return {
            "summary": {
                "total": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "skipped": 0,
                "duration": total_duration,
                "timestamp": datetime.now().isoformat()
            },
            "suites": [
                {
                    "name": suite.name,
                    "tests": [
                        {
                            "name": test.name,
                            "passed": test.passed,
                            "error": test.error,
                            "duration": test.duration,
                            "classname": test.classname or suite.name
                        }
                        for test in suite.tests
                    ],
                    "passed": suite.passed,
                    "failed": suite.failed,
                    "duration": suite.duration
                }
                for suite in self.results
            ]
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='言语言测试运行器')
    parser.add_argument('paths', nargs='*', help='测试文件路径或目录')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('--discover', action='store_true', help='自动发现测试文件')
    parser.add_argument('--pattern', action='append', help='测试文件匹配模式 (可多次指定)')
    parser.add_argument('--exclude', action='append', help='排除的文件模式 (可多次指定)')
    parser.add_argument('--html', metavar='FILE', help='生成 HTML 报告')
    parser.add_argument('--junit', metavar='FILE', help='生成 JUnit XML 报告')
    parser.add_argument('--json', metavar='FILE', help='生成 JSON 报告')

    args = parser.parse_args()

    discovery_config = TestDiscovery()
    if args.pattern:
        discovery_config.patterns = args.pattern
    if args.exclude:
        discovery_config.exclude_patterns = args.exclude

    runner = TestRunner(verbose=args.verbose, discovery=discovery_config)

    if args.discover or not args.paths:
        test_files = runner.discover_tests(args.paths[0] if args.paths else ".")
        if args.verbose:
            print(f"发现 {len(test_files)} 个测试文件:")
            for f in test_files:
                print(f"  - {f}")
        for filepath in test_files:
            runner.run_file(filepath)
    else:
        for path in args.paths:
            if os.path.isdir(path):
                test_files = runner.discover_tests(path)
                for filepath in test_files:
                    runner.run_file(filepath)
            elif os.path.isfile(path):
                runner.run_file(path)
            else:
                print(f"警告: 路径不存在: {path}")

    runner.print_report()

    if args.html:
        runner.generate_html_report(args.html)
        print(f"\nHTML 报告已生成: {args.html}")

    if args.junit:
        runner.generate_junit_report(args.junit)
        print(f"\nJUnit XML 报告已生成: {args.junit}")

    if args.json:
        import json
        report = runner.generate_json_report()
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nJSON 报告已生成: {args.json}")

    total_failed = sum(r.failed for r in runner.results)
    sys.exit(0 if total_failed == 0 else 1)


if __name__ == '__main__':
    main()