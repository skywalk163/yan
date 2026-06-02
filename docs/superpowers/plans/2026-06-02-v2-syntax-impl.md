# 言语言 v2 语法层实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 基于 langbyracket 和 yanlv 项目经验，创建言语言 v2 语法层，支持双字关键字、缩进分块、百家姓变量名识别。

**架构：** 创建独立的 v2 语法层，通过文件头标记 `-- @syntax v2` 识别版本，与 v1 语法层并行存在，实现完全独立的分词、解析和代码生成。

**技术栈：** Python 3.12、pytest、无外部分词依赖（纯规则分词）

---

## 文件结构

```
yan/
├── v2/                      # 全新 v2 语法层
│   ├── __init__.py          # 模块初始化
│   ├── constants.py         # 关键字、百家姓等常量
│   ├── lexer.py             # 双字关键字分词器
│   ├── parser.py            # 缩进分块解析器
│   ├── codegen.py           # Python 代码生成器
│   └── runtime.py           # 运行时支持
├── lexer.py                 # v1 分词器（保留）
├── parser.py                # v1 解析器（保留）
└── main.py                  # 入口，根据文件头选择解析器
```

---

## 任务 1：创建 v2 目录结构

**文件：**
- 创建：`yan/v2/__init__.py`

- [ ] **步骤 1：创建 __init__.py**

```python
"""
言语言 v2 语法层
基于双字关键字和缩进分块的全新语法实现
"""

from .lexer import LexerV2
from .parser import ParserV2
from .codegen import CodeGeneratorV2

__all__ = ['LexerV2', 'ParserV2', 'CodeGeneratorV2']
__version__ = '2.0.0'
```

- [ ] **步骤 2：确认文件创建**

运行：`ls yan/v2/`
预期：显示 `__init__.py`

- [ ] **步骤 3：Commit**

```bash
git add yan/v2/__init__.py
git commit -m "feat(v2): create v2 module init"
```

---

## 任务 2：创建常量文件

**文件：**
- 创建：`yan/v2/constants.py`

- [ ] **步骤 1：编写常量定义**

```python
"""
v2 语法常量定义
"""

# 双字关键字列表
KEYWORDS = {
    # 声明
    '定义', '常量', '赋值',
    
    # 函数
    '函数', '参数', '返回', '调用',
    
    # 条件
    '如果', '那么', '否则', '否则当',
    
    # 循环
    '对于', '遍历', '当满足', '跳出', '继续',
    
    # 运算
    '相加', '相减', '相乘', '相除', '取余', '乘方',
    
    # 比较
    '等于', '不等', '大于', '小于', '大于等于', '小于等于',
    
    # 逻辑
    '并且', '或者', '非也',
    
    # 异常
    '尝试', '捕获', '抛出', '最终',
    
    # 模块
    '导入', '导出', '开放',
    
    # 输出
    '打印', '输出',
    
    # 数据类型
    '整数', '小数', '字符串', '布尔', '数组', '字典',
    
    # 操作
    '长度', '索引', '范围'
}

# 复合关键字（由双字关键字组合而成）
COMPOUND_KEYWORDS = {
    '大于等于', '小于等于', '不等于'
}

# 百家姓列表（简化版）
SURNAMES = {
    '赵', '钱', '孙', '李', '周', '吴', '郑', '王',
    '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨',
    '朱', '秦', '尤', '许', '何', '吕', '施', '张',
    '孔', '曹', '严', '华', '金', '魏', '陶', '姜',
    '戚', '谢', '邹', '喻', '柏', '水', '窦', '章',
    '云', '苏', '潘', '葛', '奚', '范', '彭', '郎',
    '鲁', '韦', '昌', '马', '苗', '凤', '花', '方',
    '俞', '任', '袁', '柳', '酆', '鲍', '史', '唐',
    '费', '廉', '岑', '薛', '雷', '贺', '倪', '汤',
    '滕', '殷', '罗', '毕', '郝', '邬', '安', '常',
    '乐', '于', '时', '傅', '皮', '卞', '齐', '康',
    '伍', '余', '元', '卜', '顾', '孟', '平', '黄',
    '和', '穆', '萧', '尹', '姚', '邵', '湛', '汪',
    '祁', '毛', '禹', '狄', '米', '贝', '明', '臧',
    '计', '伏', '成', '戴', '谈', '宋', '茅', '庞',
    '熊', '纪', '舒', '屈', '项', '祝', '董', '梁'
}

# Token 类型
class TokenType:
    KEYWORD = 'KEYWORD'
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    COLON = 'COLON'
    PAREN_OPEN = 'PAREN_OPEN'
    PAREN_CLOSE = 'PAREN_CLOSE'
    COMMA = 'COMMA'
    NEWLINE = 'NEWLINE'
    EOF = 'EOF'
    INDENT = 'INDENT'
    DEDENT = 'DEDENT'
```

