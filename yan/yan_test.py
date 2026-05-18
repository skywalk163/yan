#!/usr/bin/env python3
"""
言语言测试框架 - Python 端支持模块
"""

import inspect

# 测试装饰器
def suite(name):
    def decorator(cls):
        cls._suite_name = name
        return cls
    return decorator

def test(name):
    def decorator(func):
        func._test_name = name
        return func
    return decorator

# 断言函数
def 等(a, b):
    assert a == b, f"断言失败: {a} != {b}"

def 为真(value):
    assert bool(value), f"断言失败: {value} 不为真"

def 为假(value):
    assert not bool(value), f"断言失败: {value} 不为假"

def 引发异常(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        assert False, "期望异常但未抛出"
    except Exception:
        pass

# 测试运行器
def run():
    """运行所有测试"""
    report = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    # 获取调用者的全局命名空间
    caller_globals = inspect.stack()[1][0].f_globals
    
    for name, obj in caller_globals.items():
        if inspect.isclass(obj) and hasattr(obj, '_suite_name'):
            suite_name = obj._suite_name
            instance = obj()
            
            for method_name, method in inspect.getmembers(instance):
                if inspect.ismethod(method) and hasattr(method, '_test_name'):
                    test_name = method._test_name
                    try:
                        method()
                        report['passed'] += 1
                        report['tests'].append({
                            'suite': suite_name,
                            'name': test_name,
                            'status': 'passed'
                        })
                        print(f"✓ {suite_name} - {test_name}")
                    except AssertionError as e:
                        report['failed'] += 1
                        report['tests'].append({
                            'suite': suite_name,
                            'name': test_name,
                            'status': 'failed',
                            'error': str(e)
                        })
                        print(f"✗ {suite_name} - {test_name}: {e}")
                    except Exception as e:
                        report['failed'] += 1
                        report['tests'].append({
                            'suite': suite_name,
                            'name': test_name,
                            'status': 'failed',
                            'error': str(e)
                        })
                        print(f"✗ {suite_name} - {test_name}: {e}")
    
    return report

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

class YanTestFramework:
    """言语言测试框架类"""
    
    def __init__(self):
        self._suites = []
    
    def suite(self, name):
        """定义测试套件"""
        def decorator(cls_or_func):
            if hasattr(cls_or_func, '__call__'):
                # 函数风格
                suite_info = {
                    'name': name,
                    'type': 'function',
                    'func': cls_or_func,
                    'tests': []
                }
            else:
                # 类风格
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
                # 查找函数内定义的测试
                func = suite_info['func']
                # 执行函数以注册测试
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


# 导出所有符号
__all__ = ['suite', 'test', '等', '为真', '为假', '引发异常', 'run', 'print_summary', 'YanTestFramework', 'YanTestReport']
