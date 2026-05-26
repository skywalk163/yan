"""
调试器增强功能测试
"""

import pytest
from yan.debugger_enhanced import (
    YanDebuggerEnhanced,
    DebugState,
    StepMode,
    Breakpoint,
    WatchExpression,
    Frame,
    VariableInfo
)


class TestBreakpointManagement:
    """断点管理测试"""
    
    def test_set_breakpoint(self):
        debugger = YanDebuggerEnhanced()
        bp = debugger.set_breakpoint(10, "test.yan")
        
        assert bp.line == 10
        assert bp.file == "test.yan"
        assert bp.enabled is True
        assert bp.verified is True
    
    def test_set_breakpoint_with_condition(self):
        debugger = YanDebuggerEnhanced()
        bp = debugger.set_breakpoint(15, "test.yan", condition="x > 10")
        
        assert bp.condition == "x > 10"
    
    def test_set_breakpoint_with_hit_condition(self):
        debugger = YanDebuggerEnhanced()
        bp = debugger.set_breakpoint(20, "test.yan", hit_condition="hitCount > 5")
        
        assert bp.hit_condition == "hitCount > 5"
    
    def test_set_breakpoint_with_log_message(self):
        debugger = YanDebuggerEnhanced()
        bp = debugger.set_breakpoint(25, "test.yan", log_message="x = {x}")
        
        assert bp.log_message == "x = {x}"
    
    def test_get_breakpoint(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan")
        
        bp = debugger.get_breakpoint(10, "test.yan")
        assert bp is not None
        assert bp.line == 10
    
    def test_remove_breakpoint(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan")
        
        result = debugger.remove_breakpoint(10, "test.yan")
        assert result is True
        
        bp = debugger.get_breakpoint(10, "test.yan")
        assert bp is None
    
    def test_remove_nonexistent_breakpoint(self):
        debugger = YanDebuggerEnhanced()
        result = debugger.remove_breakpoint(999, "test.yan")
        assert result is False
    
    def test_toggle_breakpoint(self):
        debugger = YanDebuggerEnhanced()
        
        result = debugger.toggle_breakpoint(10, "test.yan")
        assert result is True
        
        bp = debugger.get_breakpoint(10, "test.yan")
        assert bp.enabled is True
        
        result = debugger.toggle_breakpoint(10, "test.yan")
        assert result is False
        
        bp = debugger.get_breakpoint(10, "test.yan")
        assert bp.enabled is False
    
    def test_clear_breakpoints(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan")
        debugger.set_breakpoint(20, "test.yan")
        
        assert len(debugger.get_breakpoints()) == 2
        
        debugger.clear_breakpoints()
        assert len(debugger.get_breakpoints()) == 0
    
    def test_should_break_basic(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan")
        
        bp = debugger.should_break(10, "test.yan", {})
        assert bp is not None
        assert bp.line == 10
    
    def test_should_break_disabled(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan")
        bp = debugger.get_breakpoint(10, "test.yan")
        bp.enabled = False
        
        result = debugger.should_break(10, "test.yan", {})
        assert result is None
    
    def test_should_break_condition_met(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan", condition="x > 5")
        
        # 条件满足
        bp = debugger.should_break(10, "test.yan", {"x": 10})
        assert bp is not None
    
    def test_should_break_condition_not_met(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan", condition="x > 5")
        
        # 条件不满足
        bp = debugger.should_break(10, "test.yan", {"x": 3})
        assert bp is None
    
    def test_should_break_hit_condition(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan", hit_condition="hitCount > 3")
        
        # 前3次不触发
        assert debugger.should_break(10, "test.yan", {}) is None
        assert debugger.should_break(10, "test.yan", {}) is None
        assert debugger.should_break(10, "test.yan", {}) is None
        
        # 第4次触发
        bp = debugger.should_break(10, "test.yan", {})
        assert bp is not None


class TestWatchExpressions:
    """监视表达式测试"""
    
    def test_add_watch_expression(self):
        debugger = YanDebuggerEnhanced()
        watch = debugger.add_watch_expression("x + y")
        
        assert watch.expression == "x + y"
        assert watch.enabled is True
        assert watch.id is not None
    
    def test_remove_watch_expression(self):
        debugger = YanDebuggerEnhanced()
        watch = debugger.add_watch_expression("x")
        
        result = debugger.remove_watch_expression(watch.id)
        assert result is True
        
        assert len(debugger.get_watch_expressions()) == 0
    
    def test_remove_nonexistent_watch(self):
        debugger = YanDebuggerEnhanced()
        result = debugger.remove_watch_expression("nonexistent")
        assert result is False
    
    def test_update_watch_expressions(self):
        debugger = YanDebuggerEnhanced()
        debugger.add_watch_expression("x + y")
        debugger.local_variables = {"x": 3, "y": 5}
        
        debugger.update_watch_expressions()
        
        watches = debugger.get_watch_expressions()
        assert len(watches) == 1
        assert watches[0].value == 8
        assert watches[0].type_name == "int"
    
    def test_watch_expression_error(self):
        debugger = YanDebuggerEnhanced()
        debugger.add_watch_expression("unknown_var")
        
        debugger.update_watch_expressions()
        
        watches = debugger.get_watch_expressions()
        assert watches[0].error is not None


class TestDebugControl:
    """调试控制测试"""
    
    def test_start(self):
        debugger = YanDebuggerEnhanced()
        debugger.start()
        
        assert debugger.state == DebugState.RUNNING
        assert debugger.step_mode == StepMode.NONE
    
    def test_pause(self):
        debugger = YanDebuggerEnhanced()
        debugger.start()
        debugger.pause()
        
        assert debugger.pause_requested is True
    
    def test_resume(self):
        debugger = YanDebuggerEnhanced()
        debugger.state = DebugState.PAUSED
        debugger.pause_requested = True
        
        debugger.resume()
        
        assert debugger.state == DebugState.RUNNING
        assert debugger.pause_requested is False
    
    def test_step_into(self):
        debugger = YanDebuggerEnhanced()
        debugger.step_into()
        
        assert debugger.state == DebugState.STEPPING
        assert debugger.step_mode == StepMode.STEP_INTO
    
    def test_step_over(self):
        debugger = YanDebuggerEnhanced()
        debugger.step_over()
        
        assert debugger.state == DebugState.STEPPING
        assert debugger.step_mode == StepMode.STEP_OVER
    
    def test_step_out(self):
        debugger = YanDebuggerEnhanced()
        debugger.call_stack = [Frame(id=1, name="func1", line=10)]
        
        debugger.step_out()
        
        assert debugger.state == DebugState.STEPPING
        assert debugger.step_mode == StepMode.STEP_OUT
        assert debugger.step_out_level == 1
    
    def test_stop(self):
        debugger = YanDebuggerEnhanced()
        debugger.start()
        debugger.stop()
        
        assert debugger.state == DebugState.STOPPED
        assert debugger.terminate_requested is True
    
    def test_restart(self):
        debugger = YanDebuggerEnhanced()
        debugger.call_stack = [Frame(id=1, name="func1", line=10)]
        debugger.local_variables = {"x": 10}
        debugger.current_line = 5
        
        debugger.restart()
        
        assert debugger.state == DebugState.STOPPED
        assert len(debugger.call_stack) == 0
        assert len(debugger.local_variables) == 0
        assert debugger.current_line == 0


class TestCallStack:
    """调用栈测试"""
    
    def test_enter_function(self):
        debugger = YanDebuggerEnhanced()
        debugger.enter_function("my_func", 10, {"x": 5, "y": 3})
        
        assert len(debugger.call_stack) == 1
        frame = debugger.call_stack[0]
        assert frame.name == "my_func"
        assert frame.line == 10
        assert frame.scope_variables == {"x": 5, "y": 3}
    
    def test_exit_function(self):
        debugger = YanDebuggerEnhanced()
        debugger.enter_function("func1", 10, {"a": 1})
        debugger.enter_function("func2", 20, {"b": 2})
        
        assert len(debugger.call_stack) == 2
        
        debugger.exit_function()
        assert len(debugger.call_stack) == 1
        assert debugger.call_stack[0].name == "func1"
    
    def test_get_call_stack(self):
        debugger = YanDebuggerEnhanced()
        debugger.enter_function("main", 5, {})
        debugger.enter_function("helper", 15, {"x": 10})
        
        stack = debugger.get_call_stack()
        assert len(stack) == 2
        assert stack[0].name == "main"
        assert stack[1].name == "helper"


class TestVariables:
    """变量管理测试"""
    
    def test_set_local_variable(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_variable("x", 42)
        
        assert debugger.local_variables["x"] == 42
    
    def test_set_global_variable(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_variable("global_var", "hello", is_global=True)
        
        assert debugger.global_variables["global_var"] == "hello"
    
    def test_evaluate_expression(self):
        debugger = YanDebuggerEnhanced()
        debugger.local_variables = {"x": 10, "y": 20}
        
        result = debugger.evaluate_expression("x + y")
        assert result == 30
    
    def test_evaluate_expression_error(self):
        debugger = YanDebuggerEnhanced()
        
        result = debugger.evaluate_expression("unknown + 1")
        assert "错误" in str(result)
    
    def test_get_variables(self):
        debugger = YanDebuggerEnhanced()
        debugger.local_variables = {"x": 10, "y": "hello"}
        debugger.global_variables = {"global": 100}
        
        local_vars = debugger.get_variables("local")
        assert len(local_vars) == 2
        
        global_vars = debugger.get_variables("global")
        assert len(global_vars) == 1


class TestOnLineCallback:
    """行回调测试"""
    
    def test_on_line_triggers_breakpoint(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan")
        debugger.start()
        
        breakpoint_hit = []
        debugger.on_break = lambda bp: breakpoint_hit.append(bp)
        
        debugger.on_line(10, "test.yan", {})
        
        assert len(breakpoint_hit) == 1
        assert debugger.state == DebugState.BREAKPOINT
    
    def test_on_line_triggers_step_into(self):
        debugger = YanDebuggerEnhanced()
        debugger.step_into()
        
        step_hit = []
        debugger.on_step = lambda line, file: step_hit.append((line, file))
        
        debugger.on_line(5, "test.yan", {})
        
        assert len(step_hit) == 1
        assert debugger.state == DebugState.PAUSED
        assert debugger.step_mode == StepMode.NONE
    
    def test_on_line_updates_variables(self):
        debugger = YanDebuggerEnhanced()
        debugger.start()
        
        debugger.on_line(5, "test.yan", {"x": 10, "y": 20})
        
        assert debugger.local_variables["x"] == 10
        assert debugger.local_variables["y"] == 20


class TestStateQuery:
    """状态查询测试"""
    
    def test_get_state(self):
        debugger = YanDebuggerEnhanced()
        debugger.set_breakpoint(10, "test.yan")
        debugger.local_variables = {"x": 5}
        
        state = debugger.get_state()
        
        assert state["state"] == "stopped"
        assert state["current_line"] == 0
        assert len(state["breakpoints"]) == 1
        assert state["local_variables"]["x"] == "5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
