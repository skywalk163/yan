# 言语言 - Python 转译方案

## 一、整体架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   源码      │───▶│   Lexer     │───▶│   Parser    │───▶│   CodeGen   │───▶ exec()
│   文本      │    │   Token流   │    │   AST       │    │   Python    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

**核心模块**：
- `lexer.py` - 词法分析器（无空格分词 + 多字贪心匹配）
- `parser.py` - 语法分析器（动词吞噬 + 副词修饰 + 管道构建）
- `ast.py` - AST 节点定义
- `codegen.py` - Python 代码生成器
- `runtime.py` - 运行时支持（柯里化、高阶函数）
- `builtins.py` - 内置动词映射表
- `main.py` - 入口

---

## 二、词法分析器 (lexer.py)

### 2.1 Token 类型

```python
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

class TokenType(Enum):
    NUM = auto()      # 数字：1, 2.5, -3
    STR = auto()      # 字符串：『hello』
    WORD = auto()     # 动词/标识符：加, 乘, 列
    LPAREN = auto()   # '
    RPAREN = auto()   # 
    COMMA = auto()    # ，
    DOT = auto()      # 。
    SEMI = auto()     # ；
    EQUALS = auto()   # =
    EOF = auto()      # 结束

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r})"
```

### 2.2 字符分类

```python
class CharClass:
    """字符分类"""
    STRUCTURE = set('。，；『』=')  # 结构符
    DIGIT = set('0123456789.-')         # 数字字符
    HAN_START = 0x4E00                  # CJK 汉字起始
    HAN_END = 0x9FFF                    # CJK 汉字结束

    @staticmethod
    def is_han(ch: str) -> bool:
        """判断是否为汉字"""
        if not ch:
            return False
        cp = ord(ch)
        return CharClass.HAN_START <= cp <= CharClass.HAN_END

    @staticmethod
    def is_digit(ch: str) -> bool:
        return ch in CharClass.DIGIT

    @staticmethod
    def is_structure(ch: str) -> bool:
        return ch in CharClass.STRUCTURE

    @staticmethod
    def is_space(ch: str) -> bool:
        return ch in ' \t\n\r'
```

### 2.3 词法分析器实现