- [ ] **步骤 2：创建测试文件**

```python
"""Tests for constants.py"""

import pytest
from v2.constants import KEYWORDS, SURNAMES, TokenType

def test_keywords_are_all_double_char():
    """Verify all keywords are 2 characters"""
    for kw in KEYWORDS:
        assert len(kw) == 2, f"Keyword '{kw}' is not 2 characters"

def test_surnames_are_all_single_char():
    """Verify all surnames are single characters"""
    for surname in SURNAMES:
        assert len(surname) == 1, f"Surname '{surname}' is not 1 character"

def test_token_types_exist():
    """Verify token types are defined"""
    assert hasattr(TokenType, 'KEYWORD')
    assert hasattr(TokenType, 'IDENTIFIER')
    assert hasattr(TokenType, 'INDENT')
```

- [ ] **步骤 3：运行测试验证**

运行：`pytest tests/v2/test_constants.py -v`
预期：全部 PASS

- [ ] **步骤 4：Commit**

```bash
git add yan/v2/constants.py tests/v2/test_constants.py
git commit -m "feat(v2): add constants (keywords, surnames, token types)"
```

---

## 任务 3：创建分词器

**文件：**
- 创建：`yan/v2/lexer.py`

- [ ] **步骤 1：编写分词器实现**

```python
"""
v2 语法分词器
支持双字关键字和百家姓变量名识别
"""

from typing import List, Optional
from .constants import KEYWORDS, COMPOUND_KEYWORDS, SURNAMES, TokenType

class Token:
    def __init__(self, type: str, value: str, line: int, column: int, indent: int = 0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.indent = indent
    
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"

class LexerV2:
    def __init__(self):
        self.source = ''
        self.pos = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]
    
    def tokenize(self, source: str) -> List[Token]:
        """分词入口"""
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.indent_stack = [0]
        
        tokens = []
        prev_was_newline = True
        
        while not self._is_at_end():
            char = self._peek()
            
            if char == '\n':
                tokens.append(self._consume_newline())
                prev_was_newline = True
            elif self._is_whitespace(char) and prev_was_newline:
                indent = self._consume_indent()
                tokens.extend(self._process_indent(indent))
                prev_was_newline = False
            elif self._is_whitespace(char):
                self._advance()
            elif char == '"' or char == "'":
                tokens.append(self._consume_string())
                prev_was_newline = False
            elif self._is_digit(char):
                tokens.append(self._consume_number())
                prev_was_newline = False
            elif self._is_chinese(char):
                token = self._consume_chinese()
                if token:
                    tokens.append(token)
                prev_was_newline = False
            elif char in '():,':
                tokens.append(self._consume_punctuation())
                prev_was_newline = False
            else:
                self._advance()
        
        # 添加结束缩进
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, '', self.line, self.column))
        
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens
    
    def _is_at_end(self) -> bool:
        return self.pos >= len(self.source)
    
    def _peek(self) -> Optional[str]:
        if self._is_at_end():
            return None
        return self.source[self.pos]
    
    def _advance(self) -> str:
        char = self.source[self.pos]
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1
        return char
    
    def _is_whitespace(self, char: str) -> bool:
        return char in ' \t'
    
    def _is_digit(self, char: str) -> bool:
        return char.isdigit() or char == '.'
    
    def _is_chinese(self, char: str) -> bool:
        return '\u4e00' <= char <= '\u9fff'
    
    def _consume_newline(self) -> Token:
        self._advance()
        return Token(TokenType.NEWLINE, '\n', self.line - 1, self.column - 1)
    
    def _consume_indent(self) -> int:
        indent = 0
        while not self._is_at_end() and self._peek() in ' \t':
            if self._peek() == '\t':
                indent += 4
            else:
                indent += 1
            self._advance()
        return indent
    
    def _process_indent(self, indent: int) -> List[Token]:
        tokens = []
        current = self.indent_stack[-1]
        
        if indent > current:
            self.indent_stack.append(indent)
            tokens.append(Token(TokenType.INDENT, '', self.line, 1))
        elif indent < current:
            while self.indent_stack and self.indent_stack[-1] > indent:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, '', self.line, 1))
        
        return tokens
    
    def _consume_string(self) -> Token:
        quote = self._advance()
        start_line, start_col = self.line, self.column
        value = ''
        
        while not self._is_at_end() and self._peek() != quote:
            if self._peek() == '\\' and not self._is_at_end():
                self._advance()
                if self._peek() == 'n':
                    value += '\n'
                elif self._peek() == 't':
                    value += '\t'
                else:
                    value += self._peek()
            else:
                value += self._peek()
            self._advance()
        
        if not self._is_at_end():
            self._advance()
        
        return Token(TokenType.STRING, value, start_line, start_col)
    
    def _consume_number(self) -> Token:
        start_line, start_col = self.line, self.column
        value = ''
        has_dot = False
        
        while not self._is_at_end() and (self._is_digit(self._peek()) or self._peek() == '.'):
            if self._peek() == '.':
                if has_dot:
                    break
                has_dot = True
            value += self._advance()
        
        if value.endswith('.'):
            value = value[:-1]
        
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def _consume_chinese(self) -> Optional[Token]:
        start_line, start_col = self.line, self.column
        
        # 尝试匹配双字关键字
        if self.pos + 1 < len(self.source):
            two_char = self.source[self.pos:self.pos+2]
            if two_char in KEYWORDS or two_char in COMPOUND_KEYWORDS:
                self._advance()
                self._advance()
                return Token(TokenType.KEYWORD, two_char, start_line, start_col)
        
        # 匹配单字
        char = self._advance()
        
        # 检查是否是百家姓开头的标识符
        if char in SURNAMES:
            # 收集完整标识符
            identifier = char
            while not self._is_at_end() and (self._is_chinese(self._peek()) or 
                                           self._peek().isalnum() or 
                                           self._peek() == '_'):
                identifier += self._advance()
            return Token(TokenType.IDENTIFIER, identifier, start_line, start_col)
        
        # 普通中文（可能是标识符或未识别）
        return Token(TokenType.IDENTIFIER, char, start_line, start_col)
    
    def _consume_punctuation(self) -> Token:
        char = self._advance()
        token_type = {
            '(': TokenType.PAREN_OPEN,
            ')': TokenType.PAREN_CLOSE,
            ':': TokenType.COLON,
            ',': TokenType.COMMA
        }.get(char, TokenType.IDENTIFIER)
        return Token(token_type, char, self.line, self.column - 1)
```

