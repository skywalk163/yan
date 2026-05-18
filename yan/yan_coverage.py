#!/usr/bin/env python3
"""
言语言代码覆盖率统计

支持行覆盖率、分支覆盖率、函数覆盖率
"""

import os
import sys
import re
import ast
import json
import traceback
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class LineCoverage:
    """行覆盖率"""
    total_lines: int = 0
    covered_lines: int = 0
    uncovered_lines: List[int] = field(default_factory=list)
    
    @property
    def percentage(self) -> float:
        if self.total_lines == 0:
            return 100.0
        return (self.covered_lines / self.total_lines) * 100


@dataclass
class BranchCoverage:
    """分支覆盖率"""
    total_branches: int = 0
    covered_branches: int = 0
    
    @property
    def percentage(self) -> float:
        if self.total_branches == 0:
            return 100.0
        return (self.covered_branches / self.total_branches) * 100


@dataclass
class FunctionCoverage:
    """函数覆盖率"""
    total_functions: int = 0
    covered_functions: int = 0
    uncovered_functions: List[str] = field(default_factory=list)
    
    @property
    def percentage(self) -> float:
        if self.total_functions == 0:
            return 100.0
        return (self.covered_functions / self.total_functions) * 100


@dataclass
class FileCoverage:
    """文件覆盖率"""
    file_path: str
    line_coverage: LineCoverage = field(default_factory=LineCoverage)
    branch_coverage: BranchCoverage = field(default_factory=BranchCoverage)
    function_coverage: FunctionCoverage = field(default_factory=FunctionCoverage)
    
    @property
    def line_percentage(self) -> float:
        return self.line_coverage.percentage
    
    @property
    def overall_percentage(self) -> float:
        """综合覆盖率（行覆盖率权重0.7，函数覆盖率0.3）"""
        return self.line_percentage * 0.7 + self.function_coverage.percentage * 0.3


@dataclass
class CoverageReport:
    """覆盖率报告"""
    total_files: int = 0
    total_lines: int = 0
    covered_lines: int = 0
    total_functions: int = 0
    covered_functions: int = 0
    file_coverages: Dict[str, FileCoverage] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def line_percentage(self) -> float:
        if self.total_lines == 0:
            return 100.0
        return (self.covered_lines / self.total_lines) * 100
    
    @property
    def function_percentage(self) -> float:
        if self.total_functions == 0:
            return 100.0
        return (self.covered_functions / self.total_functions) * 100
    
    @property
    def overall_percentage(self) -> float:
        return self.line_percentage * 0.7 + self.function_percentage * 0.3
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_files': self.total_files,
            'total_lines': self.total_lines,
            'covered_lines': self.covered_lines,
            'line_percentage': self.line_percentage,
            'total_functions': self.total_functions,
            'covered_functions': self.covered_functions,
            'function_percentage': self.function_percentage,
            'overall_percentage': self.overall_percentage,
            'timestamp': self.timestamp,
            'files': {
                path: {
                    'line_percentage': fc.line_percentage,
                    'function_percentage': fc.function_percentage,
                    'overall_percentage': fc.overall_percentage,
                    'uncovered_lines': fc.line_coverage.uncovered_lines
                }
                for path, fc in self.file_coverages.items()
            }
        }