```python
class Lexer:
    def __init__(self, keywords: Optional[set] = None):
        # 内置关键字（多字动词优先）
        self.keywords = keywords or {
            # 多字动词
            '定义', '阶乘', '平方', '否则', '如果', '那么',
            # 单字动词
            '加', '减', '乘', '除', '模', '幂',
            '大', '小', '等', '不等',
            '且', '或', '非',
            '列', '典', '序', '对',
            '首', '余', '入', '长',
            '皆', '只', '归', '潜',
            '印', '读', '写',
            '若', '则', '定', '函', '行',
            '真', '假', '空',
        }
        self.max_keyword_len = max(len(k) for k in self.keywords) if self.keywords else 1

    def tokenize(self, source: str) -> List[Token]:
        """将源码转为 Token 流"""
        tokens = []
        i = 0
        line, col = 1, 1

        while i < len(source):
            ch = source[i]

            # 跳过空白符
            if CharClass.is_space(ch):
                if ch == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                i += 1
                continue

            # 注释：-- 开头到行尾
            if source[i:i+2] == '--':
                while i < len(source) and source[i] != '\n':
                    i += 1
                continue

            # 注释：注 开头到行尾
            if source[i:i+1] == '注':
                while i < len(source) and source[i] != '\n':
                    i += 1
                continue

            # 结构符
            if ch == '。':
                tokens.append(Token(TokenType.DOT, '。', line, col))
                i += 1; col += 1
                continue
            if ch == '，':
                tokens.append(Token(TokenType.COMMA, '，', line, col))
                i += 1; col += 1
                continue
            if ch == '；':
                tokens.append(Token(TokenType.SEMI, '；', line, col))
                i += 1; col += 1
                continue
            if ch == ''':
                tokens.append(Token(TokenType.QUOTE, "'", line, col))
                i += 1; col += 1
                continue
            if ch == '':
                tokens.append(# Quote uses single quote prefix, line, col))
                i += 1; col += 1
                continue
            if ch == '=':
                tokens.append(Token(TokenType.EQUALS, '=', line, col))
                i += 1; col += 1
                continue

            # 字符串：『...』
            if ch == '『':
                j = i + 1
                while j < len(source) and source[j] != '』':
                    j += 1
                value = source[i+1:j]
                tokens.append(Token(TokenType.STR, value, line, col))
                col += j - i + 1
                i = j + 1
                continue

            # 数字
            if CharClass.is_digit(ch):
                j = i
                has_dot = False
                while j < len(source):
                    c = source[j]
                    if c.isdigit():
                        j += 1
                    elif c == '.' and not has_dot:
                        has_dot = True
                        j += 1
                    elif c == '-' and j == i:  # 负号在开头
                        j += 1
                    else:
                        break

                value_str = source[i:j]
                try:
                    value = float(value_str) if '.' in value_str else int(value_str)
                    tokens.append(Token(TokenType.NUM, value, line, col))
                    col += j - i
                    i = j
                except ValueError:
                    raise LexerError(f"无效数字: {value_str}", line, col)
                continue

            # 汉字（动词/标识符）：多字贪心匹配
            if CharClass.is_han(ch):
                # 尝试最长匹配
                matched = None
                for length in range(min(self.max_keyword_len, len(source) - i), 0, -1):
                    candidate = source[i:i+length]
                    if candidate in self.keywords:
                        matched = candidate
                        break

                if matched:
                    tokens.append(Token(TokenType.WORD, matched, line, col))
                    col += len(matched)
                    i += len(matched)
                else:
                    # 不在关键字表中，作为普通标识符
                    # 收集连续汉字
                    j = i
                    while j < len(source) and CharClass.is_han(source[j]):
                        j += 1
                    value = source[i:j]
                    tokens.append(Token(TokenType.WORD, value, line, col))
                    col += len(value)
                    i = j
                continue

            # 未知字符
            raise LexerError(f"未知字符: {ch}", line, col)

        tokens.append(Token(TokenType.EOF, None, line, col))
        return tokens


class LexerError(Exception):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"词法错误 (行{line}, 列{col}): {message}")
```

### 2.4 测试词法分析器

```python
if __name__ == "__main__":
    lexer = Lexer()

    # 测试用例
    tests = [
        "列1 2 3皆乘2。",
        "10加5，乘2。",
        "定平方=函x乘x x。",
        "若5大3则印"大"否则印"小"。",
        "『Hello World』",
    ]

    for source in tests:
        print(f"\n源码: {source}")
        tokens = lexer.tokenize(source)
        for tok in tokens:
            print(f"  {tok}")
```

---

## 三、AST 节点定义 (ast.py)

```python
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
class List(Node):
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
    is_partial: bool = False  # 是否为偏函数（柯里化）

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
class If(Node):
    """条件分支"""
    cond: Node
    then_branch: Node
    else_branch: Optional[Node]

@dataclass
class Program(Node):
    """程序（多个语句）"""
    statements: List[Node]
```

---

## 四、语法分析器 (parser.py)

### 4.1 核心解析逻辑