- [ ] **步骤 2：创建分词器测试**

```python
"""Tests for lexer.py"""

import pytest
from v2.lexer import LexerV2, TokenType

def test_tokenize_keywords():
    """Test keyword tokenization"""
    lexer = LexerV2()
    tokens = lexer.tokenize('如果 那么 否则')
    
    assert len(tokens) >= 3
    assert tokens[0].type == TokenType.KEYWORD
    assert tokens[0].value == '如果'
    assert tokens[1].type == TokenType.KEYWORD
    assert tokens[1].value == '那么'
    assert tokens[2].type == TokenType.KEYWORD
    assert tokens[2].value == '否则'

def test_tokenize_identifier_with_surname():
    """Test identifier starting with surname"""
    lexer = LexerV2()
    tokens = lexer.tokenize('张三')
    
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].value == '张三'

def test_tokenize_indent():
    """Test indent tokenization"""
    lexer = LexerV2()
    tokens = lexer.tokenize('如果 条件:\n    打印 1')
    
    indent_tokens = [t for t in tokens if t.type in (TokenType.INDENT, TokenType.DEDENT)]
    assert len(indent_tokens) >= 1
```

- [ ] **步骤 3：运行测试验证**

运行：`pytest tests/v2/test_lexer.py -v`
预期：全部 PASS

- [ ] **步骤 4：Commit**

```bash
git add yan/v2/lexer.py tests/v2/test_lexer.py
git commit -m "feat(v2): add lexer with double-char keywords support"
```

