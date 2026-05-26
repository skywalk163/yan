"""
言语言调试器增强版
提供完整的断点、步进、变量监视功能
"""

import sys
import json
import traceback
import threading
import time
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum


class DebugState(Enum):
    """调试状态"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"
    BREAKPOINT = "breakpoint"


class StepMode(Enum):
    """步进模式"""
    NONE = None
    STEP_INTO = "stepInto"
    STEP_OVER = "stepOver"
    STEP_OUT = "stepOut"


@dataclass
class Breakpoint:
    """断点"""
    id: str
    line: int
    file: str
    condition: Optional[str] = None
    hit_condition: Optional[str] = None  # 命中条件（如 hitCount > 5）
    log_message: Optional[str] = None    # 日志点消息
    enabled: bool = True
    hit_count: int = 0
    verified: bool = False
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "line": self.line,
            "file": self.file,
            "condition": self.condition,
            "hitCondition": self.hit_condition,
            "logMessage": self.log_message,
            "enabled": self.enabled,
            "hitCount": self.hit_count,
            "verified": self.verified
        }


@dataclass
class WatchExpression:
    """监视表达式"""
    id: str
    expression: str
    value: Any = None
    type_name: str = ""
    enabled: bool = True
    error: Optional[str] = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "expression": self.expression,
            "value": repr(self.value) if self.value is not None else "undefined",
            "type": self.type_name,
            "enabled": self.enabled,
            "error": self.error
        }


@dataclass
class Frame:
    """调用栈帧"""
    id: int
    name: str
    line: int
    column: int = 0
    file: str = ""
    scope_variables: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "file": self.file,
            "variables": len(self.scope_variables)
        }


@dataclass
class VariableInfo:
    """变量信息"""
    name: str
    value: Any
    type_name: str
    is_primitive: bool = True
    children: List['VariableInfo'] = field(default_factory=list)
    variables_reference: int = 0
    
    def to_dict(self):
        """转换为字典"""
        return {
            "name": self.name,
            "value": repr(self.value) if self.is_primitive else "...",
            "type": self.type_name,
            "variablesReference": self.variables_reference if self.children else 0,
            "hasChildren": len(self.children) > 0
        }


class YanDebuggerEnhanced:
    """增强版言语言调试器"""
    
    def __init__(self):
        # 调试状态
        self.state = DebugState.STOPPED
        self.step_mode = StepMode.NONE
        self.step_out_level = 0
        
        # 断点管理
        self.breakpoints: Dict[str, Breakpoint] = {}
        self.breakpoint_id_counter = 1
        
        # 监视表达式
        self.watch_expressions: Dict[str, WatchExpression] = {}
        self.watch_id_counter = 1
        
        # 调用栈
        self.call_stack: List[Frame] = []
        self.frame_id_counter = 1
        
        # 当前执行位置
        self.current_file = ""
        self.current_line = 0
        self.current_column = 0
        
        # 变量存储
        self.global_variables: Dict[str, Any] = {}
        self.local_variables: Dict[str, Any] = {}
        
        # 回调函数
        self.on_break: Optional[Callable[[Breakpoint], None]] = None
        self.on_step: Optional[Callable[[int, str], None]] = None
        self.on_variable_change: Optional[Callable[[str, Any], None]] = None
        self.on_output: Optional[Callable[[str], None]] = None
        self.on_watch_update: Optional[Callable[[List[WatchExpression]], None]] = None
        
        # 配置
        self.config = {
            "source_path": ".",
            "entry_file": "主.yan",
            "args": [],
            "auto_continue": False,
            "show_hidden_variables": False
        }
        
        # 执行控制
        self.pause_requested = False
        self.terminate_requested = False
        
        # 事件通知
        self.event_queue: List[Dict] = []
    
    def set_config(self, key: str, value: Any):
        """设置配置"""
        self.config[key] = value
    
    # ====================
    # 断点管理
    # ====================
    
    def set_breakpoint(
        self,
        line: int,
        file: str = "",
        condition: Optional[str] = None,
        hit_condition: Optional[str] = None,
        log_message: Optional[str] = None
    ) -> Breakpoint:
        """设置断点"""
        bp_id = f"bp_{self.breakpoint_id_counter}"
        self.breakpoint_id_counter += 1
        
        bp = Breakpoint(
            id=bp_id,
            line=line,
            file=file,
            condition=condition,
            hit_condition=hit_condition,
            log_message=log_message,
            verified=True  # 假设设置时就验证通过
        )
        
        # 使用文件+行号作为键
        key = f"{file}:{line}"
        self.breakpoints[key] = bp
        
        return bp
    
    def get_breakpoint(self, line: int, file: str = "") -> Optional[Breakpoint]:
        """获取断点"""
        key = f"{file}:{line}"
        return self.breakpoints.get(key)
    
    def remove_breakpoint(self, line: int, file: str = "") -> bool:
        """移除断点"""
        key = f"{file}:{line}"
        if key in self.breakpoints:
            del self.breakpoints[key]
            return True
        return False
    
    def remove_breakpoint_by_id(self, bp_id: str) -> bool:
        """按ID移除断点"""
        for key, bp in list(self.breakpoints.items()):
            if bp.id == bp_id:
                del self.breakpoints[key]
                return True
        return False
    
    def clear_breakpoints(self):
        """清除所有断点"""
        self.breakpoints.clear()
    
    def toggle_breakpoint(self, line: int, file: str = "") -> bool:
        """切换断点状态"""
        key = f"{file}:{line}"
        if key in self.breakpoints:
            self.breakpoints[key].enabled = not self.breakpoints[key].enabled
            return self.breakpoints[key].enabled
        else:
            self.set_breakpoint(line, file)
            return True
    
    def get_breakpoints(self) -> List[Breakpoint]:
        """获取所有断点"""
        return list(self.breakpoints.values())
    
    def should_break(self, line: int, file: str, env: Dict) -> Optional[Breakpoint]:
        """检查是否应该在该行暂停"""
        key = f"{file}:{line}"
        
        if key not in self.breakpoints:
            return None
        
        bp = self.breakpoints[key]
        
        if not bp.enabled:
            return None
        
        bp.hit_count += 1
        
        # 检查命中条件
        if bp.hit_condition:
            if not self._evaluate_hit_condition(bp, env):
                return None
        
        # 检查条件表达式
        if bp.condition:
            if not self._evaluate_condition(bp.condition, env):
                return None
        
        # 处理日志点
        if bp.log_message:
            message = self._format_log_message(bp.log_message, env)
            if self.on_output:
                self.on_output(message)
            # 如果只是日志点，不暂停
            if not bp.condition and not bp.hit_condition:
                return None
        
        return bp
    
    def _evaluate_condition(self, condition: str, env: Dict) -> bool:
        """评估条件表达式"""
        try:
            # 在环境中评估条件
            return bool(eval(condition, {}, env))
        except Exception:
            return False
    
    def _evaluate_hit_condition(self, bp: Breakpoint, env: Dict) -> bool:
        """评估命中条件"""
        try:
            # 支持 hitCount 变量
            local_env = {"hitCount": bp.hit_count}
            local_env.update(env)
            return eval(bp.hit_condition, {}, local_env)
        except Exception:
            return False
    
    def _format_log_message(self, message: str, env: Dict) -> str:
        """格式化日志消息（支持 {variable} 语法）"""
        try:
            # 替换 {var} 为变量值
            import re
            def replacer(match):
                var_name = match.group(1)
                return repr(env.get(var_name, f"{{{var_name}}}"))
            return re.sub(r'\{(\w+)\}', replacer, message)
        except Exception:
            return message
    
    # ====================
    # 监视表达式管理
    # ====================
    
    def add_watch_expression(self, expression: str) -> WatchExpression:
        """添加监视表达式"""
        watch_id = f"watch_{self.watch_id_counter}"
        self.watch_id_counter += 1
        
        watch = WatchExpression(
            id=watch_id,
            expression=expression,
            enabled=True
        )
        
        self.watch_expressions[watch_id] = watch
        self.update_watch_expressions()
        
        return watch
    
    def remove_watch_expression(self, watch_id: str) -> bool:
        """移除监视表达式"""
        if watch_id in self.watch_expressions:
            del self.watch_expressions[watch_id]
            return True
        return False
    
    def get_watch_expressions(self) -> List[WatchExpression]:
        """获取所有监视表达式"""
        return list(self.watch_expressions.values())
    
    def update_watch_expressions(self):
        """更新所有监视表达式的值"""
        updated = []
        
        for watch in self.watch_expressions.values():
            if not watch.enabled:
                continue
            
            try:
                # 合并全局和局部变量
                env = {**self.global_variables, **self.local_variables}
                value = eval(watch.expression, {}, env)
                watch.value = value
                watch.type_name = type(value).__name__
                watch.error = None
                updated.append(watch)
            except Exception as e:
                watch.error = str(e)
                watch.value = None
        
        if self.on_watch_update and updated:
            self.on_watch_update(updated)
    
    # ====================
    # 调试控制
    # ====================
    
    def start(self):
        """开始调试"""
        self.state = DebugState.RUNNING
        self.step_mode = StepMode.NONE
    
    def pause(self):
        """暂停执行"""
        self.pause_requested = True
    
    def resume(self):
        """继续执行"""
        self.state = DebugState.RUNNING
        self.step_mode = StepMode.NONE
        self.pause_requested = False
    
    def step_into(self):
        """单步进入"""
        self.state = DebugState.STEPPING
        self.step_mode = StepMode.STEP_INTO
        self.pause_requested = False
    
    def step_over(self):
        """单步跳过（下一步）"""
        self.state = DebugState.STEPPING
        self.step_mode = StepMode.STEP_OVER
        self.pause_requested = False
    
    def step_out(self):
        """单步跳出"""
        self.state = DebugState.STEPPING
        self.step_mode = StepMode.STEP_OUT
        self.step_out_level = len(self.call_stack)
        self.pause_requested = False
    
    def stop(self):
        """停止调试"""
        self.state = DebugState.STOPPED
        self.terminate_requested = True
    
    def restart(self):
        """重启调试"""
        self.state = DebugState.STOPPED
        self.call_stack.clear()
        self.local_variables.clear()
        self.current_line = 0
        self.step_mode = StepMode.NONE
        self.pause_requested = False
        self.terminate_requested = False
    
    # ====================
    # 执行回调
    # ====================
    
    def on_line(self, line: int, file: str, env: Dict):
        """行执行回调"""
        self.current_line = line
        self.current_file = file
        
        # 更新变量
        self.local_variables.update(env)
        
        # 更新监视表达式
        self.update_watch_expressions()
        
        # 检查断点
        bp = self.should_break(line, file, env)
        if bp:
            self.state = DebugState.BREAKPOINT
            if self.on_break:
                self.on_break(bp)
            return
        
        # 检查暂停请求
        if self.pause_requested:
            self.state = DebugState.PAUSED
            self.pause_requested = False
            if self.on_step:
                self.on_step(line, file)
            return
        
        # 检查步进模式
        if self.step_mode != StepMode.NONE:
            if self.step_mode == StepMode.STEP_INTO:
                self.state = DebugState.PAUSED
                self.step_mode = StepMode.NONE
                if self.on_step:
                    self.on_step(line, file)
            elif self.step_mode == StepMode.STEP_OVER:
                # 仅在当前调用层级暂停
                if len(self.call_stack) <= self.step_out_level:
                    self.state = DebugState.PAUSED
                    self.step_mode = StepMode.NONE
                    if self.on_step:
                        self.on_step(line, file)
            elif self.step_mode == StepMode.STEP_OUT:
                # 当调用栈变短时暂停
                if len(self.call_stack) < self.step_out_level:
                    self.state = DebugState.PAUSED
                    self.step_mode = StepMode.NONE
                    if self.on_step:
                        self.on_step(line, file)
    
    def enter_function(self, name: str, line: int, args: Dict[str, Any], file: str = ""):
        """进入函数"""
        frame = Frame(
            id=self.frame_id_counter,
            name=name,
            line=line,
            file=file,
            scope_variables=args.copy()
        )
        self.frame_id_counter += 1
        self.call_stack.append(frame)
        
        # 更新局部变量
        self.local_variables = args.copy()
    
    def exit_function(self):
        """退出函数"""
        if self.call_stack:
            self.call_stack.pop()
            # 恢复上一层的变量
            if self.call_stack:
                self.local_variables = self.call_stack[-1].scope_variables.copy()
            else:
                self.local_variables.clear()
    
    def set_variable(self, name: str, value: Any, is_global: bool = False):
        """设置变量值"""
        if is_global:
            self.global_variables[name] = value
        else:
            self.local_variables[name] = value
        
        # 更新监视表达式
        self.update_watch_expressions()
        
        if self.on_variable_change:
            self.on_variable_change(name, value)
    
    def evaluate_expression(self, expr: str) -> Any:
        """计算表达式"""
        try:
            env = {**self.global_variables, **self.local_variables}
            return eval(expr, {}, env)
        except Exception as e:
            return f"错误: {e}"
    
    # ====================
    # 状态查询
    # ====================
    
    def get_call_stack(self) -> List[Frame]:
        """获取调用栈"""
        return self.call_stack
    
    def get_variables(self, scope: str = "local") -> List[VariableInfo]:
        """获取变量列表"""
        variables = self.local_variables if scope == "local" else self.global_variables
        result = []
        
        for name, value in variables.items():
            var_info = self._create_variable_info(name, value, 0)
            result.append(var_info)
        
        return result
    
    def _create_variable_info(self, name: str, value: Any, ref_id: int) -> VariableInfo:
        """创建变量信息对象"""
        var_type = type(value).__name__
        is_primitive = isinstance(value, (int, float, str, bool, type(None)))
        
        children = []
        if not is_primitive:
            if isinstance(value, dict):
                for key, val in value.items():
                    children.append(self._create_variable_info(str(key), val, ref_id + 1))
            elif isinstance(value, (list, tuple)):
                for i, val in enumerate(value):
                    children.append(self._create_variable_info(str(i), val, ref_id + 1))
        
        return VariableInfo(
            name=name,
            value=value,
            type_name=var_type,
            is_primitive=is_primitive,
            children=children,
            variables_reference=ref_id if children else 0
        )
    
    def get_state(self) -> Dict:
        """获取调试状态"""
        return {
            "state": self.state.value,
            "current_file": self.current_file,
            "current_line": self.current_line,
            "current_column": self.current_column,
            "call_stack": [frame.to_dict() for frame in self.call_stack],
            "breakpoints": [bp.to_dict() for bp in self.breakpoints.values()],
            "watch_expressions": [w.to_dict() for w in self.watch_expressions.values()],
            "local_variables": {k: repr(v) for k, v in self.local_variables.items()},
            "global_variables": {k: repr(v) for k, v in self.global_variables.items()}
        }


class DebugServerEnhanced:
    """增强版调试服务器"""
    
    def __init__(self, debugger: YanDebuggerEnhanced):
        self.debugger = debugger
        self.running = False
        self.port = 4711
        self.thread: Optional[threading.Thread] = None
        
        # 设置回调
        self.debugger.on_break = self._on_break
        self.debugger.on_step = self._on_step
        self.debugger.on_output = self._on_output
        self.debugger.on_watch_update = self._on_watch_update
    
    def start(self, port: int = 4711):
        """启动调试服务器"""
        self.port = port
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        print(f"调试服务器已启动，端口 {port}")
    
    def stop(self):
        """停止调试服务器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def _run_server(self):
        """服务器主循环"""
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    continue
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    response = self._handle_request(request)
                    if response:
                        print(json.dumps(response, ensure_ascii=False))
                        sys.stdout.flush()
                except json.JSONDecodeError:
                    continue
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"调试服务器错误: {e}", file=sys.stderr)
    
    def _handle_request(self, request: Dict) -> Optional[Dict]:
        """处理调试请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        result = None
        
        if method == "initialize":
            result = {
                "supportsConfigurationDoneRequest": True,
                "supportsFunctionBreakpoints": True,
                "supportsConditionalBreakpoints": True,
                "supportsHitConditionalBreakpoints": True,
                "supportsEvaluateForHovers": True,
                "supportsStepBack": False,
                "supportsSetVariable": True,
                "supportsRestartFrame": False,
                "supportsGotoTargets": False,
                "supportsStepInTargets": False,
                "supportsCompletionsRequest": True,
                "supportsModulesRequest": False,
                "supportsRestartRequest": True,
                "supportsExceptionOptions": False,
                "supportsValueFormattingOptions": False,
                "supportsExceptionInfoRequest": False,
                "supportsTerminateDebuggee": True,
                "supportsDelayedStackTraceLoading": False,
                "supportsLoadedSources": False,
                "supportsLogPoints": True,
                "supportsTerminateThreads": False,
                "supportsTerminateRequest": True,
                "supportsBreakpointLocations": True,
                "supportsClipboardContext": False
            }
        
        elif method == "launch":
            file = params.get("program")
            args = params.get("args", [])
            if file:
                self.debugger.set_config("entry_file", file)
            self.debugger.set_config("args", args)
            self.debugger.start()
        
        elif method == "attach":
            self.debugger.start()
        
        elif method == "continue":
            self.debugger.resume()
        
        elif method == "next":
            self.debugger.step_over()
        
        elif method == "stepIn":
            self.debugger.step_into()
        
        elif method == "stepOut":
            self.debugger.step_out()
        
        elif method == "pause":
            self.debugger.pause()
        
        elif method == "terminate":
            self.debugger.stop()
            self.running = False
        
        elif method == "restart":
            self.debugger.restart()
        
        elif method == "setBreakpoints":
            file = params.get("source", {}).get("path", "")
            bps = params.get("breakpoints", [])
            
            # 移除该文件的所有断点
            self.debugger.breakpoints = {
                k: v for k, v in self.debugger.breakpoints.items()
                if not k.startswith(file + ":")
            }
            
            # 添加新断点
            for bp in bps:
                line = bp.get("line", 0)
                condition = bp.get("condition")
                hit_condition = bp.get("hitCondition")
                log_message = bp.get("logMessage")
                self.debugger.set_breakpoint(line, file, condition, hit_condition, log_message)
            
            result = {
                "breakpoints": [
                    {"verified": bp.verified, "line": bp.line, "id": bp.id}
                    for bp in self.debugger.get_breakpoints()
                ]
            }
        
        elif method == "setExpression":
            # 设置监视表达式
            expr = params.get("expression", "")
            enabled = params.get("enabled", True)
            watch = self.debugger.add_watch_expression(expr)
            watch.enabled = enabled
            result = {
                "id": watch.id,
                "expression": expr,
                "enabled": enabled
            }
        
        elif method == "clearExpression":
            # 清除监视表达式
            watch_id = params.get("id", "")
            self.debugger.remove_watch_expression(watch_id)
        
        elif method == "stackTrace":
            stack = self.debugger.get_call_stack()
            result = {
                "stackFrames": [
                    {
                        "id": frame.id,
                        "name": frame.name,
                        "source": {"path": frame.file} if frame.file else {},
                        "line": frame.line,
                        "column": frame.column
                    }
                    for frame in stack
                ],
                "totalFrames": len(stack)
            }
        
        elif method == "scopes":
            result = {
                "scopes": [
                    {
                        "name": "Local",
                        "variablesReference": 1,
                        "namedVariables": len(self.debugger.local_variables),
                        "indexedVariables": 0
                    },
                    {
                        "name": "Global",
                        "variablesReference": 2,
                        "namedVariables": len(self.debugger.global_variables),
                        "indexedVariables": 0
                    }
                ]
            }
        
        elif method == "variables":
            variables_reference = params.get("variablesReference", 0)
            scope = "local" if variables_reference == 1 else "global"
            variables = self.debugger.get_variables(scope)
            
            result = {
                "variables": [var.to_dict() for var in variables]
            }
        
        elif method == "evaluate":
            expr = params.get("expression", "")
            result = {
                "result": repr(self.debugger.evaluate_expression(expr)),
                "type": "any",
                "variablesReference": 0
            }
        
        elif method == "setVariable":
            name = params.get("name", "")
            value = params.get("value", "")
            self.debugger.set_variable(name, value)
            result = {
                "name": name,
                "value": value,
                "variablesReference": 0
            }
        
        elif method == "threads":
            result = {
                "threads": [{"id": 1, "name": "Main Thread"}]
            }
        
        elif method == "breakpointLocations":
            result = {"breakpoints": []}
        
        elif method == "source":
            result = {"content": "", "mimeType": "text/plain"}
        
        elif method == "loadedSources":
            result = {"sources": []}
        
        if request_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        return None
    
    def _send_event(self, event: Dict):
        """发送事件"""
        print(json.dumps(event, ensure_ascii=False))
        sys.stdout.flush()
    
    def _on_break(self, bp: Breakpoint):
        """断点事件"""
        self._send_event({
            "jsonrpc": "2.0",
            "method": "stopped",
            "params": {
                "reason": "breakpoint",
                "threadId": 1,
                "source": {"path": bp.file} if bp.file else {},
                "line": bp.line
            }
        })
    
    def _on_step(self, line: int, file: str):
        """步进事件"""
        self._send_event({
            "jsonrpc": "2.0",
            "method": "stopped",
            "params": {
                "reason": "step",
                "threadId": 1,
                "source": {"path": file} if file else {},
                "line": line
            }
        })
    
    def _on_output(self, text: str):
        """输出事件"""
        self._send_event({
            "jsonrpc": "2.0",
            "method": "output",
            "params": {
                "category": "stdout",
                "output": text,
                "source": {"path": self.debugger.current_file},
                "line": self.debugger.current_line
            }
        })
    
    def _on_watch_update(self, watches: List[WatchExpression]):
        """监视表达式更新事件"""
        self._send_event({
            "jsonrpc": "2.0",
            "method": "output",
            "params": {
                "category": "telemetry",
                "output": json.dumps([w.to_dict() for w in watches], ensure_ascii=False)
            }
        })


def main():
    """调试器主函数"""
    debugger = YanDebuggerEnhanced()
    server = DebugServerEnhanced(debugger)
    
    print("言语言调试器 v0.2.0")
    print("等待连接...")
    
    try:
        server.start()
        while server.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("调试器已停止")


if __name__ == "__main__":
    main()
