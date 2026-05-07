"""
言语言 AST 节点定义
"""

from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class Node:
    """AST 节点基类"""
    pass


@dataclass
class Num(Node):
    """数字字面量"""
    value: float | int


@dataclass
class Str(Node):
    """字符串字面量"""
    value: str


@dataclass
class Bool(Node):
    """布尔值"""
    value: bool


@dataclass
class Nil(Node):
    """空值"""
    pass


@dataclass
class MathExpr(Node):
    """数学表达式（中缀表达式，直接嵌入 Python）"""
    expr: str


@dataclass
class PythonCode(Node):
    """Python 代码块"""
    code: str


@dataclass
class ListLiteral(Node):
    """列表字面量"""
    elements: List[Node]


@dataclass
class Word(Node):
    """动词/标识符"""
    name: str


@dataclass
class Call(Node):
    """函数调用"""
    verb: Word
    args: List[Node]
    is_partial: bool = False


@dataclass
class Pipeline(Node):
    """管道结构"""
    steps: List[Node]


@dataclass
class Quote(Node):
    """引用（未求值的 AST）"""
    expr: Node


@dataclass
class Define(Node):
    """变量/函数定义"""
    name: str
    value: Node


@dataclass
class Lambda(Node):
    """匿名函数"""
    params: List[str]
    body: Node


@dataclass
class Block(Node):
    """代码块（多个语句）"""
    statements: List[Node]


@dataclass
class If(Node):
    """条件分支"""
    cond: Node
    then_branch: Node
    else_branch: Optional[Node] = None


@dataclass
class ForEach(Node):
    """遍历循环"""
    var: str
    iterable: Node
    body: Node


@dataclass
class While(Node):
    """当循环"""
    cond: Node
    body: Node


@dataclass
class Program(Node):
    """程序（多个语句）"""
    statements: List[Node]