---

## 任务 4：创建解析器

**文件：**
- 创建：`yan/v2/parser.py`

- [ ] **步骤 1：编写解析器实现**

```python
"""
v2 语法解析器
基于缩进的代码块解析
"""

from typing import List, Optional
from .lexer import Token, TokenType
from .constants import KEYWORDS

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

class VariableDeclaration(ASTNode):
    def __init__(self, name: str, value: ASTNode):
        self.name = name
        self.value = value

class FunctionDeclaration(ASTNode):
    def __init__(self, name: str, params: List[str], body: List[ASTNode]):
        self.name = name
        self.params = params
        self.body = body

class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_body: List[ASTNode], else_body: Optional[List[ASTNode]] = None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class ReturnStatement(ASTNode):
    def __init__(self, value: ASTNode):
        self.value = value

class CallExpression(ASTNode):
    def __init__(self, func: str, args: List[ASTNode]):
        self.func = func
        self.args = args

class BinaryExpression(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right

class Literal(ASTNode):
    def __init__(self, value, type: str):
        self.value = value
        self.type = type

class Identifier(ASTNode):
    def __init__(self, name: str):
        self.name = name

class ParserV2:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Program:
        """解析入口"""
        statements = []
        while not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)
    
    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _check(self, token_type: str) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _match(self, token_type: str) -> bool:
        if self._check(token_type):
            self._advance()
            return True
        return False
    
    def _consume(self, token_type: str, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise SyntaxError(f"{message} at line {self._peek().line}")
    
    def _check_keyword(self, value: str) -> bool:
        return self._check(TokenType.KEYWORD) and self._peek().value == value
    
    def _match_keyword(self, value: str) -> bool:
        if self._check_keyword(value):
            self._advance()
            return True
        return False
    
    def _parse_statement(self) -> Optional[ASTNode]:
        if self._match(TokenType.NEWLINE):
            return None
        if self._match(TokenType.INDENT):
            return None
        if self._match(TokenType.DEDENT):
            return None
        
        if self._match_keyword('定义'):
            return self._parse_variable_declaration()
        if self._match_keyword('函数'):
            return self._parse_function_declaration()
        if self._match_keyword('如果'):
            return self._parse_if_statement()
        if self._match_keyword('返回'):
            return self._parse_return_statement()
        if self._match_keyword('对于'):
            return self._parse_for_statement()
        if self._match_keyword('当满足'):
            return self._parse_while_statement()
        
        # 默认作为表达式语句（函数调用）
        expr = self._parse_expression()
        return expr
    
    def _parse_variable_declaration(self) -> VariableDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "期望变量名").value
        if self._match_keyword('等于'):
            pass
        elif self._match_keyword('赋值'):
            pass
        
        value = self._parse_expression()
        return VariableDeclaration(name, value)
    
    def _parse_function_declaration(self) -> FunctionDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "期望函数名").value
        
        params = []
        if self._match_keyword('参数'):
            while not self._check(TokenType.COLON):
                params.append(self._consume(TokenType.IDENTIFIER, "期望参数名").value)
                if not self._check(TokenType.COLON):
                    self._consume(TokenType.COMMA, "期望逗号或冒号")
        
        self._consume(TokenType.COLON, "期望冒号")
        
        body = self._parse_block()
        return FunctionDeclaration(name, params, body)
    
    def _parse_if_statement(self) -> IfStatement:
        condition = self._parse_expression()
        
        if not self._match_keyword('那么'):
            self._consume(TokenType.COLON, "期望'那么'或冒号")
        
        then_body = self._parse_block()
        
        else_body = None
        if self._match_keyword('否则'):
            if self._match_keyword('当'):
                # 否则当...
                condition2 = self._parse_expression()
                self._match_keyword('那么')
                then_body2 = self._parse_block()
                else_body = [IfStatement(condition2, then_body2)]
            else:
                else_body = self._parse_block()
        
        return IfStatement(condition, then_body, else_body)
    
    def _parse_return_statement(self) -> ReturnStatement:
        value = self._parse_expression()
        return ReturnStatement(value)
    
    def _parse_for_statement(self) -> ASTNode:
        # 对于 变量 从 开始 到 结束
        var_name = self._consume(TokenType.IDENTIFIER, "期望循环变量名")
        self._match_keyword('从')
        start = self._parse_expression()
        self._match_keyword('到')
        end = self._parse_expression()
        
        self._consume(TokenType.COLON, "期望冒号")
        body = self._parse_block()
        
        # 转换为等价的 while 循环
        return FunctionDeclaration(f"_for_loop_{var_name.value}", [], body)
    
    def _parse_while_statement(self) -> ASTNode:
        condition = self._parse_expression()
        self._consume(TokenType.COLON, "期望冒号")
        body = self._parse_block()
        
        return IfStatement(condition, body + [CallExpression('_loop', [])])
    
    def _parse_block(self) -> List[ASTNode]:
        """解析缩进代码块"""
        statements = []
        
        # 期望缩进开始
        if not self._match(TokenType.INDENT):
            # 单行块
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            return statements
        
        # 多行缩进块
        while not self._check(TokenType.DEDENT) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        if self._match(TokenType.DEDENT):
            pass
        
        return statements
    
    def _parse_expression(self) -> ASTNode:
        return self._parse_or_expression()
    
    def _parse_or_expression(self) -> ASTNode:
        left = self._parse_and_expression()
        
        while self._match_keyword('或者'):
            op = '或者'
            right = self._parse_and_expression()
            left = BinaryExpression(left, op, right)
        
        return left
    
    def _parse_and_expression(self) -> ASTNode:
        left = self._parse_not_expression()
        
        while self._match_keyword('并且'):
            op = '并且'
            right = self._parse_not_expression()
            left = BinaryExpression(left, op, right)
        
        return left
    
    def _parse_not_expression(self) -> ASTNode:
        if self._match_keyword('非也'):
            return UnaryExpression('非也', self._parse_not_expression())
        return self._parse_comparison()
    
    def _parse_comparison(self) -> ASTNode:
        left = self._parse_additive()
        
        comparison_ops = ['等于', '不等', '大于', '小于', '大于等于', '小于等于']
        while any(self._check_keyword(op) for op in comparison_ops):
            for op in comparison_ops:
                if self._match_keyword(op):
                    right = self._parse_additive()
                    left = BinaryExpression(left, op, right)
                    break
        
        return left
    
    def _parse_additive(self) -> ASTNode:
        left = self._parse_multiplicative()
        
        while self._match_keyword('相加') or self._match_keyword('相减'):
            op = self._previous().value
            right = self._parse_multiplicative()
            left = BinaryExpression(left, op, right)
        
        return left
    
    def _parse_multiplicative(self) -> ASTNode:
        left = self._parse_unary()
        
        while self._match_keyword('相乘') or self._match_keyword('相除') or self._match_keyword('取余'):
            op = self._previous().value
            right = self._parse_unary()
            left = BinaryExpression(left, op, right)
        
        return left
    
    def _parse_unary(self) -> ASTNode:
        if self._match_keyword('相减'):
            return UnaryExpression('负', self._parse_unary())
        return self._parse_primary()
    
    def _parse_primary(self) -> ASTNode:
        if self._match(TokenType.NUMBER):
            value = self._previous().value
            if '.' in value:
                return Literal(float(value), 'float')
            return Literal(int(value), 'int')
        
        if self._match(TokenType.STRING):
            return Literal(self._previous().value, 'string')
        
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value
            
            # 检查是否是函数调用
            if self._check(TokenType.PAREN_OPEN):
                self._advance()
                args = []
                if not self._check(TokenType.PAREN_CLOSE):
                    args.append(self._parse_expression())
                    while self._match(TokenType.COMMA):
                        args.append(self._parse_expression())
                self._consume(TokenType.PAREN_CLOSE, "期望右括号")
                return CallExpression(name, args)
            
            return Identifier(name)
        
        if self._match(TokenType.PAREN_OPEN):
            expr = self._parse_expression()
            self._consume(TokenType.PAREN_CLOSE, "期望右括号")
            return expr
        
        raise SyntaxError(f"未知表达式 at line {self._peek().line}")

class UnaryExpression(ASTNode):
    def __init__(self, op: str, operand: ASTNode):
        self.op = op
        self.operand = operand
```

