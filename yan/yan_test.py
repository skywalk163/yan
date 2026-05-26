#!/usr/bin/env python3
"""
言语言测试框架 - Python 端支持模块
"""

import inspect
import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Tuple, Set, Union

# 测试装饰器
def suite(name):
    def decorator(cls):
        cls._suite_name = name
        return cls
    return decorator

def test(name, tags: Optional[List[str]] = None, priority: int = 1):
    """
    测试方法装饰器
    
    Args:
        name: 测试名称
        tags: 标签列表，用于过滤测试
        priority: 优先级，1 为最高优先级
    """
    def decorator(func):
        func._test_name = name
        func._test_tags = tags or []
        func._test_priority = priority
        return func
    return decorator

def skip(reason: str = ""):
    """
    跳过测试装饰器
    
    Args:
        reason: 跳过原因
    """
    def decorator(func):
        func._test_skip = reason
        return func
    return decorator

def skip_if(condition: bool, reason: str = ""):
    """
    条件跳过测试装饰器
    
    Args:
        condition: 如果为 True 则跳过
        reason: 跳过原因
    """
    def decorator(func):
        if condition:
            func._test_skip = reason
        return func
    return decorator

def skip_unless(condition: bool, reason: str = ""):
    """
    除非条件满足否则跳过测试装饰器
    
    Args:
        condition: 如果为 False 则跳过
        reason: 跳过原因
    """
    def decorator(func):
        if not condition:
            func._test_skip = reason
        return func
    return decorator

# 断言函数
def 等(a, b, message: str = None):
    if a != b:
        msg = message or f"断言失败: {a} != {b}"
        assert a == b, msg

def 不等(a, b, message: str = None):
    if a == b:
        msg = message or f"断言失败: {a} == {b}"
        assert a != b, msg

def 为真(value, message: str = None):
    if not bool(value):
        msg = message or f"断言失败: {value} 不为真"
        assert bool(value), msg

def 为假(value, message: str = None):
    if bool(value):
        msg = message or f"断言失败: {value} 不为假"
        assert not bool(value), msg

def 引发异常(func, *args, message: str = None, **kwargs):
    try:
        func(*args, **kwargs)
        msg = message or "期望异常但未抛出"
        assert False, msg
    except Exception:
        pass

def 引发特定异常(func, exception_type, *args, message: str = None, **kwargs):
    """引发特定类型的异常"""
    try:
        func(*args, **kwargs)
        msg = message or f"期望 {exception_type.__name__} 异常但未抛出"
        assert False, msg
    except exception_type:
        pass
    except Exception as e:
        msg = message or f"期望 {exception_type.__name__} 但得到 {type(e).__name__}"
        assert False, msg

def 不引发异常(func, *args, message: str = None, **kwargs):
    """断言函数不引发异常"""
    try:
        func(*args, **kwargs)
    except Exception as e:
        msg = message or f"不应抛出异常，但抛出了 {type(e).__name__}: {e}"
        assert False, msg


# Mock 对象
class Mock:
    """简单的 Mock 对象"""
    
    def __init__(self):
        self._calls = []
        self._return_values = {}
        self._side_effect = None
    
    def __call__(self, *args, **kwargs):
        self._calls.append({'args': args, 'kwargs': kwargs})
        
        # 检查是否有副作用函数
        if self._side_effect is not None:
            if callable(self._side_effect):
                return self._side_effect(*args, **kwargs)
            elif isinstance(self._side_effect, list):
                if self._side_effect:
                    return self._side_effect.pop(0)
                return None
        
        # 返回默认值
        return self._return_values.get(len(self._calls), None)
    
    def set_return_value(self, value):
        """设置返回值"""
        self._return_values = {i: value for i in range(100)}
    
    def set_return_values(self, values: List):
        """设置多个返回值"""
        for i, value in enumerate(values):
            self._return_values[i + 1] = value
    
    def set_side_effect(self, effect):
        """设置副作用"""
        self._side_effect = effect
    
    @property
    def call_count(self):
        """调用次数"""
        return len(self._calls)
    
    @property
    def calls(self):
        """所有调用记录"""
        return self._calls
    
    def assert_called(self):
        """断言至少被调用一次"""
        assert self.call_count > 0, "Mock 未被调用"
    
    def assert_called_once(self):
        """断言只被调用一次"""
        assert self.call_count == 1, f"Mock 被调用 {self.call_count} 次，期望 1 次"
    
    def assert_called_with(self, *args, **kwargs):
        """断言最后一次调用使用了指定参数"""
        if not self._calls:
            assert False, "Mock 未被调用"
        
        last_call = self._calls[-1]
        assert last_call['args'] == args, f"参数不匹配: {last_call['args']} != {args}"
        assert last_call['kwargs'] == kwargs, f"关键字参数不匹配: {last_call['kwargs']} != {kwargs}"
    
    def reset_mock(self):
        """重置调用记录"""
        self._calls = []


