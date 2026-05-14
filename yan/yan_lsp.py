#!/usr/bin/env python3
"""
言语言 LSP 服务器
为编辑器提供语言智能支持
"""

import json
import sys
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path

CONTENT_TYPE = "application/vscode-jsonrpc3"


@dataclass
class TextDocumentItem:
    """文本文档"""
    uri: str
    language_id: str
    version: int
    text: str


@dataclass
class Position:
    """位置"""
    line: int
    character: int


@dataclass
class Range:
    """范围"""
    start: Position
    end: Position


@dataclass
class Diagnostic:
    """诊断信息"""
    range: Range
    severity: int
    message: str
    source: str = "yan"


@dataclass
class ReferenceResult:
    """引用结果"""
    uri: str
    range: Range
    line_text: str


class YanLanguageServer:
    """言语言 LSP 服务器"""

    def __init__(self):
        self.documents: Dict[str, TextDocumentItem] = {}
        self.user_verbs: set = set()
        self.symbols: Dict[str, List[Tuple[str, int, int]]] = {}
        self._build_builtins_docs()

    def _build_builtins_docs(self):
        """构建内置函数文档"""
        self.docs = {
            '加': ('加法', 'a 加 b - 返回 a + b'),
            '减': ('减法', 'a 减 b - 返回 a - b'),
            '乘': ('乘法', 'a 乘 b - 返回 a * b'),
            '除': ('除法', 'a 除 b - 返回 a / b'),
            '模': ('取模', 'a 模 b - 返回 a % b'),
            '幂': ('幂运算', 'a 幂 b - 返回 a ** b'),
            '列': ('列表', '列 1 2 3 - 创建列表 [1, 2, 3]'),
            '函': ('函数', '函 x 加 x 1 - 定义匿名函数'),
            '印': ('打印', '印 "hello" - 打印输出'),
            '引': ('导入', '引 模块名 - 导入模块'),
            '出': ('导出', '出 函数名 - 导出定义'),
            '定': ('定义', '定 x = 10 - 定义变量'),
            '若': ('条件', '若 x 等 1 则 ... - 条件语句'),
            '遍历': ('遍历', '遍历 x 于 列表 - 遍历列表'),
            '断言等': ('断言相等', '断言等 a b - 断言 a == b'),
            '皆': ('映射', '皆 平方 数据 - 映射函数'),
            '只': ('过滤', '只 谓词 数据 - 过滤函数'),
            '归': ('归约', '归 加 0 数据 - 归约函数'),
            '转JSON': ('JSON编码', '转JSON 数据 - JSON编码'),
            '解JSON': ('JSON解码', '解JSON 字符串 - JSON解码'),
            '正弦': ('正弦', '正弦 x - 正弦函数'),
            '余弦': ('余弦', '余弦 x - 余弦函数'),
            '正切': ('正切', '正切 x - 正切函数'),
            '开方': ('平方根', '开方 x - 平方根'),
            '取整': ('向下取整', '取整 x - 向下取整'),
            '进位': ('向上取整', '进位 x - 向上取整'),
            '四舍五入': ('四舍五入', '四舍五入 x - 四舍五入'),
            '随机': ('随机数', '随机 - 返回0-1随机数'),
            '随机整数': ('随机整数', '随机整数 a b - 返回a-b随机整数'),
            '圆周率': ('π', '圆周率 - 返回π值'),
            '自然常数': ('e', '自然常数 - 返回e值'),
            '读文件': ('读文件', '读文件 "path" - 读取文件'),
            '写文件': ('写文件', '写文件 "path" 内容 - 写文件'),
            '存在': ('存在检查', '存在 "path" - 检查文件是否存在'),
            '是文件': ('文件检查', '是文件 "path" - 检查是否为文件'),
            '是目录': ('目录检查', '是目录 "path" - 检查是否为目录'),
            '列目录': ('列目录', '列目录 "path" - 列出目录内容'),
            '建目录': ('建目录', '建目录 "path" - 创建目录'),
            '删文件': ('删文件', '删文件 "path" - 删除文件'),
            '长': ('长度', '长 列表 - 获取长度'),
            '首': ('首元素', '首 列表 - 获取第一个元素'),
            '余': ('剩余列表', '余 列表 - 获取除第一个外的列表'),
            '入': ('索引访问', '入 列表 索引 - 访问元素'),
            '添': ('追加', '添 列表 元素 - 追加元素'),
            '连': ('连接', '连 列表1 列表2 - 连接列表'),
            '含': ('包含检查', '含 列表 元素 - 检查是否包含'),
            '空': ('空检查', '空 列表 - 检查是否为空'),
            '当前时间': ('时间戳', '当前时间 - 返回当前时间戳'),
            '日期': ('日期', '日期 - 返回日期字符串'),
            '时间': ('时间', '时间 - 返回时间字符串'),
            '睡眠': ('睡眠', '睡眠 秒 - 暂停执行'),
            '类型': ('类型', '类型 值 - 返回类型名'),
            '是数': ('数字检查', '是数 x - 检查是否为数字'),
            '是串': ('字符串检查', '是串 x - 检查是否为字符串'),
            '是表': ('列表检查', '是表 x - 检查是否为列表'),
            '是函': ('函数检查', '是函 x - 检查是否为函数'),
            '断言大': ('断言大于', '断言大 a b - 断言 a > b'),
            '断言小': ('断言小于', '断言小 a b - 断言 a < b'),
        }

    def _create_diagnostic(self, line: int, start_char: int, end_char: int,
                         message: str, severity: int = 1) -> Diagnostic:
        """创建诊断信息"""
        return Diagnostic(
            range=Range(
                start=Position(line=line, character=start_char),
                end=Position(line=line, character=end_char)
            ),
            severity=severity,
            message=message,
            source="yan"
        )

    def _find_references(self, text: str, word: str, exclude_line: int = -1) -> List[ReferenceResult]:
        """查找所有引用"""
        references = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines):
            if line_num == exclude_line:
                continue

            pattern = rf'\b{re.escape(word)}\b'
            for match in re.finditer(pattern, line):
                references.append(ReferenceResult(
                    uri="",
                    range=Range(
                        start=Position(line=line_num, character=match.start()),
                        end=Position(line=line_num, character=match.end())
                    ),
                    line_text=line.strip()
                ))

        return references

    def _rename_symbol(self, text: str, word: str, new_name: str, exclude_line: int = -1) -> List[Tuple[int, int, int, str]]:
        """重命名符号，返回需要替换的位置"""
        replacements = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines):
            if line_num == exclude_line:
                continue

            pattern = rf'\b{re.escape(word)}\b'
            for match in re.finditer(pattern, line):
                replacements.append((
                    line_num,
                    match.start(),
                    match.end(),
                    new_name
                ))

        return replacements

    def _get_symbols(self, text: str) -> List[Dict]:
        """提取文档中的符号定义"""
        symbols = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines):
            stripped = line.strip()

            define_pattern = r'^定\s+(\w+)\s*='
            match = re.match(define_pattern, stripped)
            if match:
                symbols.append({
                    'name': match.group(1),
                    'kind': 12,
                    'location': {
                        'uri': '',
                        'range': {
                            'start': {'line': line_num, 'character': 0},
                            'end': {'line': line_num, 'character': len(line)}
                        }
                    }
                })

            lambda_pattern = r'^函\s+(\w+)\s+'
            match = re.match(lambda_pattern, stripped)
            if match:
                symbols.append({
                    'name': match.group(1),
                    'kind': 12,
                    'location': {
                        'uri': '',
                        'range': {
                            'start': {'line': line_num, 'character': 0},
                            'end': {'line': line_num, 'character': len(line)}
                        }
                    }
                })

        return symbols

    def _get_semantic_tokens(self, text: str) -> List[Dict]:
        """获取语义标记（用于语法高亮）"""
        tokens = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines):
            pos = 0
            while pos < len(line):
                if line[pos:].startswith('--'):
                    token_type = "comment"
                    tokens.append({
                        'line': line_num,
                        'startChar': pos,
                        'length': len(line) - pos,
                        'tokenType': 4
                    })
                    break

                if line[pos] == '"':
                    start = pos
                    pos += 1
                    while pos < len(line) and line[pos] != '"':
                        if line[pos] == '\\':
                            pos += 2
                            continue
                        pos += 1
                    if pos < len(line):
                        pos += 1
                    tokens.append({
                        'line': line_num,
                        'startChar': start,
                        'length': pos - start,
                        'tokenType': 6
                    })
                    continue

                if line[pos] == '{{':
                    start = pos
                    pos += 2
                    while pos < len(line) and not line[pos:].startswith('}}'):
                        pos += 1
                    if pos < len(line):
                        pos += 2
                    tokens.append({
                        'line': line_num,
                        'startChar': start,
                        'length': pos - start,
                        'tokenType': 8
                    })
                    continue

                match = re.match(r'^([\u4e00-\u9fff]+)', line[pos:])
                if match:
                    word = match.group(1)
                    if word in self.docs:
                        tokens.append({
                            'line': line_num,
                            'startChar': pos,
                            'length': len(word),
                            'tokenType': 1
                        })
                    pos += len(word)
                    continue

                match = re.match(r'^(\d+\.?\d*)', line[pos:])
                if match:
                    tokens.append({
                        'line': line_num,
                        'startChar': pos,
                        'length': len(match.group(1)),
                        'tokenType': 5
                    })
                    pos += len(match.group(1))
                    continue

                pos += 1

        return tokens

    def _analyze_document(self, text: str) -> List[Diagnostic]:
        """分析文档，返回诊断信息"""
        diagnostics = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines):
            stripped = line.strip()

            if stripped.startswith('--'):
                continue

            if '"' in line:
                in_string = False
                i = 0
                while i < len(line):
                    if line[i] == '"' and (i == 0 or line[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            quote_start = i
                        else:
                            in_string = False
                    i += 1
                if in_string:
                    diagnostics.append(self._create_diagnostic(
                        line_num, quote_start, len(line),
                        "未闭合的字符串",
                        1
                    ))

            if '{{' in line:
                open_count = line.count('{{')
                close_count = line.count('}}')
                if open_count != close_count:
                    for i, c in enumerate(line):
                        if line[i:].startswith('{{'):
                            diagnostics.append(self._create_diagnostic(
                                line_num, i, i + 2,
                                "未闭合的代码块",
                                1
                            ))
                            break

            var_pattern = r'定\s+(\w+)\s*='
            for match in re.finditer(var_pattern, stripped):
                var_name = match.group(1)
                if var_name in self.docs:
                    diagnostics.append(self._create_diagnostic(
                        line_num, match.start(1), match.start(1) + len(var_name),
                        f"变量名 '{var_name}' 与内置函数同名",
                        2
                    ))

            if stripped and not stripped.startswith('--'):
                if '。' not in stripped and '：' not in stripped and stripped not in ['引', '出', '定', '函']:
                    pass

        return diagnostics

    def _get_completions(self, text: str, line: int, character: int) -> List[Dict]:
        """获取自动完成建议"""
        completions = []

        # 内置动词
        builtin_verbs = [
            {'label': '加', 'kind': 1, 'detail': '加法运算', 'documentation': 'a 加 b'},
            {'label': '减', 'kind': 1, 'detail': '减法运算', 'documentation': 'a 减 b'},
            {'label': '乘', 'kind': 1, 'detail': '乘法运算', 'documentation': 'a 乘 b'},
            {'label': '除', 'kind': 1, 'detail': '除法运算', 'documentation': 'a 除 b'},
            {'label': '等', 'kind': 1, 'detail': '比较是否相等', 'documentation': 'a 等 b'},
            {'label': '列', 'kind': 1, 'detail': '创建列表', 'documentation': '列 1 2 3'},
            {'label': '函', 'kind': 1, 'detail': '定义函数', 'documentation': '函 x 加 x 1'},
            {'label': '定', 'kind': 1, 'detail': '定义变量', 'documentation': '定 x = 10'},
            {'label': '印', 'kind': 1, 'detail': '打印输出', 'documentation': '印 "hello"'},
            {'label': '遍历', 'kind': 1, 'detail': '遍历列表', 'documentation': '遍历 x 于 列表'},
            {'label': '若', 'kind': 1, 'detail': '条件语句', 'documentation': '若 x 等 1 则'},
            {'label': '引', 'kind': 1, 'detail': '导入模块', 'documentation': '引 模块名'},
            {'label': '出', 'kind': 1, 'detail': '导出定义', 'documentation': '出 函数名'},
            {'label': '断言等', 'kind': 1, 'detail': '断言相等', 'documentation': '断言等 a b'},
            {'label': '皆', 'kind': 1, 'detail': '映射函数', 'documentation': '皆 平方 数据'},
            {'label': '只', 'kind': 1, 'detail': '过滤函数', 'documentation': '只 谓词 数据'},
            {'label': '归', 'kind': 1, 'detail': '归约函数', 'documentation': '归 加 0 数据'},
            {'label': '转JSON', 'kind': 1, 'detail': 'JSON 编码', 'documentation': '转JSON 数据'},
            {'label': '解JSON', 'kind': 1, 'detail': 'JSON 解码', 'documentation': '解JSON 字符串'},
        ]

        completions.extend(builtin_verbs)

        # 用户定义的动词
        for verb in self.user_verbs:
            completions.append({
                'label': verb,
                'kind': 1,
                'detail': '用户定义函数',
                'documentation': f'定 {verb} = 函 ...'
            })

        return completions

    def _find_definitions(self, text: str, line: int, character: int) -> List[Dict]:
        """查找定义位置"""
        # 这里简化处理，实际应该解析 AST
        definitions = []
        return definitions

    def _get_hover(self, text: str, line: int, character: int) -> Optional[Dict]:
        """获取悬停信息"""
        lines = text.split('\n')
        if line >= len(lines):
            return None

        line_text = lines[line]

        # 查找当前单词
        word_start = character
        while word_start > 0 and (line_text[word_start-1].isalnum() or line_text[word_start-1] in '_-'):
            word_start -= 1

        word_end = character
        while word_end < len(line_text) and (line_text[word_end].isalnum() or line_text[word_end] in '_-'):
            word_end += 1

        word = line_text[word_start:word_end]

        # 内置函数文档
        docs = {
            '加': ('加法', 'a 加 b - 返回 a + b'),
            '减': ('减法', 'a 减 b - 返回 a - b'),
            '乘': ('乘法', 'a 乘 b - 返回 a * b'),
            '除': ('除法', 'a 除 b - 返回 a / b'),
            '列': ('列表', '列 1 2 3 - 创建列表 [1, 2, 3]'),
            '函': ('函数', '函 x 加 x 1 - 定义匿名函数'),
            '印': ('打印', '印 "hello" - 打印输出'),
            '引': ('导入', '引 模块名 - 导入模块'),
            '出': ('导出', '出 函数名 - 导出定义'),
        }

        if word in docs:
            title, desc = docs[word]
            return {
                'contents': {
                    'kind': 'markdown',
                    'value': f'**{title}**\n\n{desc}'
                }
            }

        return None

    def handle_request(self, method: str, params: Any) -> Any:
        """处理 LSP 请求"""
        if method == "initialize":
            return {
                "capabilities": {
                    "textDocumentSync": 1,  # 完整文档
                    "completionProvider": {
                        "triggerCharacters": [" ", "定", "函", "印"]
                    },
                    "definitionProvider": True,
                    "hoverProvider": True,
                    "diagnosticProvider": {
                        "interFileDependencies": False,
                        "workspaceDiagnostics": False
                    }
                },
                "serverInfo": {
                    "name": "Yan Language Server",
                    "version": "0.1.0"
                }
            }

        elif method == "textDocument/didOpen":
            doc = params['textDocument']
            self.documents[doc['uri']] = TextDocumentItem(
                uri=doc['uri'],
                language_id=doc['languageId'],
                version=doc['version'],
                text=doc['text']
            )

            # 发送诊断信息
            diagnostics = self._analyze_document(doc['text'])
            return {
                "method": "textDocument/publishDiagnostics",
                "params": {
                    "uri": doc['uri'],
                    "diagnostics": [
                        {
                            "range": {
                                "start": {"line": d.range.start.line, "character": d.range.start.character},
                                "end": {"line": d.range.end.line, "character": d.range.end.character}
                            },
                            "severity": d.severity,
                            "message": d.message,
                            "source": d.source
                        }
                        for d in diagnostics
                    ]
                }
            }

        elif method == "textDocument/didChange":
            doc = params['textDocument']
            if doc['uri'] in self.documents:
                self.documents[doc['uri']].text = params['contentChanges'][0]['text']
                self.documents[doc['uri']].version += 1

                # 重新分析并发送诊断
                diagnostics = self._analyze_document(params['contentChanges'][0]['text'])
                return {
                    "method": "textDocument/publishDiagnostics",
                    "params": {
                        "uri": doc['uri'],
                        "diagnostics": [
                            {
                                "range": {
                                    "start": {"line": d.range.start.line, "character": d.range.start.character},
                                    "end": {"line": d.range.end.line, "character": d.range.end.character}
                                },
                                "severity": d.severity,
                                "message": d.message,
                                "source": d.source
                            }
                            for d in diagnostics
                        ]
                    }
                }

        elif method == "textDocument/completion":
            doc_uri = params['textDocument']['uri']
            if doc_uri not in self.documents:
                return []

            doc = self.documents[doc_uri]
            line = params['position']['line']
            character = params['position']['character']

            return self._get_completions(doc.text, line, character)

        elif method == "textDocument/definition":
            doc_uri = params['textDocument']['uri']
            if doc_uri not in self.documents:
                return []

            doc = self.documents[doc_uri]
            line = params['position']['line']
            character = params['position']['character']

            return self._find_definitions(doc.text, line, character)

        elif method == "textDocument/hover":
            doc_uri = params['textDocument']['uri']
            if doc_uri not in self.documents:
                return None

            doc = self.documents[doc_uri]
            line = params['position']['line']
            character = params['position']['character']

            return self._get_hover(doc.text, line, character)

        elif method == "textDocument/references":
            doc_uri = params['textDocument']['uri']
            if doc_uri not in self.documents:
                return []

            doc = self.documents[doc_uri]
            line = params['position']['line']
            character = params['position']['character']

            word = self._get_word_at_position(doc.text, line, character)
            if not word:
                return []

            refs = self._find_references(doc.text, word, exclude_line=line)
            return [
                {
                    'uri': doc_uri,
                    'range': {
                        'start': {'line': r.range.start.line, 'character': r.range.start.character},
                        'end': {'line': r.range.end.line, 'character': r.range.end.character}
                    }
                }
                for r in refs
            ]

        elif method == "textDocument/rename":
            doc_uri = params['textDocument']['uri']
            if doc_uri not in self.documents:
                return None

            doc = self.documents[doc_uri]
            line = params['position']['line']
            character = params['position']['character']
            new_name = params.get('newName', '')

            if not new_name:
                return None

            word = self._get_word_at_position(doc.text, line, character)
            if not word:
                return None

            replacements = self._rename_symbol(doc.text, word, new_name, exclude_line=line)

            changes = {}
            for line_num, start, end, name in replacements:
                if doc_uri not in changes:
                    changes[doc_uri] = []
                changes[doc_uri].append({
                    'range': {
                        'start': {'line': line_num, 'character': start},
                        'end': {'line': line_num, 'character': end}
                    },
                    'newText': name
                })

            return {'changes': changes}

        elif method == "textDocument/documentSymbol":
            doc_uri = params.get('textDocument', {}).get('uri')
            if doc_uri not in self.documents:
                return []

            doc = self.documents[doc_uri]
            return self._get_symbols(doc.text)

        elif method == "textDocument/semanticTokens/full":
            doc_uri = params.get('textDocument', {}).get('uri')
            if doc_uri not in self.documents:
                return {'data': []}

            doc = self.documents[doc_uri]
            tokens = self._get_semantic_tokens(doc.text)

            data = []
            for token in tokens:
                data.extend([
                    token['line'],
                    token['startChar'],
                    token['length'],
                    token['tokenType'],
                    0
                ])

            return {'data': data}

        return None

    def _get_word_at_position(self, text: str, line: int, character: int) -> Optional[str]:
        """获取指定位置的单词"""
        lines = text.split('\n')
        if line >= len(lines):
            return None

        line_text = lines[line]

        if character >= len(line_text):
            return None

        start = character
        while start > 0 and (line_text[start-1].isalnum() or line_text[start-1] in '_-'):
            start -= 1

        end = character
        while end < len(line_text) and (line_text[end].isalnum() or line_text[end] in '_-'):
            end += 1

        if start == end:
            return None

        return line_text[start:end]


def main():
    """LSP 服务器主循环"""
    server = YanLanguageServer()

    while True:
        try:
            # 读取请求
            line = sys.stdin.readline()
            if not line:
                break

            # 跳过空行
            line = line.strip()
            if not line:
                continue

            # 解析 JSON-RPC 请求
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                continue

            method = request.get("method")
            params = request.get("params")
            msg_id = request.get("id")

            # 处理请求
            result = server.handle_request(method, params)

            # 发送响应
            if msg_id is not None:
                if result and isinstance(result, dict) and 'method' in result:
                    # 这是个通知，不需要响应
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

            # 刷新输出
            sys.stdout.flush()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