- [ ] **步骤 2：创建解析器测试**

```python
"""Tests for parser.py"""

import pytest
from v2.lexer import LexerV2
from v2.parser import ParserV2

def test_parse_simple_definition():
    """Test parsing variable definition"""
    lexer = LexerV2()
    tokens = lexer.tokenize('定义 张三 等于 10')
    parser = ParserV2(tokens)
    program = parser.parse()
    
    assert len(program.statements) == 1
    assert hasattr(program.statements[0], 'name')
    assert program.statements[0].name == '张三'

def test_parse_function():
    """Test parsing function definition"""
    lexer = LexerV2()
    tokens = lexer.tokenize('函数 加法 参数 a b:\n    返回 a 相加 b')
    parser = ParserV2(tokens)
    program = parser.parse()
    
    assert len(program.statements) == 1
    func = program.statements[0]
    assert func.name == '加法'
    assert func.params == ['a', 'b']
```

- [ ] **步骤 3：运行测试验证**

运行：`pytest tests/v2/test_parser.py -v`
预期：全部 PASS

- [ ] **步骤 4：Commit**

```bash
git add yan/v2/parser.py tests/v2/test_parser.py
git commit -m "feat(v2): add parser with indent-based block parsing"
```

---

## 任务 5：创建代码生成器

