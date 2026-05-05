"""
言语言 Markdown 解析器
支持文学编程模式：Markdown 文档 + 言语言代码块
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MDNode:
    """Markdown 节点基类"""
    pass


@dataclass
class MDText(MDNode):
    """普通文本"""
    content: str


@dataclass
class MDHeading(MDNode):
    """标题"""
    level: int
    content: str


@dataclass
class MDCodeBlock(MDNode):
    """代码块"""
    lang: str  # 语言标识（yan, python, etc.）
    code: str


@dataclass
class MDInlineCode(MDNode):
    """内联代码"""
    code: str


@dataclass
class MDMath(MDNode):
    """数学公式"""
    expr: str
    inline: bool  # True: $...$, False: $$...$$


@dataclass
class MDDocument(MDNode):
    """Markdown 文档"""
    nodes: List[MDNode]


class MDParser:
    """Markdown 解析器"""

    def __init__(self):
        self.pos = 0
        self.source = ""

    def parse(self, source: str) -> MDDocument:
        """解析 Markdown 文档"""
        self.source = source
        self.pos = 0
        nodes = []

        while self.pos < len(self.source):
            node = self._parse_node()
            if node:
                nodes.append(node)

        return MDDocument(nodes)

    def _parse_node(self) -> Optional[MDNode]:
        """解析单个节点"""
        # 跳过空白
        self._skip_whitespace()

        if self.pos >= len(self.source):
            return None

        # 标题（必须在行首）
        if self._peek(0) == '#' and (self.pos == 0 or self.source[self.pos-1] == '\n'):
            return self._parse_heading()

        # 代码块
        if self.source[self.pos:self.pos+3] == '```':
            self.pos += 3
            return self._parse_code_block()

        # 块级公式
        if self.source[self.pos:self.pos+2] == '$$':
            self.pos += 2
            return self._parse_math_block()

        # 行内公式（单个 $，后面不是 $）
        if self._peek(0) == '$' and self._peek(1) != '$':
            return self._parse_math_inline()

        # 内联代码（单个 `，后面不是 `）
        if self._peek(0) == '`' and self._peek(1) != '`':
            return self._parse_inline_code()

        # 普通文本
        return self._parse_text()

    def _peek(self, offset: int = 0) -> str:
        """查看字符"""
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return ''

    def _match(self, s: str) -> bool:
        """匹配字符串"""
        if self.source[self.pos:self.pos + len(s)] == s:
            self.pos += len(s)
            return True
        return False

    def _skip_whitespace(self):
        """跳过行首空白"""
        while self.pos < len(self.source) and self.source[self.pos] in ' \t':
            self.pos += 1

    def _parse_heading(self) -> MDHeading:
        """解析标题"""
        level = 0
        while self._peek(0) == '#':
            level += 1
            self.pos += 1

        # 跳过空格
        while self._peek(0) == ' ':
            self.pos += 1

        # 读取标题内容
        content = ""
        while self.pos < len(self.source) and self._peek(0) != '\n':
            content += self.source[self.pos]
            self.pos += 1

        # 跳过换行
        if self._peek(0) == '\n':
            self.pos += 1

        return MDHeading(level, content.strip())

    def _parse_code_block(self) -> MDCodeBlock:
        """解析代码块"""
        # 读取语言标识
        lang = ""
        while self.pos < len(self.source) and self._peek(0) not in '\n\r':
            lang += self.source[self.pos]
            self.pos += 1

        lang = lang.strip() or "text"

        # 跳过换行
        if self._peek(0) in '\r\n':
            self.pos += 1
            if self._peek(-1) == '\r' and self._peek(0) == '\n':
                self.pos += 1

        # 读取代码内容
        code = ""
        while self.pos < len(self.source):
            if self._match('```'):
                break
            code += self.source[self.pos]
            self.pos += 1

        # 跳过换行
        if self._peek(0) == '\n':
            self.pos += 1

        return MDCodeBlock(lang, code.strip())

    def _parse_math_block(self) -> MDMath:
        """解析块级公式 $$...$$"""
        expr = ""
        while self.pos < len(self.source):
            if self._match('$$'):
                break
            expr += self.source[self.pos]
            self.pos += 1

        # 跳过换行
        if self._peek(0) == '\n':
            self.pos += 1

        return MDMath(expr.strip(), inline=False)

    def _parse_math_inline(self) -> MDMath:
        """解析行内公式 $...$"""
        self.pos += 1  # 跳过 $

        expr = ""
        while self.pos < len(self.source) and self._peek(0) != '$':
            expr += self.source[self.pos]
            self.pos += 1

        if self._peek(0) == '$':
            self.pos += 1

        return MDMath(expr.strip(), inline=True)

    def _parse_inline_code(self) -> MDInlineCode:
        """解析内联代码 `...`"""
        self.pos += 1  # 跳过 `

        code = ""
        while self.pos < len(self.source) and self._peek(0) != '`':
            code += self.source[self.pos]
            self.pos += 1

        if self._peek(0) == '`':
            self.pos += 1

        return MDInlineCode(code)

    def _parse_text(self) -> MDText:
        """解析普通文本"""
        text = ""
        while self.pos < len(self.source):
            ch = self._peek(0)

            # 遇到特殊标记则停止
            if ch in '#$`':
                # 检查是否是代码块或块级公式
                if self.source[self.pos:self.pos + 3] == '```':
                    break
                if self.source[self.pos:self.pos + 2] == '$$':
                    break
                # 单个 # 可能是标题，检查是否在行首
                if ch == '#' and (len(text) == 0 or text.endswith('\n')):
                    break
                # 单个 $ 或 ` 继续读取
                if ch == '$' and self._peek(1) != '$':
                    break
                if ch == '`' and self._peek(1) != '`':
                    break

            text += ch
            self.pos += 1

        return MDText(text)


def parse_markdown(source: str) -> MDDocument:
    """解析 Markdown 文档"""
    parser = MDParser()
    return parser.parse(source)
