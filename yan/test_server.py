#!/usr/bin/env python3
"""测试 Playground 服务器"""

import urllib.request
import json

data = json.dumps({'code': '印 "Hello Yan!"。'}).encode('utf-8')
req = urllib.request.Request('http://localhost:5000/api/execute', data=data, headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req, timeout=30)
print(response.read().decode('utf-8'))