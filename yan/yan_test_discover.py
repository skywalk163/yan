#!/usr/bin/env python3
"""
言语言测试发现机制

支持目录递归、标签过滤、测试优先级
"""

import os
import sys
import re
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class TestPriority(Enum):
    """测试优先级"""
    CRITICAL = 1  # 关键测试，必须通过
    HIGH = 2      # 高优先级
    NORMAL = 3   # 普通优先级
    LOW = 4       # 低优先级


@dataclass
class TestInfo:
    """测试信息"""
    name: str
    suite_name: str
    file_path: str
    line_number: int
    priority: TestPriority = TestPriority.NORMAL
    tags: Set[str] = field(default_factory=set)
    skip: bool = False
    skip_reason: str = ""
    timeout: Optional[float] = None
    flaky: bool = False


@dataclass 
class SuiteInfo:
    """测试套件信息"""
    name: str
    file_path: str
    line_number: int
    tags: Set[str] = field(default_factory=set)
    tests: List[TestInfo] = field(default_factory=list)


@dataclass
class DiscoveryResult:
    """测试发现结果"""
    suites: List[SuiteInfo]
    tests: List[TestInfo]
    total_files: int
    total_suites: int
    total_tests: int
    
    @property
    def passed(self):
        return 0
    
    @property
    def failed(self):
        return 0


class TestFilter:
    """测试过滤器"""
    
    def __init__(self):
        self.include_tags: Set[str] = set()
        self.exclude_tags: Set[str] = set()
        self.include_patterns: List[str] = []
        self.exclude_patterns: List[str] = []
        self.priorities: Set[TestPriority] = set()
        self.skip_flaky: bool = False
    
    def add_include_tag(self, tag: str):
        """添加包含标签"""
        self.include_tags.add(tag)
    
    def add_exclude_tag(self, tag: str):
        """添加排除标签"""
        self.exclude_tags.add(tag)
    
    def add_include_pattern(self, pattern: str):
        """添加包含模式"""
        self.include_patterns.append(pattern)
    
    def add_exclude_pattern(self, pattern: str):
        """添加排除模式"""
        self.exclude_patterns.append(pattern)
    
    def set_priorities(self, priorities: List[TestPriority]):
        """设置优先级"""
        self.priorities = set(priorities)
    
    def match(self, test: TestInfo) -> bool:
        """检查测试是否匹配过滤器"""
        # 检查标签
        if self.include_tags and not (test.tags & self.include_tags):
            return False
        if self.exclude_tags and (test.tags & self.exclude_tags):
            return False
        
        # 检查模式
        if self.include_patterns:
            matched = False
            for pattern in self.include_patterns:
                if re.search(pattern, test.name) or re.search(pattern, test.suite_name):
                    matched = True
                    break
            if not matched:
                return False
        
        if self.exclude_patterns:
            for pattern in self.exclude_patterns:
                if re.search(pattern, test.name) or re.search(pattern, test.suite_name):
                    return False
        
        # 检查优先级
        if self.priorities and test.priority not in self.priorities:
            return False
        
        # 检查 flaky
        if self.skip_flaky and test.flaky:
            return False
        
        return True