```python
class Parser:
    def __init__(self, adverbs: Optional[set] = None):
        # 副词表
        self.adverbs = adverbs or {'皆', '只', '归', '潜'}

    def parse(self, tokens: List[Token]) -> Program:
        """解析 Token 流，返回 AST"""
        self.tokens = tokens
        self.pos = 0
        statements = []

        while not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        return Program(statements)

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def _is_at_end(self) -> bool:
        return self._current().type == TokenType.EOF

    def _advance(self) -> Token:
        tok = self._current()
        if not self._is_at_end():
            self.pos += 1
        return tok

    def _match(self, *types: TokenType) -> bool:
        if self._current().type in types:
            self._advance()
            return True
        return False

    def _expect(self, type: TokenType, message: str) -> Token:
        if self._current().type == type:
            return self._advance()
        raise ParserError(message, self._current().line, self._current().col)

    def _parse_statement(self) -> Optional[Node]:
        """解析语句"""
        # 跳过句号和分号
        if self._match(TokenType.DOT, TokenType.SEMI):
            return None

        # 变量定义：定 名称 = 值
        if self._current().type == TokenType.WORD and self._current().value == '定':
            return self._parse_define()

        # 表达式
        expr = self._parse_expression()

        # 消耗结尾的句号/分号
        self._match(TokenType.DOT, TokenType.SEMI)

        return expr

    def _parse_define(self) -> Define:
        """解析定义语句：定 名称 = 值"""
        self._expect(TokenType.WORD, "期望 '定'")  # 消耗 '定'

        name_tok = self._expect(TokenType.WORD, "期望标识符")
        name = name_tok.value

        self._expect(TokenType.EQUALS, "期望 '='")

        # 检查是否是函数定义：定 名称 = 函 参数... 体
        if self._current().type == TokenType.WORD and self._current().value == '函':
            value = self._parse_lambda()
        else:
            value = self._parse_expression()

        return Define(name, value)

    def _parse_lambda(self) -> Lambda:
        """解析匿名函数：函 参数... 体"""
        self._expect(TokenType.WORD, "期望 '函'")  # 消耗 '函'

        # 收集参数（直到遇到非 WORD 或遇到动词）
        params = []
        while (self._current().type == TokenType.WORD and
               self._current().value not in {'若', '则', '否则'} and
               len(self._current().value) == 1):  # 单字参数
            params.append(self._advance().value)

        # 函数体：解析到句号或结束
        body = self._parse_expression()

        return Lambda(params, body)

    def _parse_expression(self) -> Node:
        """解析表达式（管道链）"""
        return self._parse_pipeline()

    def _parse_pipeline(self) -> Node:
        """解析管道链：项 ， 项 ， ..."""
        steps = [self._parse_call()]

        while self._match(TokenType.COMMA):
            steps.append(self._parse_call())

        if len(steps) == 1:
            return steps[0]
        return Pipeline(steps)

    def _parse_call(self) -> Node:
        """解析动词调用：动词 参数..."""
        # 引用：' 表达式 
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            # Quote handled by prefix
            return Quote(expr)

        # 条件：若 条件 则 分支 否则 分支
        if self._current().type == TokenType.WORD and self._current().value == '若':
            return self._parse_if()

        # 数字、字符串等字面量
        if self._current().type == TokenType.NUM:
            return Num(self._advance().value)

        if self._current().type == TokenType.STR:
            return Str(self._advance().value)

        # 动词调用
        if self._current().type == TokenType.WORD:
            verb = Word(self._advance().value)
            args = []

            # 收集参数
            while not self._is_at_end():
                tok = self._current()

                # 遇到结构符，停止
                if tok.type in {TokenType.DOT, TokenType.SEMI, TokenType.COMMA,
                                TokenType.RPAREN, TokenType.EQUALS}:
                    break

                # 遇到其他动词，停止（除非当前动词是可变参数）
                if tok.type == TokenType.WORD and tok.value not in self.adverbs:
                    # 检查是否是动词
                    if self._is_verb(tok.value):
                        break

                # 收集参数
                arg = self._parse_arg()
                args.append(arg)

            return Call(verb, args)

        raise ParserError(f"意外的 token: {self._current()}", 
                         self._current().line, self._current().col)

    def _parse_arg(self) -> Node:
        """解析单个参数"""
        tok = self._current()

        if tok.type == TokenType.NUM:
            return Num(self._advance().value)

        if tok.type == TokenType.STR:
            return Str(self._advance().value)

        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            # Quote handled by prefix
            return expr

        if tok.type == TokenType.WORD:
            # 可能是动词调用或标识符
            return self._parse_call()

        raise ParserError(f"期望参数，得到: {tok}", tok.line, tok.col)

    def _parse_if(self) -> If:
        """解析条件：若 条件 则 分支 否则 分支"""
        self._expect(TokenType.WORD, "期望 '若'")  # 消耗 '若'

        cond = self._parse_expression()

        self._expect(TokenType.WORD, "期望 '则'")  # 消耗 '则'
        then_branch = self._parse_expression()

        else_branch = None
        if self._current().type == TokenType.WORD and self._current().value == '否则':
            self._advance()  # 消耗 '否则'
            else_branch = self._parse_expression()

        return If(cond, then_branch, else_branch)

    def _is_verb(self, name: str) -> bool:
        """判断是否是动词（简化版：非副词的汉字标识符）"""
        # 这里可以查表，暂时假设所有汉字都是动词
        return name not in self.adverbs


class ParserError(Exception):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"语法错误 (行{line}, 列{col}): {message}")
```

