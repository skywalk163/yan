"""
言语言性能分析器 - Profiler
提供代码执行性能分析功能
"""

import time
import sys
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class ProfileMode(Enum):
    """性能分析模式"""
    TIME = "time"           # 时间分析
    MEMORY = "memory"       # 内存分析
    CALLS = "calls"         # 调用次数分析
    FULL = "full"           # 完整分析


class ProfileLevel(Enum):
    """分析级别"""
    FUNCTION = "function"   # 函数级分析
    LINE = "line"           # 行级分析
    BLOCK = "block"         # 代码块级分析


@dataclass
class FunctionStats:
    """函数统计信息"""
    name: str
    calls: int = 0
    total_time: float = 0.0
    self_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    children: Dict[str, 'FunctionStats'] = field(default_factory=dict)
    file: str = ""
    line: int = 0
    
    def update(self, duration: float):
        """更新统计信息"""
        self.calls += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        if self.calls > 0:
            self.avg_time = self.total_time / self.calls
    
    def to_dict(self):
        """转换为字典"""
        return {
            "name": self.name,
            "calls": self.calls,
            "total_time": self.total_time,
            "self_time": self.self_time,
            "min_time": self.min_time,
            "max_time": self.max_time,
            "avg_time": self.avg_time,
            "file": self.file,
            "line": self.line,
            "children": {k: v.to_dict() for k, v in self.children.items()}
        }


@dataclass
class LineStats:
    """行统计信息"""
    line: int
    hits: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    
    def update(self, duration: float):
        """更新统计信息"""
        self.hits += 1
        self.total_time += duration
        if self.hits > 0:
            self.avg_time = self.total_time / self.hits
    
    def to_dict(self):
        """转换为字典"""
        return {
            "line": self.line,
            "hits": self.hits,
            "total_time": self.total_time,
            "avg_time": self.avg_time
        }


@dataclass
class ProfileReport:
    """性能分析报告"""
    total_time: float = 0.0
    function_stats: Dict[str, FunctionStats] = field(default_factory=dict)
    line_stats: Dict[str, Dict[int, LineStats]] = field(default_factory=dict)
    call_stack: List[str] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    
    def to_dict(self):
        """转换为字典"""
        return {
            "total_time": self.total_time,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "function_stats": {k: v.to_dict() for k, v in self.function_stats.items()},
            "line_stats": {
                file: {str(line): stats.to_dict() for line, stats in lines.items()}
                for file, lines in self.line_stats.items()
            },
            "call_stack": self.call_stack
        }


class YanProfiler:
    """言语言性能分析器"""
    
    def __init__(self, mode: ProfileMode = ProfileMode.TIME, level: ProfileLevel = ProfileLevel.FUNCTION):
        self.mode = mode
        self.level = level
        self.report = ProfileReport()
        self._is_running = False
        self._current_function = None
        self._start_times: Dict[str, float] = {}
        self._function_stack: List[str] = []
        self._line_timers: Dict[str, float] = {}
        
        # 用于计算 self_time
        self._child_time: Dict[str, float] = defaultdict(float)
    
    def start(self):
        """开始性能分析"""
        self._is_running = True
        self.report.start_time = time.perf_counter()
        self.report.function_stats.clear()
        self.report.line_stats.clear()
        self.report.call_stack.clear()
    
    def stop(self):
        """停止性能分析"""
        self._is_running = False
        self.report.end_time = time.perf_counter()
        self.report.total_time = self.report.end_time - self.report.start_time
        
        # 计算 self_time
        for func_name, stats in self.report.function_stats.items():
            stats.self_time = stats.total_time - self._child_time[func_name]
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._is_running
    
    def enter_function(self, func_name: str, file: str = "", line: int = 0):
        """进入函数"""
        if not self._is_running:
            return
        
        self._function_stack.append(func_name)
        self._current_function = func_name
        
        # 记录调用栈
        self.report.call_stack.append(f"-> {func_name}")
        
        # 记录开始时间
        self._start_times[func_name] = time.perf_counter()
        
        # 初始化函数统计
        if func_name not in self.report.function_stats:
            self.report.function_stats[func_name] = FunctionStats(
                name=func_name,
                file=file,
                line=line
            )
    
    def exit_function(self, func_name: str):
        """退出函数"""
        if not self._is_running:
            return
        
        if func_name in self._start_times:
            duration = time.perf_counter() - self._start_times[func_name]
            
            # 更新函数统计
            if func_name in self.report.function_stats:
                self.report.function_stats[func_name].update(duration)
            
            # 更新父函数的子时间
            if len(self._function_stack) > 1:
                parent_func = self._function_stack[-2]
                self._child_time[parent_func] += duration
            
            del self._start_times[func_name]
        
        if self._function_stack and self._function_stack[-1] == func_name:
            self._function_stack.pop()
        
        if self._function_stack:
            self._current_function = self._function_stack[-1]
        else:
            self._current_function = None
    
    def record_line(self, file: str, line: int, duration: float = 0.0):
        """记录行执行"""
        if not self._is_running or self.level != ProfileLevel.LINE:
            return
        
        if file not in self.report.line_stats:
            self.report.line_stats[file] = {}
        
        if line not in self.report.line_stats[file]:
            self.report.line_stats[file][line] = LineStats(line=line)
        
        self.report.line_stats[file][line].update(duration)
    
    def record_block(self, block_name: str, duration: float):
        """记录代码块执行时间"""
        if not self._is_running:
            return
        
        # 代码块作为虚拟函数处理
        if block_name not in self.report.function_stats:
            self.report.function_stats[block_name] = FunctionStats(name=block_name)
        
        self.report.function_stats[block_name].update(duration)
    
    def get_report(self) -> ProfileReport:
        """获取分析报告"""
        return self.report
    
    def get_hotspots(self, limit: int = 10) -> List[FunctionStats]:
        """获取热点函数（按总时间排序）"""
        stats_list = sorted(
            self.report.function_stats.values(),
            key=lambda x: x.total_time,
            reverse=True
        )
        return stats_list[:limit]
    
    def get_most_called(self, limit: int = 10) -> List[FunctionStats]:
        """获取调用次数最多的函数"""
        stats_list = sorted(
            self.report.function_stats.values(),
            key=lambda x: x.calls,
            reverse=True
        )
        return stats_list[:limit]
    
    def format_report(self, detailed: bool = False) -> str:
        """格式化报告为文本"""
        lines = []
        lines.append("=" * 60)
        lines.append("言语言性能分析报告")
        lines.append("=" * 60)
        lines.append(f"分析模式: {self.mode.value}")
        lines.append(f"分析级别: {self.level.value}")
        lines.append(f"总执行时间: {self.report.total_time:.4f} 秒")
        lines.append(f"分析函数数: {len(self.report.function_stats)}")
        lines.append("-" * 60)
        
        # 热点函数
        lines.append("\n【热点函数 TOP 10】")
        lines.append("-" * 60)
        lines.append(f"{'函数名':<30} {'调用次数':>10} {'总时间':>12} {'平均时间':>12}")
        lines.append("-" * 60)
        
        for stats in self.get_hotspots(10):
            lines.append(f"{stats.name:<30} {stats.calls:>10} {stats.total_time:>12.4f} {stats.avg_time:>12.6f}")
        
        # 调用次数最多
        if detailed:
            lines.append("\n【调用次数最多 TOP 10】")
            lines.append("-" * 60)
            lines.append(f"{'函数名':<30} {'调用次数':>10} {'总时间':>12}")
            lines.append("-" * 60)
            
            for stats in self.get_most_called(10):
                lines.append(f"{stats.name:<30} {stats.calls:>10} {stats.total_time:>12.4f}")
        
        # 行级统计
        if self.level == ProfileLevel.LINE and self.report.line_stats:
            lines.append("\n【行级统计】")
            lines.append("-" * 60)
            
            for file, line_stats in self.report.line_stats.items():
                lines.append(f"\n文件: {file}")
                lines.append(f"{'行号':>6} {'命中次数':>10} {'总时间':>12}")
                lines.append("-" * 30)
                
                sorted_lines = sorted(line_stats.values(), key=lambda x: x.total_time, reverse=True)
                for stats in sorted_lines[:10]:
                    lines.append(f"{stats.line:>6} {stats.hits:>10} {stats.total_time:>12.4f}")
        
        lines.append("\n" + "=" * 60)
        lines.append("分析完成")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def export_report(self, filename: str, format_type: str = "text"):
        """导出报告到文件"""
        if format_type == "json":
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.report.to_dict(), f, ensure_ascii=False, indent=2)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.format_report(detailed=True))