class TestDiscoverer:
    """测试发现器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.filter = TestFilter()
        self._test_patterns = [
            r'^test_.*\.py$',
            r'^.*_test\.py$',
            r'^Test.*\.py$',
        ]
        self._test_class_pattern = re.compile(r'class\s+(\w+)\s*\(.*\):')
        self._test_method_pattern = re.compile(r'def\s+(test_\w+)\s*\(')
        self._suite_decorator = re.compile(r'@suite\s*\(\s*["\']([^"\']+)["\']\s*\)')
        self._test_decorator = re.compile(r'@test\s*\(\s*["\']([^"\']+)["\']\s*\)')
        self._priority_decorator = re.compile(r'@priority\s*\(\s*(\w+)\s*\)')
        self._tags_decorator = re.compile(r'@tags\s*\(\s*\[(.*?)\]\s*\)')
        self._skip_decorator = re.compile(r'@skip\s*(?:\(\s*["\']([^"\']+)["\']\s*\))?')
    
    def discover(
        self,
        pattern: str = "test_*.py",
        recursive: bool = True,
        exclude_dirs: Optional[List[str]] = None
    ) -> DiscoveryResult:
        """发现测试
        
        Args:
            pattern: 测试文件匹配模式
            recursive: 是否递归搜索子目录
            exclude_dirs: 排除的目录列表
        
        Returns:
            测试发现结果
        """
        exclude_dirs = exclude_dirs or ['__pycache__', '.git', 'venv', 'env', 'node_modules']
        
        test_files = self._find_test_files(pattern, recursive, exclude_dirs)
        suites, tests = self._parse_test_files(test_files)
        
        return DiscoveryResult(
            suites=suites,
            tests=tests,
            total_files=len(test_files),
            total_suites=len(suites),
            total_tests=len(tests)
        )
    
    def discover_with_filter(self, test_filter: TestFilter, **kwargs) -> List[TestInfo]:
        """带过滤器发现测试
        
        Args:
            test_filter: 测试过滤器
            **kwargs: discover() 的其他参数
        
        Returns:
            匹配的测试列表
        """
        result = self.discover(**kwargs)
        self.filter = test_filter
        
        return [t for t in result.tests if test_filter.match(t)]
    
    def _find_test_files(
        self,
        pattern: str,
        recursive: bool,
        exclude_dirs: List[str]
    ) -> List[Path]:
        """查找测试文件"""
        test_files = []
        pattern_re = self._pattern_to_regex(pattern)
        
        if recursive:
            for path in self.root_dir.rglob('*'):
                if path.is_file() and self._matches_pattern(path.name, pattern_re):
                    if not any(ex in path.parts for ex in exclude_dirs):
                        test_files.append(path)
        else:
            for path in self.root_dir.glob(pattern):
                if path.is_file() and not any(ex in path.parts for ex in exclude_dirs):
                    test_files.append(path)
        
        return sorted(test_files)
    
    def _pattern_to_regex(self, pattern: str) -> str:
        """将通配符模式转换为正则表达式"""
        regex = pattern.replace('.', r'\.')
        regex = regex.replace('*', '.*')
        regex = regex.replace('?', '.')
        return regex
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """检查文件名是否匹配模式"""
        return bool(re.match(pattern, name))
    
    def _parse_test_files(self, files: List[Path]) -> Tuple[List[SuiteInfo], List[TestInfo]]:
        """解析测试文件"""
        suites = []
        all_tests = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                file_suites, file_tests = self._parse_test_content(
                    content, str(file_path)
                )
                
                for suite in file_suites:
                    suites.append(suite)
                all_tests.extend(file_tests)
            except Exception as e:
                print(f"解析测试文件失败: {file_path}, 错误: {e}")
        
        return suites, all_tests
    
    def _parse_test_content(self, content: str, file_path: str) -> Tuple[List[SuiteInfo], List[TestInfo]]:
        """解析测试文件内容"""
        suites = []
        all_tests = []
        
        lines = content.split('\n')
        
        current_suite_name = "默认套件"
        current_suite_tags = set()
        current_suite_line = 0
        
        in_class = False
        class_name = ""
        
        for i, line in enumerate(lines, 1):
            # 检查 suite 装饰器
            suite_match = self._suite_decorator.search(line)
            if suite_match:
                current_suite_name = suite_match.group(1)
                current_suite_line = i
                current_suite_tags = self._parse_tags(line)
                in_class = False
                
                suites.append(SuiteInfo(
                    name=current_suite_name,
                    file_path=file_path,
                    line_number=current_suite_line,
                    tags=current_suite_tags
                ))
            
            # 检查 class 定义
            class_match = self._test_class_pattern.search(line)
            if class_match and not line.strip().startswith('#'):
                class_name = class_match.group(1)
                in_class = True
                current_suite_name = class_name
                current_suite_line = i
                
                # 检查类是否有 suite 装饰器
                suite_match = self._suite_decorator.search(line)
                if suite_match:
                    current_suite_name = suite_match.group(1)
                    current_suite_tags = self._parse_tags(line)
                
                suites.append(SuiteInfo(
                    name=current_suite_name,
                    file_path=file_path,
                    line_number=current_suite_line,
                    tags=current_suite_tags
                ))
            
            # 检查测试方法
            method_match = self._test_method_pattern.search(line)
            if method_match and not line.strip().startswith('#'):
                method_name = method_match.group(1)
                
                # 获取测试名称
                test_name = method_name
                test_match = self._test_decorator.search(line)
                if test_match:
                    test_name = test_match.group(1)
                
                # 获取标签
                tags = self._parse_tags(line) | current_suite_tags
                
                # 获取优先级
                priority = self._parse_priority(line)
                
                # 检查是否跳过
                skip_match = self._skip_decorator.search(line)
                skip = bool(skip_match)
                skip_reason = skip_match.group(1) if skip_match and skip_match.group(1) else ""
                
                test_info = TestInfo(
                    name=test_name,
                    suite_name=current_suite_name,
                    file_path=file_path,
                    line_number=i,
                    priority=priority,
                    tags=tags,
                    skip=skip,
                    skip_reason=skip_reason
                )
                
                all_tests.append(test_info)
        
        return suites, all_tests
    
    def _parse_tags(self, line: str) -> Set[str]:
        """解析标签"""
        tags_match = self._tags_decorator.search(line)
        if tags_match:
            tags_str = tags_match.group(1)
            # 解析标签列表
            tags = re.findall(r'["\']([^"\']+)["\']', tags_str)
            return set(tags)
        return set()
    
    def _parse_priority(self, line: str) -> TestPriority:
        """解析优先级"""
        priority_match = self._priority_decorator.search(line)
        if priority_match:
            priority_name = priority_match.group(1).upper()
            try:
                return TestPriority[priority_name]
            except KeyError:
                pass
        return TestPriority.NORMAL


def priority(level: int):
    """优先级装饰器"""
    def decorator(func):
        func._priority = level
        return func
    return decorator


def tags(*tag_list: str):
    """标签装饰器"""
    def decorator(func):
        func._tags = set(tag_list)
        return func
    return decorator


def skip(reason: str = ""):
    """跳过测试装饰器"""
    def decorator(func):
        func._skip = True
        func._skip_reason = reason
        return func
    return decorator


# 便捷函数
def discover_tests(
    root_dir: str = ".",
    pattern: str = "test_*.py",
    recursive: bool = True,
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    priorities: Optional[List[TestPriority]] = None
) -> List[TestInfo]:
    """发现测试的便捷函数
    
    Args:
        root_dir: 根目录
        pattern: 文件模式
        recursive: 是否递归
        include_tags: 包含的标签
        exclude_tags: 排除的标签
        priorities: 优先级过滤
    
    Returns:
        测试信息列表
    """
    discoverer = TestDiscoverer(root_dir)
    
    result = discoverer.discover(pattern, recursive)
    
    test_filter = TestFilter()
    if include_tags:
        for tag in include_tags:
            test_filter.add_include_tag(tag)
    if exclude_tags:
        for tag in exclude_tags:
            test_filter.add_exclude_tag(tag)
    if priorities:
        test_filter.set_priorities(priorities)
    
    return [t for t in result.tests if test_filter.match(t)]


def discover_suites(root_dir: str = ".", pattern: str = "test_*.py") -> List[SuiteInfo]:
    """发现测试套件
    
    Args:
        root_dir: 根目录
        pattern: 文件模式
    
    Returns:
        测试套件列表
    """
    discoverer = TestDiscoverer(root_dir)
    result = discoverer.discover(pattern)
    return result.suites


__all__ = [
    'TestInfo', 'SuiteInfo', 'TestFilter', 'TestDiscoverer',
    'TestPriority', 'DiscoveryResult',
    'priority', 'tags', 'skip',
    'discover_tests', 'discover_suites'
]
