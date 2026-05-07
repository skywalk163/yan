"""
言语言 Markdown 解析器 v2
支持作用域系统和多语言代码块
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class YanMDNode:
    """节点基类"""
    pass


@dataclass
class YanMDText(YanMDNode):
    """普通文本"""
    content: str


@dataclass
class YanMDHeading(YanMDNode):
    """标题（定义作用域）"""
    level: int
    content: str


@dataclass
class YanMDCodeBlock(YanMDNode):
    """代码块"""
    lang: str  # yan, python, lisp, etc.
    code: str


@dataclass
class YanMDInlineCode(YanMDNode):
    """内联代码"""
    code: str


@dataclass
class YanMDMath(YanMDNode):
    """数学公式"""
    expr: str
    inline: bool


@dataclass
class YanMDBlockquote(YanMDNode):
    """引用块"""
    content: str


@dataclass
class YanMDList(YanMDNode):
    """列表"""
    items: List[str]
    ordered: bool = False


@dataclass
class YanMDScope(YanMDNode):
    """作用域块"""
    level: int
    name: str
    children: List[YanMDNode] = field(default_factory=list)


@dataclass
class YanMDDocument(YanMDNode):
    """文档"""
    children: List[YanMDNode] = field(default_factory=list)


class YanMDParser:
    """言语言 Markdown 解析器"""

    def __init__(self):
        self.pos = 0
        self.source = ""
        self.line = 1
        self.col = 1

    def parse(self, source: str) -> YanMDDocument:
        """解析 Markdown 文档"""
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1

        nodes = self._parse_document()
        return YanMDDocument(nodes)

    def _parse_document(self) -> List[YanMDNode]:
        """解析文档内容"""
        nodes = []
        
        while self.pos < len(self.source):
            node = self._parse_node()
            if node:
                nodes.append(node)

        return nodes

    def _parse_node(self) -> Optional[YanMDNode]:
        """解析单个节点"""
        self._skip_blank_lines()

        if self.pos >= len(self.source):
            return None

        # 标题
        if self._peek(0) == '#':
            return self._parse_heading()

        # 代码块
        if self._match('```'):
            return self._parse_code_block()

        # 块级公式
        if self._match('$$'):
            return self._parse_math_block()

        # 引用块
        if self._peek(0) == '>':
            return self._parse_blockquote()

        # 列表
        if self._peek(0) in '-*0123456789':
            return self._parse_list()

        # 普通文本
        return self._parse_text()

    def _peek(self, offset: int = 0) -> str:
        """查看字符"""
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else ''

    def _match(self, s: str) -> bool:
        """匹配字符串"""
        if self.source[self.pos:self.pos + len(s)] == s:
            self._advance(len(s))
            return True
        return False

    def _advance(self, n: int = 1):
        """前进 n 个字符"""
        for _ in range(n):
            if self.pos < len(self.source):
                if self.source[self.pos] == '\n':
                    self.line += 1
                    self.col = 1
                else:
                    self.col += 1
                self.pos += 1

    def _skip_blank_lines(self):
        """跳过空行"""
        while self.pos < len(self.source):
            # 跳过空格和制表符
            while self._peek(0) in ' \t':
                self._advance()
            # 如果是换行，跳过
            if self._peek(0) == '\n':
                self._advance()
            else:
                break

    def _skip_line(self):
        """跳过当前行剩余内容"""
        while self.pos < len(self.source) and self._peek(0) != '\n':
            self._advance()
        if self._peek(0) == '\n':
            self._advance()

    def _read_line(self) -> str:
        """读取当前行"""
        start = self.pos
        while self.pos < len(self.source) and self._peek(0) != '\n':
            self._advance()
        line = self.source[start:self.pos]
        if self._peek(0) == '\n':
            self._advance()
        return line

    def _parse_heading(self) -> YanMDHeading:
        """解析标题"""
        level = 0
        while self._peek(0) == '#':
            level += 1
            self._advance()

        # 跳过空格
        while self._peek(0) == ' ':
            self._advance()

        # 读取标题内容
        content = self._read_line().strip()

        return YanMDHeading(level, content)

    def _parse_code_block(self) -> YanMDCodeBlock:
        """解析代码块"""
        # 读取语言标识
        lang = ""
        while self.pos < len(self.source) and self._peek(0) not in '\n\r':
            lang += self._peek(0)
            self._advance()

        lang = lang.strip() or "text"

        # 跳过换行
        if self._peek(0) in '\r\n':
            self._advance()
            if self._peek(-1) == '\r' and self._peek(0) == '\n':
                self._advance()

        # 读取代码内容
        code_lines = []
        while self.pos < len(self.source):
            # 检查是否结束
            if self.source[self.pos:self.pos + 3] == '```':
                self._advance(3)
                break
            
            # 读取一行
            line = ""
            while self.pos < len(self.source) and self._peek(0) != '\n':
                line += self._peek(0)
                self._advance()
            code_lines.append(line)
            
            if self._peek(0) == '\n':
                self._advance()

        # 移除末尾空行
        while code_lines and not code_lines[-1].strip():
            code_lines.pop()

        code = '\n'.join(code_lines)
        return YanMDCodeBlock(lang, code)

    def _parse_math_block(self) -> YanMDMath:
        """解析块级公式"""
        expr_lines = []
        while self.pos < len(self.source):
            if self.source[self.pos:self.pos + 2] == '$$':
                self._advance(2)
                break
            
            line = ""
            while self.pos < len(self.source) and self._peek(0) != '\n':
                line += self._peek(0)
                self._advance()
            expr_lines.append(line)
            
            if self._peek(0) == '\n':
                self._advance()

        expr = '\n'.join(expr_lines).strip()
        return YanMDMath(expr, inline=False)

    def _parse_blockquote(self) -> YanMDBlockquote:
        """解析引用块"""
        lines = []
        while self.pos < len(self.source):
            # 跳过空格
            while self._peek(0) in ' \t':
                self._advance()
            
            # 检查是否是引用行
            if self._peek(0) != '>':
                break
            
            self._advance()  # 跳过 >
            if self._peek(0) == ' ':
                self._advance()
            
            line = self._read_line().rstrip()
            lines.append(line)

        content = '\n'.join(lines)
        return YanMDBlockquote(content)

    def _parse_list(self) -> YanMDList:
        """解析列表"""
        items = []
        ordered = self._peek(0).isdigit()

        while self.pos < len(self.source):
            # 跳过空格
            indent = 0
            while self._peek(0) in ' \t':
                self._advance()
                indent += 1

            # 检查列表标记
            if self._peek(0) == '-' or self._peek(0) == '*':
                self._advance()
                if self._peek(0) == ' ':
                    self._advance()
            elif self._peek(0).isdigit():
                while self._peek(0).isdigit():
                    self._advance()
                if self._peek(0) == '.':
                    self._advance()
                if self._peek(0) == ' ':
                    self._advance()
            else:
                break

            # 读取列表项
            item = self._read_line().strip()
            items.append(item)

        return YanMDList(items, ordered)

    def _parse_text(self) -> YanMDText:
        """解析普通文本"""
        lines = []
        
        while self.pos < len(self.source):
            # 检查是否遇到特殊结构
            if self._peek(0) == '#' or self._peek(0) == '>':
                break
            if self.source[self.pos:self.pos + 3] == '```':
                break
            if self.source[self.pos:self.pos + 2] == '$$':
                break
            if self._peek(0) in '-*0123456789':
                # 可能是列表，检查下一字符
                next_char = self._peek(1)
                if next_char == ' ' or next_char == '.':
                    break

            line = self._read_line()
            lines.append(line)

            # 空行结束段落
            if not line.strip():
                break

        content = '\n'.join(lines)
        return YanMDText(content)


def parse_yanmd(source: str) -> YanMDDocument:
    """解析言语言 Markdown 文档"""
    parser = YanMDParser()
    return parser.parse(source)


def build_scope_tree(doc: YanMDDocument) -> YanMDScope:
    """将文档转换为作用域树"""
    root = YanMDScope(level=0, name="root", children=[])
    scope_stack = [root]

    for node in doc.children:
        if isinstance(node, YanMDHeading):
            # 创建新作用域
            new_scope = YanMDScope(level=node.level, name=node.content, children=[])

            # 弹出栈直到找到父作用域
            while len(scope_stack) > 1 and scope_stack[-1].level >= node.level:
                scope_stack.pop()

            # 添加到当前作用域
            scope_stack[-1].children.append(new_scope)
            scope_stack.append(new_scope)

        else:
            # 添加到当前作用域
            scope_stack[-1].children.append(node)

    return root


if __name__ == "__main__":
    # 测试
    test_source = """# 数学工具库

本文档定义了一些常用的数学函数。

## 基础运算

```yan
定圆周率=3.14159。
定平方=函x乘x x。
```

## 几何计算

```yan
定面积=函r圆周率乘平方r。
印面积5。
```

# 另一个模块

```python
print("Hello from Python")
```
"""

    doc = parse_yanmd(test_source)
    
    print("=== 解析结果 ===")
    for node in doc.children:
        print(f"  {type(node).__name__}: {node}")
    
    print("\n=== 作用域树 ===")
    scope_tree = build_scope_tree(doc)
    
    def print_scope(scope: YanMDScope, indent: int = 0):
        print("  " * indent + f"[{scope.level}] {scope.name}")
        for child in scope.children:
            if isinstance(child, YanMDScope):
                print_scope(child, indent + 1)
            else:
                print("  " * (indent + 1) + f"- {type(child).__name__}")
    
    print_scope(scope_tree)