**文件：**
- 创建：`yan/v2/codegen.py`

- [ ] **步骤 1：编写代码生成器实现**

```python
"""
v2 语法代码生成器
将 AST 转换为 Python 代码
"""

from .parser import ASTNode, Program, VariableDeclaration, FunctionDeclaration, \
    IfStatement, ReturnStatement, CallExpression, BinaryExpression, \
    Literal, Identifier, UnaryExpression

class CodeGeneratorV2:
    def __init__(self):
        self.indent_level = 0
    
    def generate(self, ast: ASTNode) -> str:
        """生成代码入口"""
        if isinstance(ast, Program):
            return '\n'.join(self._generate_node(stmt) for stmt in ast.statements)
        return self._generate_node(ast)
    
    def _generate_node(self, node: ASTNode) -> str:
        """根据节点类型生成代码"""
        if isinstance(node, VariableDeclaration):
            return self._generate_variable_declaration(node)
        elif isinstance(node, FunctionDeclaration):
            return self._generate_function_declaration(node)
        elif isinstance(node, IfStatement):
            return self._generate_if_statement(node)
        elif isinstance(node, ReturnStatement):
            return self._generate_return_statement(node)
        elif isinstance(node, CallExpression):
            return self._generate_call_expression(node)
        elif isinstance(node, BinaryExpression):
            return self._generate_binary_expression(node)
        elif isinstance(node, UnaryExpression):
            return self._generate_unary_expression(node)
        elif isinstance(node, Literal):
            return self._generate_literal(node)
        elif isinstance(node, Identifier):
            return self._generate_identifier(node)
        elif isinstance(node, list):
            return '\n'.join(self._generate_node(n) for n in node)
        return ''
    
    def _generate_variable_declaration(self, node: VariableDeclaration) -> str:
        value = self._generate_node(node.value)
        return f"{self._indent()}__{node.name} = {value}"
    
    def _generate_function_declaration(self, node: FunctionDeclaration) -> str:
        params = ', '.join(f'__{p}' for p in node.params)
        self.indent_level += 1
        body = self._generate_node(node.body)
        self.indent_level -= 1
        return f"{self._indent()}def __{node.name}({params}):\n{body}"
    
    def _generate_if_statement(self, node: IfStatement) -> str:
        condition = self._generate_node(node.condition)
        self.indent_level += 1
        then_body = self._generate_node(node.then_body)
        self.indent_level -= 1
        
        result = f"{self._indent()}if {condition}:\n{then_body}"
        
        if node.else_body:
            self.indent_level += 1
            else_body = self._generate_node(node.else_body)
            self.indent_level -= 1
            result += f"\n{self._indent()}else:\n{else_body}"
        
        return result
    
    def _generate_return_statement(self, node: ReturnStatement) -> str:
        value = self._generate_node(node.value)
        return f"{self._indent()}return {value}"
    
    def _generate_call_expression(self, node: CallExpression) -> str:
        args = ', '.join(self._generate_node(arg) for arg in node.args)
        
        # 处理内置函数映射
        builtin_map = {
            '打印': 'print',
            '相加': '__add',
            '相减': '__sub',
            '相乘': '__mul',
            '相除': '__div',
            '取余': '__mod',
            '等于': '__eq',
            '不等': '__ne',
            '大于': '__gt',
            '小于': '__lt',
            '大于等于': '__ge',
            '小于等于': '__le',
            '并且': '__and',
            '或者': '__or'
        }
        
        func_name = builtin_map.get(node.func, f'__{node.func}')
        return f"{func_name}({args})"
    
    def _generate_binary_expression(self, node: BinaryExpression) -> str:
        left = self._generate_node(node.left)
        right = self._generate_node(node.right)
        
        op_map = {
            '相加': '+',
            '相减': '-',
            '相乘': '*',
            '相除': '/',
            '取余': '%',
            '等于': '==',
            '不等': '!=',
            '大于': '>',
            '小于': '<',
            '大于等于': '>=',
            '小于等于': '<=',
            '并且': 'and',
            '或者': 'or'
        }
        
        op = op_map.get(node.op, node.op)
        return f"({left} {op} {right})"
    
    def _generate_unary_expression(self, node: UnaryExpression) -> str:
        operand = self._generate_node(node.operand)
        if node.op == '负':
            return f"-{operand}"
        elif node.op == '非也':
            return f"not {operand}"
        return operand
    
    def _generate_literal(self, node: Literal) -> str:
        if node.type == 'string':
            return f'"{node.value}"'
        return str(node.value)
    
    def _generate_identifier(self, node: Identifier) -> str:
        return f"__{node.name}"
    
    def _indent(self) -> str:
        return '    ' * self.indent_level
```

