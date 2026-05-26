"""
性能分析器测试
"""

import pytest
import time
from yan.profiler import (
    YanProfiler,
    ProfileMode,
    ProfileLevel,
    FunctionStats,
    LineStats,
    ProfileReport,
    ProfilerDecorator,
    ProfilerContextManager,
    profile_function,
    profile_block,
    get_global_profiler,
    start_profiling,
    stop_profiling,
    print_profiling_report
)


class TestFunctionStats:
    """函数统计信息测试"""
    
    def test_update_stats(self):
        """测试更新统计信息"""
        stats = FunctionStats(name="test_func")
        stats.update(0.1)
        stats.update(0.2)
        stats.update(0.3)
        
        assert stats.calls == 3
        assert stats.total_time == pytest.approx(0.6, abs=0.001)
        assert stats.min_time == pytest.approx(0.1, abs=0.001)
        assert stats.max_time == pytest.approx(0.3, abs=0.001)
        assert stats.avg_time == pytest.approx(0.2, abs=0.001)
    
    def test_to_dict(self):
        """测试转换为字典"""
        stats = FunctionStats(name="test_func", file="test.yan", line=10)
        stats.update(0.1)
        
        result = stats.to_dict()
        assert result["name"] == "test_func"
        assert result["calls"] == 1
        assert result["file"] == "test.yan"
        assert result["line"] == 10


class TestLineStats:
    """行统计信息测试"""
    
    def test_update_line_stats(self):
        """测试更新行统计"""
        stats = LineStats(line=10)
        stats.update(0.01)
        stats.update(0.02)
        
        assert stats.hits == 2
        assert stats.total_time == pytest.approx(0.03, abs=0.001)
        assert stats.avg_time == pytest.approx(0.015, abs=0.001)
    
    def test_to_dict(self):
        """测试转换为字典"""
        stats = LineStats(line=5)
        stats.update(0.05)
        
        result = stats.to_dict()
        assert result["line"] == 5
        assert result["hits"] == 1


class TestYanProfilerBasic:
    """性能分析器基础功能测试"""
    
    def test_profiler_start_stop(self):
        """测试分析器启动和停止"""
        profiler = YanProfiler()
        profiler.start()
        
        assert profiler.is_running() is True
        
        profiler.stop()
        assert profiler.is_running() is False
    
    def test_enter_exit_function(self):
        """测试函数进入和退出"""
        profiler = YanProfiler()
        profiler.start()
        
        profiler.enter_function("my_func", "test.yan", 10)
        time.sleep(0.01)
        profiler.exit_function("my_func")
        
        profiler.stop()
        
        stats = profiler.report.function_stats.get("my_func")
        assert stats is not None
        assert stats.calls == 1
        assert stats.total_time > 0
        assert stats.file == "test.yan"
        assert stats.line == 10
    
    def test_function_stack(self):
        """测试函数调用栈"""
        profiler = YanProfiler()
        profiler.start()
        
        profiler.enter_function("outer")
        profiler.enter_function("inner")
        time.sleep(0.01)
        profiler.exit_function("inner")
        profiler.exit_function("outer")
        
        profiler.stop()
        
        assert "outer" in profiler.report.function_stats
        assert "inner" in profiler.report.function_stats
        
        outer_stats = profiler.report.function_stats["outer"]
        inner_stats = profiler.report.function_stats["inner"]
        
        # 外部函数的总时间应大于内部函数
        assert outer_stats.total_time >= inner_stats.total_time
    
    def test_self_time_calculation(self):
        """测试自时间计算"""
        profiler = YanProfiler()
        profiler.start()
        
        profiler.enter_function("parent")
        time.sleep(0.02)
        
        profiler.enter_function("child")
        time.sleep(0.01)
        profiler.exit_function("child")
        
        profiler.exit_function("parent")
        
        profiler.stop()
        
        parent_stats = profiler.report.function_stats["parent"]
        child_stats = profiler.report.function_stats["child"]
        
        # 父函数的自时间 = 总时间 - 子函数时间
        expected_self_time = parent_stats.total_time - child_stats.total_time
        assert parent_stats.self_time == pytest.approx(expected_self_time, abs=0.001)


class TestYanProfilerMode:
    """性能分析器模式测试"""
    
    def test_time_mode(self):
        """测试时间分析模式"""
        profiler = YanProfiler(mode=ProfileMode.TIME)
        profiler.start()
        
        profiler.enter_function("test")
        time.sleep(0.01)
        profiler.exit_function("test")
        
        profiler.stop()
        
        stats = profiler.report.function_stats["test"]
        assert stats.total_time > 0
    
    def test_calls_mode(self):
        """测试调用次数分析模式"""
        profiler = YanProfiler(mode=ProfileMode.CALLS)
        profiler.start()
        
        for _ in range(5):
            profiler.enter_function("counted")
            profiler.exit_function("counted")
        
        profiler.stop()
        
        stats = profiler.report.function_stats["counted"]
        assert stats.calls == 5