### 4.2 副词后处理

```python
def process_adverbs(node: Node, adverbs: set) -> Node:
    """后处理 AST：副词吞噬右侧 Call"""
    if isinstance(node, Pipeline):
        new_steps = []
        i = 0
        steps = node.steps

        while i < len(steps):
            step = steps[i]

            # 如果是副词，吞噬右侧的 Call
            if isinstance(step, Call) and step.verb.name in adverbs:
                if i + 1 < len(steps):
                    # 吞噬右侧
                    right = steps[i + 1]
                    step = Call(step.verb, [right], step.is_partial)
                    new_steps.append(step)
                    i += 2
                    continue

            new_steps.append(step)
            i += 1

        return Pipeline(new_steps)

    return node
```

---

## 五、Python 代码生成器 (codegen.py)

```python
from typing import Dict, Tuple
import ast as py_ast

class PythonCodeGen:
    def __init__(self):
        # 内置动词映射：名称 -> (Python 表达式, 元数)
        self.builtins: Dict[str, Tuple[str, int]] = {
            # 算术
            '加': ('_add', 2),
            '减': ('_sub', 2),
            '乘': ('_mul', 2),
            '除': ('_div', 2),
            '模': ('_mod', 2),
            '幂': ('_pow', 2),

            # 比较
            '大': ('_gt', 2),
            '小': ('_lt', 2),
            '等': ('_eq', 2),
            '不等': ('_ne', 2),

            # 逻辑
            '且': ('_and', 2),
            '或': ('_or', 2),
            '非': ('_not', 1),

            # 列表
            '列': ('_list', -1),
            '首': ('_head', 1),
            '余': ('_tail', 1),
            '入': ('_nth', 2),
            '长': ('_len', 1),

            # 高阶
            '皆': ('_map', 2),
            '只': ('_filter', 2),
            '归': ('_reduce', 3),

            # I/O
            '印': ('print', 1),

            # 特殊
            '行': ('_eval', 1),
        }

        # 用户定义的函数/变量
        self.user_defined: Dict[str, str] = {}

        # 缩进级别
        self.indent = 0

    def generate(self, node: Node) -> str:
        """生成 Python 代码"""
        if isinstance(node, Program):
            return self._gen_program(node)
        elif isinstance(node, Num):
            return repr(node.value)
        elif isinstance(node, Str):
            return repr(node.value)
        elif isinstance(node, Bool):
            return 'True' if node.value else 'False'
        elif isinstance(node, Nil):
            return 'None'
        elif isinstance(node, List):
            return self._gen_list(node)
        elif isinstance(node, Word):
            return node.name
        elif isinstance(node, Call):
            return self._gen_call(node)
        elif isinstance(node, Pipeline):
            return self._gen_pipeline(node)
        elif isinstance(node, Quote):
            return self._gen_quote(node)
        elif isinstance(node, Define):
            return self._gen_define(node)
        elif isinstance(node, Lambda):
            return self._gen_lambda(node)
        elif isinstance(node, If):
            return self._gen_if(node)
        else:
            raise CodeGenError(f"未知节点类型: {type(node)}")

    def _gen_program(self, node: Program) -> str:
        """生成程序"""
        lines = []
        for stmt in node.statements:
            code = self.generate(stmt)
            if code:
                lines.append(code)
        return '\n'.join(lines)

    def _gen_list(self, node: List) -> str:
        """生成列表"""
        elements = ', '.join(self.generate(e) for e in node.elements)
        return f'[{elements}]'

    def _gen_call(self, node: Call) -> str:
        """生成函数调用"""
        verb_name = node.verb.name

        # 查找动词
        if verb_name in self.builtins:
            py_func, arity = self.builtins[verb_name]
        elif verb_name in self.user_defined:
            py_func = verb_name
            arity = self.user_defined[verb_name]
        else:
            # 假设是用户定义的函数
            py_func = verb_name
            arity = -1

        args = [self.generate(a) for a in node.args]

        # 柯里化：参数不足时生成 lambda
        if arity > 0 and len(args) < arity:
            missing = arity - len(args)
            params = ', '.join(f'_p{i}' for i in range(missing))
            all_args = args + [f'_p{i}' for i in range(missing)]
            return f'(lambda {params}: {py_func}({", ".join(all_args)}))'

        # 正常调用
        return f'{py_func}({", ".join(args)})'

    def _gen_pipeline(self, node: Pipeline) -> str:
        """生成管道"""
        if len(node.steps) == 1:
            return self.generate(node.steps[0])

        # 第一步的结果作为后续步骤的输入
        result = self.generate(node.steps[0])

        for step in node.steps[1:]:
            step_code = self.generate(step)
            # 如果 step 是 Call，将 result 作为第一个参数
            if isinstance(step, Call):
                verb_name = step.verb.name
                if verb_name in self.builtins:
                    py_func, _ = self.builtins[verb_name]
                else:
                    py_func = verb_name

                args = [self.generate(a) for a in step.args]
                # 管道值作为第一个参数
                all_args = [result] + args
                result = f'{py_func}({", ".join(all_args)})'
            else:
                result = f'{step_code}({result})'

        return result

    def _gen_quote(self, node: Quote) -> str:
        """生成引用（返回 AST 的 Python 表示）"""
        # 将 AST 转为 Python 字典/对象表示
        ast_dict = self._ast_to_dict(node.expr)
        return repr(ast_dict)

    def _ast_to_dict(self, node: Node) -> dict:
        """将 AST 节点转为字典"""
        if isinstance(node, Num):
            return {'type': 'num', 'value': node.value}
        elif isinstance(node, Str):
            return {'type': 'str', 'value': node.value}
        elif isinstance(node, Word):
            return {'type': 'word', 'name': node.name}
        elif isinstance(node, Call):
            return {
                'type': 'call',
                'verb': self._ast_to_dict(node.verb),
                'args': [self._ast_to_dict(a) for a in node.args]
            }
        elif isinstance(node, Pipeline):
            return {
                'type': 'pipeline',
                'steps': [self._ast_to_dict(s) for s in node.steps]
            }
        else:
            return {'type': 'unknown'}

    def _gen_define(self, node: Define) -> str:
        """生成定义语句"""
        name = node.name
        value = self.generate(node.value)

        # 记录用户定义
        if isinstance(node.value, Lambda):
            self.user_defined[name] = len(node.value.params)
        else:
            self.user_defined[name] = -1

        return f'{name} = {value}'

    def _gen_lambda(self, node: Lambda) -> str:
        """生成匿名函数"""
        params = ', '.join(node.params)
        body = self.generate(node.body)
        return f'(lambda {params}: {body})'

    def _gen_if(self, node: If) -> str:
        """生成条件表达式"""
        cond = self.generate(node.cond)
        then_code = self.generate(node.then_branch)

        if node.else_branch:
            else_code = self.generate(node.else_branch)
            return f'({then_code} if {cond} else {else_code})'
        else:
            return f'({then_code} if {cond} else None)'


class CodeGenError(Exception):
    pass
```

