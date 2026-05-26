#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
言语言调试适配器
支持 VS Code Debug Adapter Protocol
"""
import sys
import json
import threading
import time
from typing import Any, Dict, List, Optional


class YanDebugAdapter:
    def __init__(self):
        self.breakpoints: Dict[str, List[int]] = {}
        self.variables: Dict[str, Any] = {}
        self.current_line: int = 0
        self.current_file: str = ""
        self.stopped = False
        self.threads = {}
        self.next_thread_id = 1
        self.launch_config: Dict[str, Any] = {}

    def start(self):
        """启动调试适配器"""
        # 读取并处理输入
        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    break

                if line.startswith('Content-Length:'):
                    length = int(line.split(':', 1)[1].strip())
                    sys.stdin.readline()  # 空行
                    payload = sys.stdin.read(length)
                    request = json.loads(payload)
                    self.handle_request(request)
        except Exception as e:
            self.log(f"错误: {e}")

    def send_event(self, event: str, body: Dict[str, Any] = None):
        """发送调试事件"""
        event_obj = {
            "type": "event",
            "event": event,
            "seq": 0,
            "body": body or {}
        }
        self._send_message(event_obj)

    def send_response(self, request: Dict[str, Any], body: Dict[str, Any] = None, error_message: str = None):
        """发送响应"""
        response = {
            "type": "response",
            "request_seq": request["seq"],
            "success": error_message is None,
            "command": request["command"],
            "body": body or {}
        }
        if error_message:
            response["message"] = error_message
        self._send_message(response)

    def _send_message(self, message: Dict[str, Any]):
        """发送消息到 VS Code"""
        payload = json.dumps(message, ensure_ascii=False)
        content = f"Content-Length: {len(payload)}\r\n\r\n{payload}"
        sys.stdout.write(content)
        sys.stdout.flush()

    def log(self, msg: str):
        """记录日志"""
        self.send_event("output", {
            "category": "console",
            "output": f"[调试] {msg}\n"
        })

    def handle_request(self, request: Dict[str, Any]):
        """处理请求"""
        command = request["command"]
        self.log(f"收到请求: {command}")

        if command == "initialize":
            self.handle_initialize(request)
        elif command == "launch":
            self.handle_launch(request)
        elif command == "configurationDone":
            self.handle_configuration_done(request)
        elif command == "setBreakpoints":
            self.handle_set_breakpoints(request)
        elif command == "threads":
            self.handle_threads(request)
        elif command == "stackTrace":
            self.handle_stack_trace(request)
        elif command == "scopes":
            self.handle_scopes(request)
        elif command == "variables":
            self.handle_variables(request)
        elif command == "next":
            self.handle_next(request)
        elif command == "stepIn":
            self.handle_step_in(request)
        elif command == "stepOut":
            self.handle_step_out(request)
        elif command == "continue":
            self.handle_continue(request)
        elif command == "pause":
            self.handle_pause(request)
        elif command == "terminate":
            self.handle_terminate(request)
        else:
            self.send_response(request, {}, f"不支持的命令: {command}")

    def handle_initialize(self, request: Dict[str, Any]):
        """初始化"""
        self.send_response(request, {
            "supportsConfigurationDoneRequest": True,
            "supportsSetVariable": True,
            "supportsEvaluateForHovers": True,
            "supportsStepBack": False,
            "supportsRestartFrame": False,
            "supportsGotoTargetsRequest": False,
            "supportsStepInTargetsRequest": False,
            "supportsCompletionsRequest": True,
            "supportsModulesRequest": False,
            "supportsRestartRequest": False,
            "supportsExceptionOptions": False,
            "supportsValueFormattingOptions": False,
            "supportsExceptionInfoRequest": False,
            "supportsDelayedStackTraceLoading": False,
            "supportsLoadedSourcesRequest": False,
            "supportsLogPoints": False,
            "supportsTerminateThreadsRequest": False,
            "supportsSetExpression": False,
            "supportsTerminateRequest": True,
            "supportsDataBreakpoints": False,
            "supportsReadMemoryRequest": False,
            "supportsDisassembleRequest": False,
            "supportsCancelRequest": False,
            "supportsBreakpointLocationsRequest": False,
            "supportsClipboardContext": False
        })
        self.send_event("initialized")

    def handle_launch(self, request: Dict[str, Any]):
        """启动调试"""
        self.launch_config = request["arguments"]
        self.current_file = self.launch_config.get("program", "")
        self.threads = {1: {"id": 1, "name": "主线程"}}
        self.send_response(request)
        
        if self.launch_config.get("stopOnEntry", False):
            self.stopped = True
            self.send_event("stopped", {
                "reason": "entry",
                "threadId": 1,
                "allThreadsStopped": True
            })

    def handle_configuration_done(self, request: Dict[str, Any]):
        """配置完成"""
        self.send_response(request)

    def handle_set_breakpoints(self, request: Dict[str, Any]):
        """设置断点"""
        args = request["arguments"]
        source_path = args["source"].get("path", "")
        breakpoints = args.get("breakpoints", [])
        
        line_nums = [bp["line"] for bp in breakpoints]
        self.breakpoints[source_path] = line_nums
        
        response_bp = [
            {"verified": True, "line": line}
            for line in line_nums
        ]
        
        self.send_response(request, {"breakpoints": response_bp})

    def handle_threads(self, request: Dict[str, Any]):
        """获取线程列表"""
        thread_list = [
            {"id": tid, "name": t["name"]}
            for tid, t in self.threads.items()
        ]
        self.send_response(request, {"threads": thread_list})

    def handle_stack_trace(self, request: Dict[str, Any]):
        """获取堆栈"""
        stack_frames = [
            {
                "id": 1,
                "name": "主程序",
                "source": {"path": self.current_file},
                "line": self.current_line or 1,
                "column": 1
            }
        ]
        self.send_response(request, {
            "stackFrames": stack_frames,
            "totalFrames": len(stack_frames)
        })

    def handle_scopes(self, request: Dict[str, Any]):
        """获取作用域"""
        scopes = [
            {
                "name": "局部变量",
                "variablesReference": 1,
                "expensive": False
            },
            {
                "name": "全局变量",
                "variablesReference": 2,
                "expensive": False
            }
        ]
        self.send_response(request, {"scopes": scopes})

    def handle_variables(self, request: Dict[str, Any]):
        """获取变量"""
        variables = [
            {
                "name": name,
                "value": str(value),
                "type": type(value).__name__,
                "variablesReference": 0
            }
            for name, value in self.variables.items()
        ]
        self.send_response(request, {"variables": variables})

    def handle_next(self, request: Dict[str, Any]):
        """下一步"""
        self.send_response(request)
        self._step()

    def handle_step_in(self, request: Dict[str, Any]):
        """单步进入"""
        self.send_response(request)
        self._step()

    def handle_step_out(self, request: Dict[str, Any]):
        """单步跳出"""
        self.send_response(request)
        self._step()

    def handle_continue(self, request: Dict[str, Any]):
        """继续执行"""
        self.send_response(request)
        self.stopped = False
        self.send_event("continued", {"threadId": 1, "allThreadsContinued": True})

    def handle_pause(self, request: Dict[str, Any]):
        """暂停"""
        self.send_response(request)
        self.stopped = True
        self.send_event("stopped", {
            "reason": "pause",
            "threadId": 1,
            "allThreadsStopped": True
        })

    def handle_terminate(self, request: Dict[str, Any]):
        """终止调试"""
        self.send_response(request)
        self.send_event("terminated")

    def _step(self):
        """执行一步"""
        self.current_line += 1
        self.stopped = True
        self.send_event("stopped", {
            "reason": "step",
            "threadId": 1,
            "allThreadsStopped": True
        })


def main():
    """主函数"""
    adapter = YanDebugAdapter()
    adapter.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