class TestYanProfilerLevel:
    """性能分析器级别测试"""
    
    def test_function_level(self):
        """测试函数级分析"""
        profiler = YanProfiler(level=ProfileLevel.FUNCTION)
        profiler.start()
        
        profiler.enter_function("func1")
        time.sleep(0.01)
        profiler.exit_function("func1")
        
        profiler.stop()
        
        assert len(profiler.report.function_stats) == 1
        assert len(profiler.report.line_stats) == 0
    
    def test_line_level(self):
        """测试行级分析"""
        profiler = YanProfiler(level=ProfileLevel.LINE)
        profiler.start()
        
        profiler.record_line("test.yan", 10, 0.001)
        profiler.record_line("test.yan", 10, 0.002)
        profiler.record_line("test.yan", 15, 0.003)
        
        profiler.stop()
        
        assert "test.yan" in profiler.report.line_stats
        lines = profiler.report.line_stats["test.yan"]
        assert 10 in lines
        assert lines[10].hits == 2


class TestHotspots:
    """热点分析测试"""
    
    def test_get_hotspots(self):
        """测试获取热点函数"""
        profiler = YanProfiler()
        profiler.start()
        
        profiler.enter_function("fast_func")
        time.sleep(0.01)
        profiler.exit_function("fast_func")
        
        profiler.enter_function("slow_func")
        time.sleep(0.05)
        profiler.exit_function("slow_func")
        
        profiler.enter_function("medium_func")
        time.sleep(0.03)
        profiler.exit_function("medium_func")
        
        profiler.stop()
        
        hotspots = profiler.get_hotspots(2)
        assert len(hotspots) == 2
        assert hotspots[0].name == "slow_func"
        assert hotspots[1].name == "medium_func"
    
    def test_get_most_called(self):
        """测试获取调用次数最多的函数"""
        profiler = YanProfiler()
        profiler.start()
        
        for _ in range(10):
            profiler.enter_function("often_called")
            profiler.exit_function("often_called")
        
        for _ in range(5):
            profiler.enter_function("sometimes_called")
            profiler.exit_function("sometimes_called")
        
        profiler.stop()
        
        most_called = profiler.get_most_called(2)
        assert most_called[0].name == "often_called"
        assert most_called[0].calls == 10


class TestReportFormatting:
    """报告格式化测试"""
    
    def test_format_report(self):
        """测试格式化报告"""
        profiler = YanProfiler()
        profiler.start()
        
        profiler.enter_function("test_func")
        time.sleep(0.01)
        profiler.exit_function("test_func")
        
        profiler.stop()
        
        report = profiler.format_report()
        assert "言语言性能分析报告" in report
        assert "test_func" in report
        assert "调用次数" in report
    
    def test_export_report_text(self):
        """测试导出文本报告"""
        profiler = YanProfiler()
        profiler.start()
        
        profiler.enter_function("export_test")
        time.sleep(0.01)
        profiler.exit_function("export_test")
        
        profiler.stop()
        
        profiler.export_report("test_profile_report.txt")
        
        import os
        assert os.path.exists("test_profile_report.txt")
        os.remove("test_profile_report.txt")
    
    def test_export_report_json(self):
        """测试导出JSON报告"""
        profiler = YanProfiler()
        profiler.start()
        
        profiler.enter_function("json_test")
        time.sleep(0.01)
        profiler.exit_function("json_test")
        
        profiler.stop()
        
        profiler.export_report("test_profile_report.json", format_type="json")
        
        import os
        assert os.path.exists("test_profile_report.json")
        os.remove("test_profile_report.json")


class TestDecoratorAndContextManager:
    """装饰器和上下文管理器测试"""
    
    def test_decorator(self):
        """测试装饰器"""
        profiler = YanProfiler()
        profiler.start()
        
        @profile_function(profiler)
        def my_function():
            time.sleep(0.01)
        
        my_function()
        my_function()
        
        profiler.stop()
        
        stats = profiler.report.function_stats.get("my_function")
        assert stats is not None
        assert stats.calls == 2
    
    def test_context_manager(self):
        """测试上下文管理器"""
        profiler = YanProfiler()
        profiler.start()
        
        with profile_block(profiler, "my_block"):
            time.sleep(0.01)
        
        profiler.stop()
        
        stats = profiler.report.function_stats.get("my_block")
        assert stats is not None
        assert stats.calls == 1


class TestGlobalProfiler:
    """全局分析器测试"""
    
    def test_global_profiler(self):
        """测试全局分析器"""
        profiler = get_global_profiler()
        assert isinstance(profiler, YanProfiler)
    
    def test_start_stop_profiling(self):
        """测试启动和停止全局分析"""
        start_profiling(ProfileMode.TIME, ProfileLevel.FUNCTION)
        
        profiler = get_global_profiler()
        assert profiler.is_running() is True
        
        report = stop_profiling()
        assert isinstance(report, ProfileReport)
        assert profiler.is_running() is False


class TestProfileReport:
    """分析报告测试"""
    
    def test_report_to_dict(self):
        """测试报告转换为字典"""
        report = ProfileReport()
        report.total_time = 1.5
        report.start_time = 100.0
        report.end_time = 101.5
        
        result = report.to_dict()
        assert result["total_time"] == 1.5
        assert result["start_time"] == 100.0
        assert result["end_time"] == 101.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])