class CoverageTracker:
    """覆盖率追踪器"""
    
    def __init__(self):
        self._traced_files: Set[str] = set()
        self._executed_lines: Dict[str, Set[int]] = defaultdict(set)
        self._executed_functions: Dict[str, Set[str]] = defaultdict(set)
        self._branch_conditions: Dict[str, Dict[int, Set[bool]]] = defaultdict(
            lambda: defaultdict(set)
        )
    
    def trace_line(self, filename: str, line_number: int):
        """追踪代码行执行"""
        self._executed_lines[filename].add(line_number)
    
    def trace_function(self, filename: str, function_name: str):
        """追踪函数执行"""
        self._executed_functions[filename].add(function_name)
    
    def trace_branch(self, filename: str, line_number: int, condition: bool):
        """追踪分支执行"""
        self._branch_conditions[filename][line_number].add(condition)
    
    def get_executed_lines(self, filename: str) -> Set[int]:
        """获取文件执行的行"""
        return self._executed_lines.get(filename, set())
    
    def get_executed_functions(self, filename: str) -> Set[str]:
        """获取文件执行的函数"""
        return self._executed_functions.get(filename, set())
    
    def save(self, filepath: str):
        """保存覆盖率数据"""
        data = {
            'executed_lines': {
                k: list(v) for k, v in self._executed_lines.items()
            },
            'executed_functions': {
                k: list(v) for k, v in self._executed_functions.items()
            },
            'branch_conditions': {
                k: {str(lk): list(lv) for lk, lv in v.items()}
                for k, v in self._branch_conditions.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, filepath: str):
        """加载覆盖率数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._executed_lines = {
            k: set(v) for k, v in data.get('executed_lines', {}).items()
        }
        self._executed_functions = {
            k: set(v) for k, v in data.get('executed_functions', {}).items()
        }
        self._branch_conditions = defaultdict(
            lambda: defaultdict(set),
            {
                k: {int(lk): set(lv) for lk, lv in v.items()}
                for k, v in data.get('branch_conditions', {}).items()
            }
        )


class CoverageAnalyzer:
    """覆盖率分析器"""
    
    def __init__(self):
        self.tracker = CoverageTracker()
    
    def analyze_file(self, filepath: str) -> FileCoverage:
        """分析单个文件的覆盖率"""
        if not os.path.exists(filepath):
            return FileCoverage(file_path=filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()
        
        # 解析 AST
        try:
            tree = ast.parse(''.join(source_lines))
        except SyntaxError:
            return FileCoverage(file_path=filepath)
        
        # 获取所有可执行行
        executable_lines = self._get_executable_lines(tree, source_lines)
        
        # 获取所有函数
        all_functions = self._get_all_functions(tree)
        
        # 计算行覆盖率
        executed_lines = self.tracker.get_executed_lines(filepath)
        uncovered = [line for line in executable_lines if line not in executed_lines]
        
        line_coverage = LineCoverage(
            total_lines=len(executable_lines),
            covered_lines=len(executable_lines) - len(uncovered),
            uncovered_lines=uncovered
        )
        
        # 计算函数覆盖率
        executed_functions = self.tracker.get_executed_functions(filepath)
        uncovered_funcs = [f for f in all_functions if f not in executed_functions]
        
        function_coverage = FunctionCoverage(
            total_functions=len(all_functions),
            covered_functions=len(all_functions) - len(uncovered_funcs),
            uncovered_functions=uncovered_funcs
        )
        
        # 计算分支覆盖率
        branch_coverage = self._calculate_branch_coverage(filepath, tree)
        
        return FileCoverage(
            file_path=filepath,
            line_coverage=line_coverage,
            branch_coverage=branch_coverage,
            function_coverage=function_coverage
        )
    
    def analyze_directory(self, directory: str, pattern: str = "*.py") -> CoverageReport:
        """分析目录的覆盖率"""
        report = CoverageReport()
        
        for filepath in Path(directory).rglob(pattern):
            if self._should_exclude(str(filepath)):
                continue
            
            file_coverage = self.analyze_file(str(filepath))
            report.file_coverages[str(filepath)] = file_coverage
            
            report.total_files += 1
            report.total_lines += file_coverage.line_coverage.total_lines
            report.covered_lines += file_coverage.line_coverage.covered_lines
            report.total_functions += file_coverage.function_coverage.total_functions
            report.covered_functions += file_coverage.function_coverage.covered_functions
        
        return report
    
    def _get_executable_lines(self, tree: ast.AST, source_lines: List[str]) -> List[int]:
        """获取所有可执行行"""
        executable = set()
        
        for node in ast.walk(tree):
            if hasattr(node, 'lineno'):
                line_no = node.lineno
                # 排除空行和注释行
                if 0 < line_no <= len(source_lines):
                    line = source_lines[line_no - 1].strip()
                    if line and not line.startswith('#'):
                        executable.add(line_no)
        
        return sorted(list(executable))
    
    def _get_all_functions(self, tree: ast.AST) -> List[str]:
        """获取所有函数名"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith('_') or node.name == '__init__':
                    functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        full_name = f"{node.name}.{item.name}"
                        if not item.name.startswith('_') or item.name == '__init__':
                            functions.append(full_name)
        
        return functions
    
    def _calculate_branch_coverage(self, filepath: str, tree: ast.AST) -> BranchCoverage:
        """计算分支覆盖率"""
        total_branches = 0
        covered_branches = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                total_branches += 2  # if and else/elif
                
                # 检查条件是否被追踪
                conditions = self.tracker._branch_conditions.get(filepath, {}).get(
                    node.lineno, set()
                )
                if True in conditions:
                    covered_branches += 1
                if False in conditions:
                    covered_branches += 1
            elif isinstance(node, ast.For):
                total_branches += 1
                if self.tracker._branch_conditions.get(filepath, {}).get(node.lineno):
                    covered_branches += 1
            elif isinstance(node, ast.While):
                total_branches += 1
                if self.tracker._branch_conditions.get(filepath, {}).get(node.lineno):
                    covered_branches += 1
        
        return BranchCoverage(
            total_branches=total_branches,
            covered_branches=covered_branches
        )
    
    def _should_exclude(self, filepath: str) -> bool:
        """检查是否应该排除文件"""
        exclude_patterns = [
            '__pycache__', '.git', 'venv', 'env', 'node_modules',
            '.venv', '.env', 'build', 'dist', '.egg-info'
        ]
        
        parts = Path(filepath).parts
        return any(pattern in parts for pattern in exclude_patterns)


class CoverageRunner:
    """覆盖率运行器"""
    
    def __init__(self):
        self.analyzer = CoverageAnalyzer()
        self.tracker = self.analyzer.tracker
    
    def run_with_coverage(
        self,
        test_module: str,
        source_files: List[str]
    ) -> Tuple[Any, CoverageReport]:
        """运行测试并收集覆盖率
        
        Args:
            test_module: 测试模块名
            source_files: 源代码文件列表
        
        Returns:
            (测试结果, 覆盖率报告)
        """
        # 安装追踪器
        self._install_tracer()
        
        # 运行测试
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover(test_module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # 卸载追踪器
        self._uninstall_tracer()
        
        # 生成覆盖率报告
        report = CoverageReport()
        for source_file in source_files:
            file_coverage = self.analyzer.analyze_file(source_file)
            report.file_coverages[source_file] = file_coverage
            report.total_files += 1
            report.total_lines += file_coverage.line_coverage.total_lines
            report.covered_lines += file_coverage.line_coverage.covered_lines
            report.total_functions += file_coverage.function_coverage.total_functions
            report.covered_functions += file_coverage.function_coverage.covered_functions
        
        return result, report
    
    def _install_tracer(self):
        """安装追踪器"""
        self._old_trace = sys.gettrace()
        
        def tracer(frame, event, arg):
            if event == 'line':
                filename = frame.f_code.co_filename
                lineno = frame.f_lineno
                self.tracker.trace_line(filename, lineno)
                
                # 追踪函数调用
                if arg is not None:
                    func_name = frame.f_code.co_name
                    if not func_name.startswith('__'):
                        self.tracker.trace_function(filename, func_name)
            
            return tracer
        
        sys.settrace(tracer)
    
    def _uninstall_tracer(self):
        """卸载追踪器"""
        sys.settrace(self._old_trace)


def generate_coverage_report(
    directory: str,
    output_file: Optional[str] = None,
    format: str = 'text'
) -> CoverageReport:
    """生成覆盖率报告
    
    Args:
        directory: 源代码目录
        output_file: 输出文件路径
        format: 输出格式 ('text', 'json', 'html')
    
    Returns:
        覆盖率报告
    """
    analyzer = CoverageAnalyzer()
    report = analyzer.analyze_directory(directory)
    
    if format == 'json':
        output = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
    elif format == 'html':
        output = _generate_html_report(report)
    else:
        output = _format_text_report(report)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
    
    return report


def _format_text_report(report: CoverageReport) -> str:
    """格式化文本报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("言语言代码覆盖率报告")
    lines.append("=" * 60)
    lines.append(f"生成时间: {report.timestamp}")
    lines.append("")
    lines.append(f"总文件数: {report.total_files}")
    lines.append(f"总代码行数: {report.total_lines}")
    lines.append(f"已覆盖行数: {report.covered_lines}")
    lines.append(f"行覆盖率: {report.line_percentage:.2f}%")
    lines.append("")
    lines.append(f"总函数数: {report.total_functions}")
    lines.append(f"已覆盖函数数: {report.covered_functions}")
    lines.append(f"函数覆盖率: {report.function_percentage:.2f}%")
    lines.append("")
    lines.append(f"综合覆盖率: {report.overall_percentage:.2f}%")
    lines.append("")
    lines.append("-" * 60)
    lines.append("文件覆盖率详情")
    lines.append("-" * 60)
    
    for filepath, fc in sorted(report.file_coverages.items()):
        lines.append(f"\n{filepath}")
        lines.append(f"  行覆盖: {fc.line_percentage:.1f}% ({fc.line_coverage.covered_lines}/{fc.line_coverage.total_lines})")
        lines.append(f"  函数覆盖: {fc.function_percentage:.1f}% ({fc.function_coverage.covered_functions}/{fc.function_coverage.total_functions})")
        
        if fc.line_coverage.uncovered_lines:
            lines.append(f"  未覆盖行: {fc.line_coverage.uncovered_lines[:10]}{'...' if len(fc.line_coverage.uncovered_lines) > 10 else ''}")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def _generate_html_report(report: CoverageReport) -> str:
    """生成HTML报告"""
    total_percentage = report.overall_percentage
    color = _get_color_for_percentage(total_percentage)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>言语言代码覆盖率报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .header {{ background: {color}; color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }}
        .stat {{ background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat .number {{ font-size: 32px; font-weight: bold; color: #333; }}
        .stat .label {{ color: #666; margin-top: 8px; }}
        .coverage-bar {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .bar-container {{ background: #e0e0e0; border-radius: 10px; height: 30px; overflow: hidden; }}
        .bar {{ background: {color}; height: 100%; transition: width 0.3s; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }}
        .file-list {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }}
        .file-item {{ padding: 16px; border-bottom: 1px solid #eee; }}
        .file-item:last-child {{ border-bottom: none; }}
        .file-name {{ font-weight: 500; color: #333; }}
        .file-stats {{ display: flex; gap: 20px; margin-top: 8px; font-size: 14px; color: #666; }}
        .timestamp {{ color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>言语言代码覆盖率报告</h1>
        <p class="timestamp">生成时间: {report.timestamp}</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="number">{report.total_files}</div>
            <div class="label">文件数</div>
        </div>
        <div class="stat">
            <div class="number">{report.total_lines}</div>
            <div class="label">代码行数</div>
        </div>
        <div class="stat">
            <div class="number">{report.total_functions}</div>
            <div class="label">函数数</div>
        </div>
        <div class="stat">
            <div class="number">{report.function_percentage:.1f}%</div>
            <div class="label">函数覆盖率</div>
        </div>
    </div>
    
    <div class="coverage-bar">
        <h3>综合覆盖率: {total_percentage:.1f}%</h3>
        <div class="bar-container">
            <div class="bar" style="width: {total_percentage}%">{total_percentage:.1f}%</div>
        </div>
    </div>
    
    <div class="file-list">
        <h3 style="padding: 16px; margin: 0; border-bottom: 1px solid #eee;">文件详情</h3>
"""
    
    for filepath, fc in sorted(report.file_coverages.items()):
        file_color = _get_color_for_percentage(fc.line_percentage)
        html += f"""
        <div class="file-item">
            <div class="file-name">{filepath}</div>
            <div class="file-stats">
                <span>行覆盖: {fc.line_percentage:.1f}%</span>
                <span>函数覆盖: {fc.function_percentage:.1f}%</span>
            </div>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    return html


def _get_color_for_percentage(percentage: float) -> str:
    """根据覆盖率百分比获取颜色"""
    if percentage >= 80:
        return 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
    elif percentage >= 60:
        return 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
    else:
        return 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'


__all__ = [
    'LineCoverage', 'BranchCoverage', 'FunctionCoverage', 'FileCoverage', 'CoverageReport',
    'CoverageTracker', 'CoverageAnalyzer', 'CoverageRunner',
    'generate_coverage_report'
]
