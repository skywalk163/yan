#!/usr/bin/env python3
"""
言语言 VS Code LSP 服务器入口
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yan_lsp import YanLanguageServer


def main():
    server = YanLanguageServer()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue

            method = request.get("method")
            params = request.get("params")
            msg_id = request.get("id")

            result = server.handle_request(method, params)

            if msg_id is not None:
                if result and isinstance(result, dict) and 'method' in result:
                    response = json.dumps({
                        "jsonrpc": "2.0",
                        "method": result['method'],
                        "params": result['params']
                    })
                    print(response)
                else:
                    response = json.dumps({
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": result or {}
                    })
                    print(response)

            sys.stdout.flush()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