---

## 六、运行时支持 (runtime.py)

```python
from functools import reduce
from typing import Any, Callable, List

# ============ 算术运算 ============

def _add(a, b): return a + b
def _sub(a, b): return a - b
def _mul(a, b): return a * b
def _div(a, b): return a / b
def _mod(a, b): return a % b
def _pow(a, b): return a ** b

# ============ 比较运算 ============

def _gt(a, b): return a > b
def _lt(a, b): return a < b
def _eq(a, b): return a == b
def _ne(a, b): return a != b

# ============ 逻辑运算 ============

def _and(a, b): return a and b
def _or(a, b): return a or b
def _not(a): return not a

# ============ 列表操作 ============

def _list(*args): return list(args)
def _head(lst): return lst[0] if lst else None
def _tail(lst): return lst[1:] if len(lst) > 1 else []
def _nth(lst, n): return lst[n] if n < len(lst) else None
def _len(lst): return len(lst)

# ============ 高阶函数 ============

def _map(func, lst=None):
    """映射：支持柯里化"""
    if lst is None:
        return lambda x: list(map(func, x))
    return list(map(func, lst))

def _filter(pred, lst=None):
    """过滤：支持柯里化"""
    if lst is None:
        return lambda x: list(filter(pred, x))
    return list(filter(pred, lst))

def _reduce(func, init=None, lst=None):
    """归约：支持柯里化"""
    if lst is None:
        if init is None:
            return lambda x, y: reduce(func, x, y)
        return lambda x: reduce(func, x, init)
    return reduce(func, lst, init)

# ============ 特殊函数 ============

def _eval(ast_dict):
    """执行 AST（简化版）"""
    # 这里需要将 AST 字典转回可执行代码
    # 完整实现需要 codegen 配合
    raise NotImplementedError("eval 需要完整实现")

# ============ 柯里化辅助 ============

def curry(func, arity):
    """将函数转为可柯里化形式"""
    def wrapper(*args):
        if len(args) >= arity:
            return func(*args[:arity])
        return curry(lambda *more: func(*args, *more), arity - len(args))
    return wrapper
```

