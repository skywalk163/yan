#!/usr/bin/env python3
"""
言语言调试器 - Debugger
为言语言提供调试功能支持
"""

import sys
import json
import traceback
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import time


class DebugState(Enum):
    """调试状态"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"


@dataclass
class Breakpoint:
    """断点"""
    line: int
    condition: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0


@dataclass
class Frame:
    """调用栈帧"""
    name: str
    line: int
    variables: Dict[str, Any]
    file: str


@dataclass
class Variable:
    """变量"""
    name: str
    value: Any
    type_name: str


class YanDebugger:
    """言语言调试器"""

    def __init__(self):
        self.state = DebugState.STOPPED
        self.breakpoints: Dict[int, Breakpoint] = {}
        self.call_stack: List[Frame] = []
        self.variables: Dict[str, Any] = {}
        self.current_file = ""
        self.current_line = 0
        self.break_condition: Optional[Callable] = None
        self.pause_on_next = False
        self.stepping_mode: Optional[str] = None  # "step", "next", "stepout"
        self.step_out_level = 0

        # 用于与IDE通信的回调
        self.on_break: Optional[Callable] = None
        self.on_output: Optional[Callable] = None

        # 调试会话配置
        self.config = {
            "source_path": ".",
            "entry_file": "主.yan",
            "args": []
        }

    def set_config(self, key: str, value: Any):
        """设置配置"""
        self.config[key] = value

    def set_breakpoint(self, line: int, condition: Optional[str] = None):
        """设置断点"""
        bp = Breakpoint(line=line, condition=condition)
        self.breakpoints[line] = bp
        return bp

    def remove_breakpoint(self, line: int):
        """移除断点"""
        if line in self.breakpoints:
            del self.breakpoints[line]

    def clear_breakpoints(self):
        """清除所有断点"""
        self.breakpoints.clear()

    def get_breakpoints(self) -> List[Breakpoint]:
        """获取所有断点"""
        return list(self.breakpoints.values())

    def toggle_breakpoint(self, line: int) -> bool:
        """切换断点"""
        if line in self.breakpoints:
            self.breakpoints[line].enabled = not self.breakpoints[line].enabled
            return self.breakpoints[line].enabled
        else:
            self.set_breakpoint(line)
            return True

    def should_break(self, line: int, env: Dict) -> bool:
        """检查是否应该在该行暂停"""
        if line not in self.breakpoints:
            return False

        bp = self.breakpoints[line]
        if not bp.enabled:
            return False

        # 检查条件
        if bp.condition:
            try:
                # 这里简化处理，实际应该在言语言环境中求值
                # 暂时返回True
                pass
            except:
                pass

        bp.hit_count += 1
        return True

    def pause(self):
        """暂停执行"""
        self.pause_on_next = True

    def resume(self):
        """继续执行"""
        self.state = DebugState.RUNNING
        self.stepping_mode = None

    def step(self):
        """单步执行"""
        self.state = DebugState.STEPPING
        self.stepping_mode = "step"

    def step_next(self):
        """下一步（跳过函数）"""
        self.state = DebugState.STEPPING
        self.stepping_mode = "next"

    def step_out(self):
        """跳出函数"""
        self.state = DebugState.STEPPING
        self.stepping_mode = "stepout"
        self.step_out_level = len(self.call_stack)

    def restart(self):
        """重启调试"""
        self.state = DebugState.STOPPED
        self.call_stack.clear()
        self.variables.clear()
        self.current_line = 0

    def get_call_stack(self) -> List[Frame]:
        """获取调用栈"""
        return self.call_stack

    def get_variables(self) -> List[Variable]:
        """获取当前变量"""
        result = []
        for name, value in self.variables.items():
            result.append(Variable(
                name=name,
                value=value,
                type_name=type(value).__name__
            ))
        return result

    def set_variable(self, name: str, value: Any):
        """设置变量值"""
        self.variables[name] = value

    def evaluate_expression(self, expr: str) -> Any:
        """计算表达式（简化版）"""
        # 这里简化处理，实际应该使用言语言解释器
        try:
            # 尝试在Python环境中计算
            return eval(expr, {}, self.variables)
        except:
            return f"无法计算: {expr}"

    def on_line(self, line: int, file: str, env: Dict):
        """在行执行时的回调"""
        self.current_line = line
        self.current_file = file

        # 更新变量
        self.variables.update(env)

        # 检查是否需要暂停
        should_pause = False

        if self.should_break(line, env):
            should_pause = True
        elif self.pause_on_next:
            should_pause = True
            self.pause_on_next = False
        elif self.stepping_mode:
            if self.stepping_mode == "step":
                should_pause = True
            elif self.stepping_mode == "next" and len(self.call_stack) == self.step_out_level:
                should_pause = True
            elif self.stepping_mode == "stepout" and len(self.call_stack) < self.step_out_level:
                should_pause = True

        if should_pause:
            self.state = DebugState.PAUSED
            if self.on_break:
                self.on_break(line, file)

    def enter_function(self, name: str, line: int, variables: Dict):
        """进入函数"""
        frame = Frame(
            name=name,
            line=line,
            variables=variables.copy(),
            file=self.current_file
        )
        self.call_stack.append(frame)

    def exit_function(self, name: str):
        """退出函数"""
        if self.call_stack:
            self.call_stack.pop()

    def write_output(self, text: str):
        """输出"""
        if self.on_output:
            self.on_output(text)

    def get_state(self) -> Dict:
        """获取调试状态"""
        return {
            "state": self.state.value,
            "current_file": self.current_file,
            "current_line": self.current_line,
            "call_stack": [
                {
                    "name": frame.name,
                    "line": frame.line,
                    "file": frame.file
                }
                for frame in self.call_stack
            ],
            "variables": [
                {
                    "name": var.name,
                    "value": repr(var.value),
                    "type": var.type_name
                }
                for var in self.get_variables()
            ],
            "breakpoints": [
                {
                    "line": bp.line,
                    "enabled": bp.enabled,
                    "hit_count": bp.hit_count,
                    "condition": bp.condition
                }
                for bp in self.breakpoints.values()
            ]
        }


class DebugServer:
    """调试服务器（与IDE通信）"""

    def __init__(self, debugger: YanDebugger):
        self.debugger = debugger
        self.running = False
        self.port = 4711
        self.client = None

        # 设置回调
        self.debugger.on_break = self._on_break
        self.debugger.on_output = self._on_output

    def start(self):
        """启动调试服务器"""
        # 简化版 - 使用标准输入输出通信
        self.running = True
        self._run_communication_loop()

    def stop(self):
        """停止调试服务器"""
        self.running = False

    def _run_communication_loop(self):
        """通信循环"""
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

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
                print(f"Error: {e}", file=sys.stderr)

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
                "supportsLogPoints": False,
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
            self.debugger.state = DebugState.RUNNING

        elif method == "attach":
            self.debugger.state = DebugState.RUNNING

        elif method == "continue":
            self.debugger.resume()

        elif method == "next":
            self.debugger.step_next()

        elif method == "stepIn":
            self.debugger.step()

        elif method == "stepOut":
            self.debugger.step_out()

        elif method == "pause":
            self.debugger.pause()

        elif method == "terminate":
            self.debugger.state = DebugState.STOPPED
            self.running = False

        elif method == "restart":
            self.debugger.restart()

        elif method == "setBreakpoints":
            file = params.get("source", {}).get("path", "")
            bps = params.get("breakpoints", [])
            self.debugger.clear_breakpoints()
            for bp in bps:
                line = bp.get("line", 0)
                condition = bp.get("condition")
                self.debugger.set_breakpoint(line, condition)
            result = {
                "breakpoints": [
                    {"verified": True, "line": bp.line}
                    for bp in self.debugger.get_breakpoints()
                ]
            }

        elif method == "breakpointLocations":
            result = {"breakpoints": []}

        elif method == "stackTrace":
            stack = self.debugger.get_call_stack()
            result = {
                "stackFrames": [
                    {
                        "id": i,
                        "name": frame.name,
                        "source": {"path": frame.file},
                        "line": frame.line,
                        "column": 0
                    }
                    for i, frame in enumerate(stack)
                ],
                "totalFrames": len(stack)
            }

        elif method == "scopes":
            result = {
                "scopes": [
                    {
                        "name": "Local",
                        "variablesReference": 1,
                        "namedVariables": len(self.debugger.variables)
                    }
                ]
            }

        elif method == "variables":
            variables = self.debugger.get_variables()
            result = {
                "variables": [
                    {
                        "name": var.name,
                        "value": repr(var.value),
                        "type": var.type_name,
                        "variablesReference": 0
                    }
                    for var in variables
                ]
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

        elif method == "source":
            result = {
                "content": "",
                "mimeType": "text/plain"
            }

        elif method == "loadedSources":
            result = {"sources": []}

        elif method == "threads":
            result = {
                "threads": [
                    {"id": 1, "name": "Main Thread"}
                ]
            }

        if request_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }

        return None

    def _on_break(self, line: int, file: str):
        """断点回调"""
        event = {
            "jsonrpc": "2.0",
            "method": "stopped",
            "params": {
                "reason": "breakpoint",
                "threadId": 1,
                "source": {"path": file},
                "line": line
            }
        }
        print(json.dumps(event, ensure_ascii=False))
        sys.stdout.flush()

    def _on_output(self, text: str):
        """输出回调"""
        event = {
            "jsonrpc": "2.0",
            "method": "output",
            "params": {
                "category": "stdout",
                "output": text,
                "source": {"path": self.debugger.current_file},
                "line": self.debugger.current_line
            }
        }
        print(json.dumps(event, ensure_ascii=False))
        sys.stdout.flush()


def main():
    """调试器主函数"""
    debugger = YanDebugger()
    server = DebugServer(debugger)

    print("言语言调试器 v0.1.0")
    print("等待连接...")

    try:
        server.start()
    except KeyboardInterrupt:
        print("调试器已停止")


if __name__ == "__main__":
    main()
