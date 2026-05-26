#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
言语言调试适配器服务器
通过 TCP 端口与 VS Code 通信
"""
import socket
import threading
import json
import sys
import os
from typing import Dict, Any, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class DebugSession:
    """调试会话"""
    def __init__(self, socket_conn):
        self.conn = socket_conn
        self.seq = 0
        self.breakpoints: Dict[str, list] = {}
        self.variables = {}
        self.current_file = ""
        self.current_line = 1

    def send_event(self, event: str, body: dict = None):
        """发送事件"""
        self.seq += 1
        msg = {
            "type": "event",
            "seq": self.seq,
            "event": event,
            "body": body or {}
        }
        self._send_message(msg)

    def send_response(self, request: dict, body: dict = None, error: str = None):
        """发送响应"""
        self.seq += 1
        msg = {
            "type": "response",
            "seq": self.seq,
            "request_seq": request["seq"],
            "success": error is None,
            "command": request["command"],
            "body": body or {}
        }
        if error:
            msg["message"] = error
        self._send_message(msg)

    def _send_message(self, msg: dict):
        """发送消息"""
        try:
            payload = json.dumps(msg, ensure_ascii=False)
            content = f"Content-Length: {len(payload)}\r\n\r\n{payload}"
            self.conn.sendall(content.encode('utf-8'))
        except Exception as e:
            print(f"发送失败: {e}", file=sys.stderr)

    def _read_message(self) -> Optional[dict]:
        """读取消息"""
        try:
            # 读取头部
            buffer = b""
            while b"\r\n\r\n" not in buffer:
                chunk = self.conn.recv(1024)
                if not chunk:
                    return None
                buffer += chunk

            header_end = buffer.index(b"\r\n\r\n")
            header = buffer[:header_end].decode('utf-8')
            content_length = int(header.split(":")[1].strip())
            remaining = content_length

            body = buffer[header_end + 4:]
            while len(body) < content_length:
                chunk = self.conn.recv(1024)
                if not chunk:
                    return None
                body += chunk

            return json.loads(body.decode('utf-8'))
        except Exception as e:
            print(f"读取失败: {e}", file=sys.stderr)
            return None

    def process(self):
        """处理请求"""
        print("调试会话已连接", file=sys.stderr)
        self.send_event("output", {"category": "console", "output": "言语言调试器已启动\n"})

        try:
            while True:
                msg = self._read_message()
                if not msg:
                    break

                if msg["type"] == "request":
                    self._handle_request(msg)
        except Exception as e:
            print(f"会话错误: {e}", file=sys.stderr)

    def _handle_request(self, request: dict):
        """处理请求"""
        command = request["command"]
        print(f"处理请求: {command}", file=sys.stderr)

        if command == "initialize":
            self.send_response(request, {
                "supportsConfigurationDoneRequest": True,
                "supportsSetVariable": True,
                "supportsEvaluateForHovers": True,
                "supportsCompletionsRequest": True,
                "supportsTerminateRequest": True
            })
            self.send_event("initialized")
        elif command == "launch":
            self.current_file = request["arguments"].get("program", "")
            self.send_response(request)
            self.send_event("stopped", {
                "reason": "entry",
                "threadId": 1,
                "allThreadsStopped": True
            })
        elif command == "configurationDone":
            self.send_response(request)
        elif command == "setBreakpoints":
            args = request["arguments"]
            path = args.get("source", {}).get("path", "")
            bps = args.get("breakpoints", [])
            self.breakpoints[path] = [bp["line"] for bp in bps]
            self.send_response(request, {
                "breakpoints": [{"verified": True, "line": bp["line"]} for bp in bps]
            })
        elif command == "threads":
            self.send_response(request, {
                "threads": [{"id": 1, "name": "主线程"}]
            })
        elif command == "stackTrace":
            self.send_response(request, {
                "stackFrames": [
                    {
                        "id": 1,
                        "name": "主程序",
                        "source": {"path": self.current_file},
                        "line": self.current_line,
                        "column": 1
                    }
                ],
                "totalFrames": 1
            })
        elif command == "scopes":
            self.send_response(request, {
                "scopes": [
                    {"name": "局部变量", "variablesReference": 1, "expensive": False},
                    {"name": "全局变量", "variablesReference": 2, "expensive": False}
                ]
            })
        elif command == "variables":
            variables = [
                {"name": k, "value": str(v), "variablesReference": 0}
                for k, v in self.variables.items()
            ]
            self.send_response(request, {"variables": variables})
        elif command == "next":
            self.current_line += 1
            self.send_response(request)
            self.send_event("stopped", {
                "reason": "step",
                "threadId": 1,
                "allThreadsStopped": True
            })
        elif command == "continue":
            self.send_response(request)
            self.send_event("continued", {"threadId": 1, "allThreadsContinued": True})
        elif command == "terminate":
            self.send_response(request)
            self.send_event("terminated")
        else:
            self.send_response(request, {}, f"不支持的命令: {command}")


def start_server(port: int = 4711):
    """启动调试服务器"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('127.0.0.1', port))
        server_socket.listen(5)
        print(f"言语言调试服务器已启动，监听端口: {port}", file=sys.stderr)

        while True:
            conn, addr = server_socket.accept()
            print(f"新连接: {addr}", file=sys.stderr)

            session = DebugSession(conn)
            thread = threading.Thread(target=session.process, daemon=True)
            thread.start()

    except KeyboardInterrupt:
        print("\n服务器已停止", file=sys.stderr)
    finally:
        server_socket.close()


if __name__ == "__main__":
    port = 4711
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    start_server(port)