class ProfilerDecorator:
    """性能分析装饰器"""
    
    def __init__(self, profiler: 'YanProfiler'):
        self.profiler = profiler
    
    def profile(self, func: Callable) -> Callable:
        """装饰器：分析函数性能"""
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            if self.profiler.is_running():
                self.profiler.enter_function(func_name)
            
            try:
                return func(*args, **kwargs)
            finally:
                if self.profiler.is_running():
                    self.profiler.exit_function(func_name)
        
        return wrapper


class ProfilerContextManager:
    """性能分析上下文管理器"""
    
    def __init__(self, profiler: 'YanProfiler', name: str = ""):
        self.profiler = profiler
        self.name = name or "block"
    
    def __enter__(self):
        self.profiler.enter_function(self.name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.exit_function(self.name)


def profile_function(profiler: YanProfiler):
    """装饰器工厂：创建性能分析装饰器"""
    decorator = ProfilerDecorator(profiler)
    return decorator.profile


def profile_block(profiler: YanProfiler, name: str = ""):
    """创建性能分析上下文管理器"""
    return ProfilerContextManager(profiler, name)


# 全局分析器实例
_global_profiler = YanProfiler()


def get_global_profiler() -> YanProfiler:
    """获取全局分析器"""
    return _global_profiler


def start_profiling(mode: ProfileMode = ProfileMode.TIME, level: ProfileLevel = ProfileLevel.FUNCTION):
    """启动全局性能分析"""
    global _global_profiler
    _global_profiler = YanProfiler(mode, level)
    _global_profiler.start()


def stop_profiling() -> ProfileReport:
    """停止全局性能分析并返回报告"""
    _global_profiler.stop()
    return _global_profiler.get_report()


def print_profiling_report(detailed: bool = False):
    """打印性能分析报告"""
    print(_global_profiler.format_report(detailed))


# 示例使用
if __name__ == "__main__":
    profiler = YanProfiler(mode=ProfileMode.FULL, level=ProfileLevel.FUNCTION)
    profiler.start()
    
    # 模拟函数调用
    profiler.enter_function("主函数", "test.yan", 1)
    
    profiler.enter_function("计算函数", "test.yan", 5)
    time.sleep(0.1)
    profiler.exit_function("计算函数")
    
    profiler.enter_function("处理函数", "test.yan", 10)
    profiler.enter_function("子处理", "test.yan", 12)
    time.sleep(0.05)
    profiler.exit_function("子处理")
    time.sleep(0.08)
    profiler.exit_function("处理函数")
    
    profiler.exit_function("主函数")
    
    profiler.stop()
    
    print(profiler.format_report(detailed=True))
    
    # 导出报告
    profiler.export_report("profile_report.txt")
    profiler.export_report("profile_report.json", format_type="json")