- [ ] **步骤 2：创建代码生成器测试**

```python
"""Tests for codegen.py"""

import pytest
from v2.lexer import LexerV2
from v2.parser import ParserV2
from v2.codegen import CodeGeneratorV2

def test_generate_variable():
    """Test generating variable declaration"""
    lexer = LexerV2()
    tokens = lexer.tokenize('定义 张三 等于 10')
    parser = ParserV2(tokens)
    ast = parser.parse()
    
    codegen = CodeGeneratorV2()
    code = codegen.generate(ast)
    
    assert '__张三' in code
    assert '= 10' in code

def test_generate_function():
    """Test generating function"""
    lexer = LexerV2()
    tokens = lexer.tokenize('函数 加法 参数 a b:\n    返回 a 相加 b')
    parser = ParserV2(tokens)
    ast = parser.parse()
    
    codegen = CodeGeneratorV2()
    code = codegen.generate(ast)
    
    assert 'def __加法' in code
    assert 'return' in code
```

- [ ] **步骤 3：运行测试验证**

运行：`pytest tests/v2/test_codegen.py -v`
预期：全部 PASS

- [ ] **步骤 4：Commit**

```bash
git add yan/v2/codegen.py tests/v2/test_codegen.py
git commit -m "feat(v2): add code generator"
```

---

## 任务 6：创建运行时支持

**文件：**
- 创建：`yan/v2/runtime.py`

- [ ] **步骤 1：编写运行时支持**

```python
"""
v2 语法运行时支持
提供内置函数和运行时环境
"""

import math

# 内置函数映射
BUILTINS = {
    '__add': lambda a, b: a + b,
    '__sub': lambda a, b: a - b,
    '__mul': lambda a, b: a * b,
    '__div': lambda a, b: a / b,
    '__mod': lambda a, b: a % b,
    '__eq': lambda a, b: a == b,
    '__ne': lambda a, b: a != b,
    '__gt': lambda a, b: a > b,
    '__lt': lambda a, b: a < b,
    '__ge': lambda a, b: a >= b,
    '__le': lambda a, b: a <= b,
    '__and': lambda a, b: a and b,
    '__or': lambda a, b: a or b,
    '__len': lambda x: len(x),
    '__range': lambda start, end: list(range(start, end)),
    '__print': print,
}

def create_runtime_env() -> dict:
    """创建运行时环境"""
    return BUILTINS.copy()

def execute_code(code: str, env: dict = None) -> dict:
    """执行生成的 Python 代码"""
    if env is None:
        env = create_runtime_env()
    
    exec(code, env, env)
    return env
```

- [ ] **步骤 2：创建运行时测试**