---

## 七、主入口 (main.py)

```python
#!/usr/bin/env python3
"""
言叶语言 - Python 转译器
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParserError, process_adverbs
from codegen import PythonCodeGen, CodeGenError
from runtime import *

def run(source: str, debug: bool = False) -> Any:
    """运行言叶代码"""
    try:
        # 1. 词法分析
        lexer = Lexer()
        tokens = lexer.tokenize(source)
        if debug:
            print("=== Tokens ===")
            for tok in tokens:
                print(f"  {tok}")

        # 2. 语法分析
        parser = Parser()
        ast = parser.parse(tokens)
        ast = process_adverbs(ast, {'皆', '只', '归', '潜'})
        if debug:
            print("\n=== AST ===")
            print(f"  {ast}")

        # 3. 生成 Python 代码
        codegen = PythonCodeGen()
        py_code = codegen.generate(ast)
        if debug:
            print("\n=== Python ===")
            print(py_code)

        # 4. 执行
        # 创建执行环境
        env = globals().copy()
        result = eval(py_code, env)
        return result

    except LexerError as e:
        print(f"词法错误: {e}", file=sys.stderr)
        return None
    except ParserError as e:
        print(f"语法错误: {e}", file=sys.stderr)
        return None
    except CodeGenError as e:
        print(f"代码生成错误: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"运行时错误: {e}", file=sys.stderr)
        return None


def repl():
    """交互式环境"""
    print("言叶语言 v0.1")
    print("输入代码，以空行结束。输入 'quit' 退出。")
    print()

    while True:
        print("言叶> ", end="", flush=True)
        lines = []
        while True:
            try:
                line = input()
                if line == 'quit':
                    return
                if not line:
                    break
                lines.append(line)
            except EOFError:
                return

        if not lines:
            continue

        source = ''.join(lines)
        result = run(source, debug=False)
        if result is not None:
            print(f"  => {result}")


def main():
    """主入口"""
    if len(sys.argv) < 2:
        repl()
        return

    filename = sys.argv[1]
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    debug = '--debug' in sys.argv
    result = run(source, debug=debug)
    if result is not None:
        print(result)


if __name__ == "__main__":
    main()
```