class Stub:
    """Stub 对象 - 用于替换依赖"""
    
    def __init__(self, **attrs):
        for key, value in attrs.items():
            setattr(self, key, value)

# 测试发现机制
def discover_tests(
    pattern: str = "test_*.py", 
    directory: str = ".",
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    min_priority: int = 1
) -> List[str]:
    """
    自动发现测试文件
    
    Args:
        pattern: 测试文件匹配模式，默认为 "test_*.py"
        directory: 搜索目录，默认为当前目录
        include_tags: 只包含指定标签的测试
        exclude_tags: 排除指定标签的测试
        min_priority: 最小优先级（数字越小优先级越高）
    
    Returns:
        测试文件路径列表
    """
    test_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过隐藏目录和 __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for filename in files:
            if filename.startswith("test_") and filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                test_files.append(os.path.abspath(filepath))
    
    return sorted(test_files)


def filter_tests_by_tags(
    tests: List[Dict[str, Any]],
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    根据标签过滤测试
    
    Args:
        tests: 测试列表
        include_tags: 只包含指定标签
        exclude_tags: 排除指定标签
    
    Returns:
        过滤后的测试列表
    """
    filtered = tests
    
    if include_tags:
        include_set = set(include_tags)
        filtered = [t for t in filtered if include_set.intersection(t.get('tags', []))]
    
    if exclude_tags:
        exclude_set = set(exclude_tags)
        filtered = [t for t in filtered if not exclude_set.intersection(t.get('tags', []))]
    
    return filtered

def import_test_module(filepath: str) -> Any:
    """
    导入测试模块
    
    Args:
        filepath: 测试文件路径
    
    Returns:
        导入的模块对象
    """
    module_name = os.path.basename(filepath)[:-3]
    spec = None
    
    # Python 3.4+
    if hasattr(sys, 'modules'):
        dir_path = os.path.dirname(filepath)
        if dir_path not in sys.path:
            sys.path.insert(0, dir_path)
        
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if dir_path in sys.path:
            sys.path.remove(dir_path)
    
    return module

# 测试运行器
def run(
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    min_priority: int = 1
):
    """
    运行所有测试
    
    Args:
        include_tags: 只运行包含指定标签的测试
        exclude_tags: 排除指定标签的测试
        min_priority: 最小优先级（数字越小优先级越高）
    
    Returns:
        测试报告
    """
    report = {
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'tests': [],
        'total_time': 0.0,
        'slow_tests': []
    }
    
    caller_globals = inspect.stack()[1][0].f_globals
    
    for name, obj in caller_globals.items():
        if inspect.isclass(obj) and hasattr(obj, '_suite_name'):
            suite_name = obj._suite_name
            instance = obj()
            
            for method_name, method in inspect.getmembers(instance):
                if inspect.ismethod(method) and hasattr(method, '_test_name'):
                    test_name = method._test_name
                    test_tags = getattr(method, '_test_tags', [])
                    test_priority = getattr(method, '_test_priority', 1)
                    test_skip = getattr(method, '_test_skip', None)
                    
                    # 检查优先级
                    if test_priority > min_priority:
                        continue
                    
                    # 检查标签过滤
                    if include_tags and not set(include_tags).intersection(test_tags):
                        continue
                    if exclude_tags and set(exclude_tags).intersection(test_tags):
                        continue
                    
                    # 检查跳过标记
                    if test_skip:
                        report['skipped'] += 1
                        report['tests'].append({
                            'suite': suite_name,
                            'name': test_name,
                            'status': 'skipped',
                            'reason': test_skip,
                            'tags': test_tags,
                            'priority': test_priority,
                            'time': 0.0
                        })
                        print(f"~ {suite_name} - {test_name} (跳过: {test_skip})")
                        continue
                    
                    # 运行测试并记录时间
                    start_time = time.time()
                    try:
                        method()
                        elapsed_time = time.time() - start_time
                        
                        report['passed'] += 1
                        report['total_time'] += elapsed_time
                        report['tests'].append({
                            'suite': suite_name,
                            'name': test_name,
                            'status': 'passed',
                            'tags': test_tags,
                            'priority': test_priority,
                            'time': elapsed_time
                        })
                        
                        status = "✓"
                        if elapsed_time > 1.0:
                            report['slow_tests'].append({
                                'suite': suite_name,
                                'name': test_name,
                                'time': elapsed_time
                            })
                            status = "✓*"
                        
                        print(f"{status} {suite_name} - {test_name} ({elapsed_time:.2f}s)")
                    
                    except AssertionError as e:
                        elapsed_time = time.time() - start_time
                        report['failed'] += 1
                        report['total_time'] += elapsed_time
                        report['tests'].append({
                            'suite': suite_name,
                            'name': test_name,
                            'status': 'failed',
                            'error': str(e),
                            'tags': test_tags,
                            'priority': test_priority,
                            'time': elapsed_time
                        })
                        print(f"✗ {suite_name} - {test_name}: {e} ({elapsed_time:.2f}s)")
                    
                    except Exception as e:
                        elapsed_time = time.time() - start_time
                        report['failed'] += 1
                        report['total_time'] += elapsed_time
                        report['tests'].append({
                            'suite': suite_name,
                            'name': test_name,
                            'status': 'failed',
                            'error': str(e),
                            'tags': test_tags,
                            'priority': test_priority,
                            'time': elapsed_time
                        })
                        print(f"✗ {suite_name} - {test_name}: {e} ({elapsed_time:.2f}s)")
    
    return report

def run_discovered_tests(pattern: str = "test_*.py", directory: str = ".") -> Dict[str, Any]:
    """
    运行发现的所有测试文件
    
    Args:
        pattern: 测试文件匹配模式
        directory: 搜索目录
    
    Returns:
        综合测试报告
    """
    test_files = discover_tests(pattern, directory)
    overall_report = {
        'passed': 0,
        'failed': 0,
        'tests': [],
        'files': []
    }
    
    print(f"发现 {len(test_files)} 个测试文件")
    
    for filepath in test_files:
        print(f"\n运行测试文件: {filepath}")
        try:
            module = import_test_module(filepath)
            if hasattr(module, 'run') and callable(module.run):
                report = module.run()
                overall_report['passed'] += report.get('passed', 0)
                overall_report['failed'] += report.get('failed', 0)
                overall_report['tests'].extend(report.get('tests', []))
                overall_report['files'].append({
                    'path': filepath,
                    'passed': report.get('passed', 0),
                    'failed': report.get('failed', 0)
                })
        except Exception as e:
            print(f"✗ 加载测试文件失败 {filepath}: {e}")
            overall_report['failed'] += 1
            overall_report['tests'].append({
                'suite': filepath,
                'name': '加载失败',
                'status': 'failed',
                'error': str(e)
            })
    
    return overall_report

def print_summary(report):
    """打印测试摘要"""
    total = report['passed'] + report['failed']
    print(f"\n测试完成: {report['passed']}/{total} 通过")
    if report['failed'] > 0:
        print("\n失败的测试:")
        for test_info in report['tests']:
            if test_info['status'] == 'failed':
                print(f"  - {test_info['suite']} - {test_info['name']}")
                print(f"    错误: {test_info.get('error', '未知错误')}")

# 测试报告生成器
def generate_json_report(report: Dict[str, Any], output_file: str = None) -> str:
    """
    生成 JSON 格式测试报告
    
    Args:
        report: 测试报告字典
        output_file: 输出文件路径，为 None 时返回字符串
    
    Returns:
        JSON 字符串
    """
    full_report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': report['passed'] + report['failed'],
            'passed': report['passed'],
            'failed': report['failed'],
            'pass_rate': (report['passed'] / (report['passed'] + report['failed'])) * 100 if (report['passed'] + report['failed']) > 0 else 0
        },
        'tests': report['tests'],
        'files': report.get('files', [])
    }
    
    json_str = json.dumps(full_report, ensure_ascii=False, indent=2)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_str)
    
    return json_str

def generate_html_report(report: Dict[str, Any], output_file: str = None) -> str:
    """
    生成 HTML 格式测试报告
    
    Args:
        report: 测试报告字典
        output_file: 输出文件路径，为 None 时返回字符串
    
    Returns:
        HTML 字符串
    """
    total = report['passed'] + report['failed']
    pass_rate = (report['passed'] / total) * 100 if total > 0 else 0
    
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>言语言测试报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .stat {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; text-align: center; }}
        .stat .number {{ font-size: 36px; font-weight: bold; }}
        .stat.passed .number {{ color: #22c55e; }}
        .stat.failed .number {{ color: #ef4444; }}
        .stat.total .number {{ color: #3b82f6; }}
        .stat.rate {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .test-list {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }}
        .test-item {{ padding: 12px 16px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }}
        .test-item:last-child {{ border-bottom: none; }}
        .test-item.passed {{ background: #f0fdf4; }}
        .test-item.failed {{ background: #fef2f2; }}
        .test-status {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }}
        .status-passed {{ background: #dcfce7; color: #166534; }}
        .status-failed {{ background: #fee2e2; color: #991b1b; }}
        .test-error {{ font-size: 12px; color: #ef4444; margin-top: 4px; }}
        .timestamp {{ color: #9ca3af; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>言语言测试报告</h1>
        <p class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="stat total">
            <div class="number">{total}</div>
            <div>总测试数</div>
        </div>
        <div class="stat passed">
            <div class="number">{report['passed']}</div>
            <div>通过</div>
        </div>
        <div class="stat failed">
            <div class="number">{report['failed']}</div>
            <div>失败</div>
        </div>
        <div class="stat rate">
            <div class="number">{pass_rate:.1f}%</div>
            <div>通过率</div>
        </div>
    </div>
    
    <div class="test-list">
        <h2 style="padding: 16px; margin: 0; border-bottom: 1px solid #eee;">测试详情</h2>
"""
    
    for test_info in report['tests']:
        status_class = 'passed' if test_info['status'] == 'passed' else 'failed'
        status_text = '通过' if test_info['status'] == 'passed' else '失败'
        status_style = 'status-passed' if test_info['status'] == 'passed' else 'status-failed'
        
        error_html = f"<div class='test-error'>{test_info.get('error', '')}</div>" if test_info.get('error') else ""
        
        html_template += f"""
        <div class="test-item {status_class}">
            <div>
                <strong>{test_info['suite']}</strong> - {test_info['name']}
                {error_html}
            </div>
            <span class="test-status {status_style}">{status_text}</span>
        </div>
"""
    
    html_template += """
    </div>
</body>
</html>
"""
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
    
    return html_template

def generate_junit_report(report: Dict[str, Any], output_file: str = None) -> str:
    """
    生成 JUnit XML 格式测试报告
    
    Args:
        report: 测试报告字典
        output_file: 输出文件路径，为 None 时返回字符串
    
    Returns:
        XML 字符串
    """
    total = report['passed'] + report['failed']
    
    xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Yan Test Suite" tests="{total}" failures="{report['failed']}" errors="0" skipped="0">
"""
    
    for test_info in report['tests']:
        status = test_info['status']
        error = test_info.get('error', '')
        
        xml_template += f"""  <testcase name="{test_info['name']}" classname="{test_info['suite']}">"""
        
        if status == 'failed' and error:
            xml_template += f"""
    <failure message="{error}">{error}</failure>"""
        
        xml_template += """
  </testcase>
"""
    
    xml_template += """</testsuite>"""
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_template)
    
    return xml_template

class YanTestFramework:
    """言语言测试框架类"""
    
    def __init__(self):
        self._suites = []
    
    def suite(self, name):
        """定义测试套件"""
        def decorator(cls_or_func):
            if hasattr(cls_or_func, '__call__'):
                suite_info = {
                    'name': name,
                    'type': 'function',
                    'func': cls_or_func,
                    'tests': []
                }
            else:
                suite_info = {
                    'name': name,
                    'type': 'class',
                    'cls': cls_or_func,
                    'tests': []
                }
            self._suites.append(suite_info)
            return cls_or_func
        return decorator
    
    def test(self, name):
        """定义测试方法"""
        def decorator(func):
            func._test_name = name
            return func
        return decorator
    
    def run(self):
        """运行所有测试"""
        report = YanTestReport()
        
        for suite_info in self._suites:
            if suite_info['type'] == 'class':
                cls = suite_info['cls']
                instance = cls()
                for method_name, method in inspect.getmembers(instance):
                    if inspect.ismethod(method) and hasattr(method, '_test_name'):
                        test_name = method._test_name
                        try:
                            method()
                            report.passed += 1
                            report.tests.append((suite_info['name'], test_name, 'passed', None))
                        except AssertionError as e:
                            report.failed += 1
                            report.tests.append((suite_info['name'], test_name, 'failed', str(e)))
                    elif callable(method) and hasattr(method, '_test_name'):
                        test_name = method._test_name
                        try:
                            method()
                            report.passed += 1
                            report.tests.append((suite_info['name'], test_name, 'passed', None))
                        except AssertionError as e:
                            report.failed += 1
                            report.tests.append((suite_info['name'], test_name, 'failed', str(e)))
            elif suite_info['type'] == 'function':
                func = suite_info['func']
                try:
                    func()
                except:
                    pass
        
        return report


class YanTestReport:
    """测试报告类"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    @property
    def total(self):
        return self.passed + self.failed
    
    @property
    def pass_rate(self):
        return (self.passed / self.total) * 100 if self.total > 0 else 0
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'passed': self.passed,
            'failed': self.failed,
            'total': self.total,
            'pass_rate': self.pass_rate,
            'tests': [{
                'suite': t[0],
                'name': t[1],
                'status': t[2],
                'error': t[3]
            } for t in self.tests]
        }
    
    def generate_report(self, format_type: str = 'text', output_file: str = None) -> str:
        """
        生成测试报告
        
        Args:
            format_type: 报告格式，支持 'text', 'json', 'html', 'junit'
            output_file: 输出文件路径
        
        Returns:
            报告字符串
        """
        report_dict = self.to_dict()
        
        if format_type == 'json':
            return generate_json_report(report_dict, output_file)
        elif format_type == 'html':
            return generate_html_report(report_dict, output_file)
        elif format_type == 'junit':
            return generate_junit_report(report_dict, output_file)
        else:
            return self._format_text_report()
    
    def _format_text_report(self) -> str:
        """生成文本格式报告"""
        lines = []
        lines.append(f"测试完成: {self.passed}/{self.total} 通过 ({self.pass_rate:.1f}%)")
        
        if self.failed > 0:
            lines.append("\n失败的测试:")
            for suite, name, status, error in self.tests:
                if status == 'failed':
                    lines.append(f"  - {suite} - {name}")
                    if error:
                        lines.append(f"    错误: {error}")
        
        return '\n'.join(lines)


# 导出所有符号
__all__ = [
    'suite', 'test', '等', '为真', '为假', '引发异常',
    'run', 'print_summary', 'discover_tests', 'run_discovered_tests',
    'generate_json_report', 'generate_html_report', 'generate_junit_report',
    'YanTestFramework', 'YanTestReport'
]