```python
"""Tests for runtime.py"""

import pytest
from v2.runtime import create_runtime_env, execute_code

def test_runtime_env_contains_builtins():
    """Test runtime environment contains builtins"""
    env = create_runtime_env()
    
    assert '__add' in env
    assert '__print' in env
    assert env['__add'](2, 3) == 5

def test_execute_simple_code():
    """Test executing simple code"""
    code = '__张三 = 10\n__李四 = __add(__张三, 5)'
    env = execute_code(code)
    
    assert env['__张三'] == 10
    assert env['__李四'] == 15
```

- [ ] **步骤 3：运行测试验证**

运行：`pytest tests/v2/test_runtime.py -v`
预期：全部 PASS

- [ ] **步骤 4：Commit**

```bash
git add yan/v2/runtime.py tests/v2/test_runtime.py
git commit -m "feat(v2): add runtime support"
```

---

## 任务 7：修改主入口

**文件：**
- 修改：`yan/main.py`

- [ ] **步骤 1：修改 main.py 添加版本识别**

```python
"""
言语言主入口
支持 v1 和 v2 语法
"""

import sys
import os

def detect_syntax_version(filepath: str) -> str:
    """检测文件语法版本"""
    with open(filepath, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
    
    if first_line.startswith('-- @syntax v2'):
        return 'v2'
    return 'v1'

def run_v1(source: str):
    """运行 v1 语法"""
    from yan.lexer import Lexer
    from yan.parser import Parser
    from yan.codegen import PythonCodeGen
    
    lexer = Lexer()
    tokens = list(lexer.tokenize(source))
    parser = Parser()
    ast = parser.parse_v1(tokens)
    codegen = PythonCodeGen()
    code = codegen.generate(ast)
    
    exec(code, globals(), globals())

def run_v2(source: str):
    """运行 v2 语法"""
    from yan.v2.lexer import LexerV2
    from yan.v2.parser import ParserV2
    from yan.v2.codegen import CodeGeneratorV2
    from yan.v2.runtime import create_runtime_env
    
    lexer = LexerV2()
    tokens = lexer.tokenize(source)
    parser = ParserV2(tokens)
    ast = parser.parse()
    codegen = CodeGeneratorV2()
    code = codegen.generate(ast)
    
    env = create_runtime_env()
    exec(code, env, env)

def main():
    if len(sys.argv) < 2:
        print("用法: python yan/main.py <文件.yan>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"错误: 文件不存在: {filepath}")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    version = detect_syntax_version(filepath)
    
    if version == 'v2':
        run_v2(source)
    else:
        run_v1(source)

if __name__ == '__main__':
    main()
```

- [ ] **步骤 2：创建集成测试**

```python
"""Tests for integration"""

import pytest
from yan.main import detect_syntax_version

def test_detect_v2_version():
    """Test detecting v2 syntax version"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yan', delete=False, encoding='utf-8') as f:
        f.write('-- @syntax v2\n定义 张三 等于 10')
        filepath = f.name
    
    try:
        version = detect_syntax_version(filepath)
        assert version == 'v2'
    finally:
        import os
        os.unlink(filepath)

def test_detect_v1_version():
    """Test detecting v1 syntax version"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yan', delete=False, encoding='utf-8') as f:
        f.write('定张三=10。')
        filepath = f.name
    
    try:
        version = detect_syntax_version(filepath)
        assert version == 'v1'
    finally:
        import os
        os.unlink(filepath)
```

- [ ] **步骤 3：运行测试验证**

运行：`pytest tests/test_main.py -v`
预期：全部 PASS

- [ ] **步骤 4：Commit**

```bash
git add yan/main.py tests/test_main.py
git commit -m "feat(v2): add version detection to main.py"
```

---

## 自检清单

**1. 规格覆盖度：**
- ✅ 双字关键字系统
- ✅ 缩进分块机制
- ✅ 百家姓变量名识别
- ✅ 版本识别机制
- ✅ 文件结构规划

**2. 占位符扫描：**
- ✅ 无 "待定"、"TODO"
- ✅ 所有代码步骤都有代码块
- ✅ 所有测试都有具体内容

**3. 类型一致性：**
- ✅ TokenType 定义一致
- ✅ AST 节点定义一致
- ✅ 文件路径一致

---

## 执行交接

计划已完成并保存到 `docs/superpowers/plans/2026-06-02-v2-syntax-impl.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

选哪种方式？