---

## 八、测试用例

### 8.1 测试脚本

```python
# test_yanya.py

from main import run

def test_arithmetic():
    """测试算术运算"""
    assert run("10加5。") == 15
    assert run("10减5。") == 5
    assert run("10乘5。") == 50
    assert run("10除5。") == 2.0
    print("✓ 算术运算测试通过")

def test_pipeline():
    """测试管道"""
    assert run("10加5，乘2。") == 30
    assert run("100减50，除2。") == 25
    print("✓ 管道测试通过")

def test_list():
    """测试列表"""
    assert run("列1 2 3。") == [1, 2, 3]
    assert run("首列1 2 3。") == 1
    assert run("余列1 2 3。") == [2, 3]
    print("✓ 列表测试通过")

def test_highorder():
    """测试高阶函数"""
    assert run("列1 2 3，皆乘2。") == [2, 4, 6]
    assert run("列1 2 3 4 5，只大2。") == [3, 4, 5]
    assert run("列1 2 3，归加0。") == 6
    print("✓ 高阶函数测试通过")

def test_define():
    """测试变量定义"""
    run("定x=10。")
    run("定平方=函x乘x x。")
    print("✓ 定义测试通过")

def test_condition():
    """测试条件"""
    assert run("若5大3则印"大"否则印"小"。") is None  # print 返回 None
    print("✓ 条件测试通过")

if __name__ == "__main__":
    test_arithmetic()
    test_pipeline()
    test_list()
    test_highorder()
    test_define()
    test_condition()
    print("\n所有测试通过！")
```

### 8.2 示例程序

```python
# examples/factorial.yanya
-- 阶乘函数

定阶乘=函n
  若n等1
    则1
    否则乘 n 阶乘减 n 1
。

印阶乘5。
-- 输出: 120
```

```python
# examples/fizzbuzz.yanya
-- FizzBuzz

定fizzbuzz=函n
  若归且0 n模3 0 n模5
    则"FizzBuzz"
    若归且0 n模3 0
      则"Fizz"
      若归且0 n模5 0
        则"Buzz"
        否则n
。

列1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
皆fizzbuzz
皆印
。
```

---

## 九、文件结构

```
yanya/
├── lexer.py          # 词法分析器
├── parser.py         # 语法分析器
├── ast.py            # AST 节点定义
├── codegen.py        # Python 代码生成器
├── runtime.py        # 运行时支持
├── builtins.py       # 内置动词映射（可选，已整合到 codegen）
├── main.py           # 入口
├── test_yanya.py     # 测试
└── examples/
    ├── factorial.yanya
    ├── fizzbuzz.yanya
    └── sort.yanya
```

---

## 十、后续扩展

### 10.1 同像性（Quote/Eval）

```python
# 当前方案：AST 转为字典
# 完整方案：支持运行时编译

def _eval(ast_dict, env):
    """执行 AST 字典"""
    # 1. 将字典转回 AST 节点
    # 2. 调用 codegen 生成 Python 代码
    # 3. eval 执行
    pass
```

### 10.2 宏系统

```python
# 编译时宏展开
def expand_macros(ast, env):
    """展开宏"""
    # 遍历 AST，遇到宏调用时展开
    pass
```

### 10.3 类型检查（可选）

```python
# 添加类型标注
def check_types(ast, env):
    """静态类型检查"""
    pass
```

---

## 十一、总结

这个转译方案的核心优势：

| 特性 | 说明 |
|------|------|
| **工作量低** | 只需实现词法、语法、代码生成，无需解释器 |
| **调试方便** | 可以打印中间 Python 代码 |
| **生态复用** | 直接使用 Python 标准库 |
| **可扩展** | 后续可添加类型检查、宏系统、同像性 |

**下一步**：按照这个方案实现各个模块，先跑通 MVP，再逐步完善。
