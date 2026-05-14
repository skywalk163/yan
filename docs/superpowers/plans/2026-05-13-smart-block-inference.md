# 智能块推断实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 实现智能块推断机制，让解析器根据语法上下文自动判断块结束，减少冗余的结束符。

**架构：** 在 Parser 中添加块栈机制，修改块解析逻辑，通过检查下一个 token 的类型和缩进来判断是否应该结束当前块。

**技术栈：** Python 3.9+, pytest

---

## 文件结构

**修改文件：**
- `yan/parser.py` - 添加块栈机制，修改块解析逻辑
- `yan/lexer.py` - 添加缩进跟踪（可选增强）

**创建文件：**
- `yan/tests/test_smart_block.py` - 智能块推断的单元测试

**更新文件：**
- `yan/examples/block.yan` - 移除冗余的结束符
- `yan/tests/basic_tests.yan` - 移除冗余的结束符

---

## 任务 1：添加块栈机制

**文件：**
- 修改：`yan/parser.py:37-72`（Parser 类初始化部分）
- 创建：`yan/tests/test_smart_block.py`

- [ ] **步骤 1：编写失败的测试 - 块栈基本操作**

```python
# yan/tests/test_smart_block.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import Parser, BlockStack

def test_block_stack_push_pop():
    """测试块栈的 push 和 pop 操作"""
    stack = BlockStack()
    stack.push('FUNC', 0)
    assert stack.current() == ('FUNC', 0)
    
    stack.push('IF', 2)
    assert stack.current() == ('IF', 2)
    
    result = stack.pop()
    assert result == ('IF', 2)
    assert stack.current() == ('FUNC', 0)

def test_block_stack_empty():
    """测试空栈"""
    stack = BlockStack()
    assert stack.current() is None
    assert stack.pop() is None

def test_block_stack_depth():
    """测试栈深度"""
    stack = BlockStack()
    assert stack.depth() == 0
    
    stack.push('FUNC', 0)
    assert stack.depth() == 1
    
    stack.push('IF', 2)
    assert stack.depth() == 2
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：FAIL，报错 "cannot import name 'BlockStack'"

- [ ] **步骤 3：实现 BlockStack 类**

```python
# yan/parser.py
# 在 Parser 类之前添加 BlockStack 类

class BlockStack:
    """块栈，用于跟踪当前块的状态"""
    
    def __init__(self):
        self.stack = []  # [(block_type, indent_level)]
    
    def push(self, block_type: str, indent_level: int):
        """压入新块"""
        self.stack.append((block_type, indent_level))
    
    def pop(self):
        """弹出块"""
        if self.stack:
            return self.stack.pop()
        return None
    
    def current(self):
        """获取当前块"""
        if self.stack:
            return self.stack[-1]
        return None
    
    def depth(self):
        """获取栈深度"""
        return len(self.stack)
    
    def is_empty(self):
        """检查栈是否为空"""
        return len(self.stack) == 0
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：PASS

- [ ] **步骤 5：在 Parser 类中添加 block_stack 属性**

```python
# yan/parser.py
# 修改 Parser.__init__ 方法

def __init__(self, use_global_verbs: bool = False):
    self.tokens: List[Token] = []
    self.pos: int = 0
    self.user_verbs: Set[str] = set()
    self.use_global_verbs = use_global_verbs
    self.block_stack = BlockStack()  # 添加块栈
```

- [ ] **步骤 6：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：PASS

- [ ] **步骤 7：Commit**

```bash
cd /g/dumategithub/newlisp
git add yan/parser.py yan/tests/test_smart_block.py
git commit -m "feat: add BlockStack mechanism for smart block inference"
```

---

## 任务 2：实现 `_should_end_block()` 方法

**文件：**
- 修改：`yan/parser.py`（添加新方法）
- 修改：`yan/tests/test_smart_block.py`（添加测试）

- [ ] **步骤 1：编写失败的测试 - 块结束判断**

```python
# yan/tests/test_smart_block.py
# 添加以下测试

def test_should_end_block_at_eof():
    """测试文件结束时结束块"""
    from lexer import Lexer
    
    code = "定x=1。"
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    parser.tokens = tokens
    parser.pos = len(tokens) - 1  # 指向 EOF
    
    assert parser._should_end_block(0) == True

def test_should_end_block_at_define():
    """测试遇到新定义时结束块"""
    from lexer import Lexer
    
    code = "定x=1。定y=2。"
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    parser.tokens = tokens
    parser.pos = 3  # 指向第二个 '定'
    
    assert parser._should_end_block(0) == True

def test_should_end_block_at_if():
    """测试遇到条件语句时结束块"""
    from lexer import Lexer
    
    code = "若真则1。若假则0。"
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    parser.tokens = tokens
    parser.pos = 5  # 指向第二个 '若'
    
    assert parser._should_end_block(0) == True

def test_should_not_end_block_in_middle():
    """测试块中间不应结束"""
    from lexer import Lexer
    
    code = "定x=1。定y=2。"
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    parser.tokens = tokens
    parser.pos = 1  # 指向 'x'
    
    assert parser._should_end_block(0) == False
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py::test_should_end_block_at_eof -v`
预期：FAIL，报错 "Parser has no attribute '_should_end_block'"

- [ ] **步骤 3：实现 `_should_end_block()` 方法**

```python
# yan/parser.py
# 在 Parser 类中添加以下方法

def _should_end_block(self, block_start_indent: int) -> bool:
    """
    判断是否应该结束当前块
    
    参数：
        block_start_indent: 块开始时的缩进级别
    
    返回：
        True 如果应该结束块，False 否则
    """
    # 情况 1：文件结束
    if self._is_at_end():
        return True
    
    # 情况 2：遇到新的定义
    if self._check_word('定'):
        return True
    
    # 情况 3：遇到同层级关键字
    if self._current().type == TokenType.WORD:
        word = self._current().value
        # 这些关键字表示新的块开始，应该结束当前块
        if word in {'若', '遍历', '当', '测', '套'}:
            return True
    
    # 情况 4：缩进减少（如果实现了缩进跟踪）
    # next_indent = self._peek_next_line_indent()
    # if next_indent < block_start_indent:
    #     return True
    
    return False
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
cd /g/dumategithub/newlisp
git add yan/parser.py yan/tests/test_smart_block.py
git commit -m "feat: implement _should_end_block() method"
```

---

## 任务 3：修改 `_parse_block()` 方法

**文件：**
- 修改：`yan/parser.py:352-376`（_parse_block 方法）
- 修改：`yan/tests/test_smart_block.py`（添加测试）

- [ ] **步骤 1：编写失败的测试 - 智能块解析**

```python
# yan/tests/test_smart_block.py
# 添加以下测试

def test_parse_single_line_block():
    """测试单行块"""
    from lexer import Lexer
    
    code = "定x=1。"
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    assert ast.statements[0].name == 'x'

def test_parse_multi_line_block_auto_end():
    """测试多行块自动结束"""
    from lexer import Lexer
    
    code = """
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    # 验证函数定义
    define = ast.statements[0]
    assert define.name == '距离'
    # 验证函数体是 Block
    assert hasattr(define.value, 'body')
    # 验证块包含 2 个语句
    assert hasattr(define.value.body, 'statements')
    assert len(define.value.body.statements) == 2

def test_parse_consecutive_definitions():
    """测试连续定义"""
    from lexer import Lexer
    
    code = """
定x=1。
定y=2。
定z=加x y。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 3
    assert ast.statements[0].name == 'x'
    assert ast.statements[1].name == 'y'
    assert ast.statements[2].name == 'z'
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py::test_parse_multi_line_block_auto_end -v`
预期：FAIL（当前实现可能无法正确解析）

- [ ] **步骤 3：修改 `_parse_block()` 方法**

```python
# yan/parser.py
# 替换现有的 _parse_block 方法

def _parse_block(self) -> Node:
    """解析代码块，智能推断结束"""
    statements = []
    block_start_indent = self._get_current_indent()
    
    # 压入块栈
    self.block_stack.push('BLOCK', block_start_indent)
    
    while not self._is_at_end():
        # 跳过句号
        if self._current().type == TokenType.DOT:
            self._advance()
            
            # 检查是否应该结束块
            if self._should_end_block(block_start_indent):
                break
            continue
        
        # 块结束条件
        if self._is_block_end():
            break
        
        # 解析语句
        stmt = self._parse_statement()
        if stmt:
            statements.append(stmt)
    
    # 弹出块栈
    self.block_stack.pop()
    
    if len(statements) == 0:
        return Nil()
    elif len(statements) == 1:
        return statements[0]
    else:
        return Block(statements)

def _get_current_indent(self) -> int:
    """获取当前缩进级别（简化实现）"""
    # 简化实现：返回 0
    # 完整实现需要从 lexer 获取缩进信息
    return 0
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
cd /g/dumategithub/newlisp
git add yan/parser.py yan/tests/test_smart_block.py
git commit -m "feat: modify _parse_block() for smart block inference"
```

---

## 任务 4：修改函数定义解析

**文件：**
- 修改：`yan/parser.py:277-350`（_parse_define 方法）
- 修改：`yan/tests/test_smart_block.py`（添加测试）

- [ ] **步骤 1：编写失败的测试 - 单行和多行函数**

```python
# yan/tests/test_smart_block.py
# 添加以下测试

def test_single_line_function():
    """测试单行函数"""
    from lexer import Lexer
    
    code = "定阶乘=函n 若n等1则1否则n乘阶乘n减1。"
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    define = ast.statements[0]
    assert define.name == '阶乘'
    # 验证是 Lambda
    assert hasattr(define.value, 'params')
    assert define.value.params == ['n']

def test_multi_line_function():
    """测试多行函数"""
    from lexer import Lexer
    
    code = """
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    define = ast.statements[0]
    assert define.name == '距离'
    # 验证是 Lambda
    assert hasattr(define.value, 'params')
    assert define.value.params == ['a', 'b']
    # 验证 body 是 Block
    assert hasattr(define.value.body, 'statements')
    assert len(define.value.body.statements) == 2
```

- [ ] **步骤 2：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py::test_single_line_function -v`
预期：PASS（当前实现应该已经支持）

- [ ] **步骤 3：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py::test_multi_line_function -v`
预期：PASS（如果失败，需要修改 _parse_define）

- [ ] **步骤 4：如果需要，修改 `_parse_define()` 方法**

如果测试失败，修改 `_parse_define()` 方法以确保正确处理多行函数：

```python
# yan/parser.py
# 检查 _parse_define 方法，确保它正确调用 _parse_block()

def _parse_define(self) -> Define:
    self._advance()  # 消耗 '定'
    
    # 收集连续的 WORD 作为名称
    name_parts = []
    while self._current().type == TokenType.WORD:
        next_tok = self._peek(1)
        if next_tok.type == TokenType.EQUALS:
            name_parts.append(self._advance().value)
            break
        name_parts.append(self._advance().value)
    
    if not name_parts:
        raise ParserError("期望标识符", self._current().line, self._current().col)
    
    name = ''.join(name_parts)
    
    self._expect(TokenType.EQUALS, "期望 '='")
    
    # 解析值
    value = self._parse_expression()
    
    return Define(name, value)
```

- [ ] **步骤 5：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：PASS

- [ ] **步骤 6：Commit**

```bash
cd /g/dumategithub/newlisp
git add yan/parser.py yan/tests/test_smart_block.py
git commit -m "feat: ensure _parse_define() works with smart block inference"
```

---

## 任务 5：修改条件语句解析

**文件：**
- 修改：`yan/parser.py:554-600`（_parse_if 方法）
- 修改：`yan/tests/test_smart_block.py`（添加测试）

- [ ] **步骤 1：编写失败的测试 - 条件语句块**

```python
# yan/tests/test_smart_block.py
# 添加以下测试

def test_if_with_block():
    """测试带块的条件语句"""
    from lexer import Lexer
    
    code = """
若x大0则：
  印"正数"。
  印x。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    if_node = ast.statements[0]
    # 验证是 If 节点
    assert hasattr(if_node, 'cond')
    assert hasattr(if_node, 'then_branch')
    # 验证 then_branch 是 Block
    assert hasattr(if_node.then_branch, 'statements')
    assert len(if_node.then_branch.statements) == 2

def test_if_else_with_block():
    """测试带 else 块的条件语句"""
    from lexer import Lexer
    
    code = """
若x大0则：
  印"正数"。
否则：
  印"非正数"。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    if_node = ast.statements[0]
    # 验证有 else 分支
    assert if_node.else_branch is not None
    assert hasattr(if_node.else_branch, 'statements')
```

- [ ] **步骤 2：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py::test_if_with_block -v`
预期：PASS（当前实现应该已经支持）

- [ ] **步骤 3：如果需要，修改 `_parse_if()` 方法**

如果测试失败，确保 `_parse_if()` 正确处理块结束：

```python
# yan/parser.py
# 检查 _parse_if 方法，确保它正确处理块结束

def _parse_if(self) -> If:
    """解析条件语句：若 条件 则：分支。否则：分支。"""
    self._advance()  # 消耗 '若'
    
    # 解析条件
    cond = self._parse_term()
    
    self._expect(TokenType.WORD, "期望 '则'")
    
    # 检查是否有 '：'（块开始标记）
    has_block = self._current().type == TokenType.COLON
    if has_block:
        self._advance()  # 消耗 '：'
    
    # 解析 then 分支
    if has_block:
        then_branch = self._parse_block_until({'否则'})
    else:
        then_branch = self._parse_expr_until({'否则'})
    
    else_branch = None
    # 跳过可能的句号
    if self._current().type == TokenType.DOT:
        self._advance()
    if self._check_word('否则'):
        self._advance()
        # 检查是否有 '：'
        if self._current().type == TokenType.COLON:
            self._advance()  # 消耗 '：'
            else_branch = self._parse_block_until(set())
        else:
            else_branch = self._parse_expr_until(set())
    
    return If(cond, then_branch, else_branch)
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
cd /g/dumategithub/newlisp
git add yan/parser.py yan/tests/test_smart_block.py
git commit -m "feat: ensure _parse_if() works with smart block inference"
```

---

## 任务 6：修改循环语句解析

**文件：**
- 修改：`yan/parser.py`（_parse_foreach 和 _parse_while 方法）
- 修改：`yan/tests/test_smart_block.py`（添加测试）

- [ ] **步骤 1：编写失败的测试 - 循环语句块**

```python
# yan/tests/test_smart_block.py
# 添加以下测试

def test_foreach_with_block():
    """测试遍历循环"""
    from lexer import Lexer
    
    code = """
遍历x 于 列1 2 3：
  印x。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    foreach = ast.statements[0]
    # 验证是 ForEach 节点
    assert hasattr(foreach, 'var')
    assert foreach.var == 'x'
    assert hasattr(foreach, 'body')

def test_while_with_block():
    """测试当循环"""
    from lexer import Lexer
    
    code = """
当x小10：
  印x。
  定x=加x 1。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    while_node = ast.statements[0]
    # 验证是 While 节点
    assert hasattr(while_node, 'cond')
    assert hasattr(while_node, 'body')
```

- [ ] **步骤 2：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：PASS（当前实现应该已经支持）

- [ ] **步骤 3：如果需要，修改循环解析方法**

如果测试失败，确保循环解析方法正确处理块结束。

- [ ] **步骤 4：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
cd /g/dumategithub/newlisp
git add yan/parser.py yan/tests/test_smart_block.py
git commit -m "feat: ensure loop parsing works with smart block inference"
```

---

## 任务 7：修改测试框架解析

**文件：**
- 修改：`yan/parser.py`（_parse_test 和 _parse_test_suite 方法）
- 修改：`yan/tests/test_smart_block.py`（添加测试）

- [ ] **步骤 1：编写失败的测试 - 测试框架块**

```python
# yan/tests/test_smart_block.py
# 添加以下测试

def test_test_suite_auto_end():
    """测试测试套件自动结束"""
    from lexer import Lexer
    
    code = """
套 "算术运算测试"：
  测 "加法运算"：
    断言等 加1 2 3。

  测 "减法运算"：
    断言等 减5 3 2。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    suite = ast.statements[0]
    # 验证是 TestSuite
    assert hasattr(suite, 'tests')
    assert len(suite.tests) == 2
```

- [ ] **步骤 2：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py::test_test_suite_auto_end -v`
预期：PASS

- [ ] **步骤 3：如果需要，修改测试框架解析方法**

如果测试失败，确保 `_parse_test_suite()` 正确处理块结束。

- [ ] **步骤 4：运行测试验证通过**

运行：`cd /g/dumategithub/newlisp/yan && python -m pytest tests/test_smart_block.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
cd /g/dumategithub/newlisp
git add yan/parser.py yan/tests/test_smart_block.py
git commit -m "feat: ensure test framework parsing works with smart block inference"
```

---

## 任务 8：集成测试

**文件：**
- 运行：所有现有示例程序
- 修改：`yan/examples/block.yan`
- 修改：`yan/tests/basic_tests.yan`

- [ ] **步骤 1：运行现有示例程序验证兼容性**

运行：
```bash
cd /g/dumategithub/newlisp/yan
python main.py examples/basic.yan
python main.py examples/factorial.yan
python main.py examples/block.yan
python main.py examples/hanoi.yan
```
预期：所有程序正常运行

- [ ] **步骤 2：更新 block.yan 示例**

```yan
# yan/examples/block.yan
-- 移除冗余的结束符

定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。

印"距离示例："。
印距离3 7。
印距离7 3。
印距离10 5。

定统计=函语文 数学 英语：
  定总分=$(语文 + 数学 + 英语)。
  定均值=$(总分 / 3)。
  列总分 均值。

印"成绩统计："。
印统计85 92 78。

定体积=函x y z：
  定底面积=$(x * y)。
  定结果=$(底面积 * z)。
  结果。

印"体积计算："。
印体积3 4 5。
```

- [ ] **步骤 3：运行更新后的示例验证**

运行：`cd /g/dumategithub/newlisp/yan && python main.py examples/block.yan`
预期：正常运行

- [ ] **步骤 4：更新测试文件**

```yan
# yan/tests/basic_tests.yan
-- 移除冗余的结束符

套 "算术运算测试"：
  测 "加法运算"：
    断言等 加 1 2 3。

  测 "减法运算"：
    断言等 减 5 3 2。

  测 "乘法运算"：
    断言等 乘 3 4 12。

  测 "除法运算"：
    断言等 除 10 2 5。

套 "数据操作测试"：
  测 "数据创建"：
    定 数据 = 列 1 2 3。
    断言等 长 数据 3。

  测 "首元素"：
    定 数据 = 列 1 2 3。
    断言等 首 数据 1。

  测 "余元素"：
    定 数据 = 列 1 2 3。
    断言等 余 数据 列 2 3。

套 "高阶函数测试"：
  测 "映射函数"：
    定 数据 = 列 1 2 3。
    定 平方 = 函 x 乘 x x。
    定 值 = 皆 平方 数据。
    断言等 值 列 1 4 9。

  测 "过滤函数"：
    定 数据 = 列 1 2 3 4 5。
    定 是偶数 = 函 x 等 模 x 2 0。
    定 值 = 只 是偶数 数据。
    断言等 值 列 2 4。

  测 "归约函数"：
    定 数据 = 列 1 2 3 4 5。
    定 值 = 归 加 0 数据。
    断言等 值 15。

套 "条件语句测试"：
  测 "条件为真"：
    定 值 = 若 大 3 2 则 1 否则 0。
    断言等 值 1。

  测 "条件为假"：
    定 值 = 若 小 3 2 则 1 否则 0。
    断言等 值 0。

套 "递归函数测试"：
  测 "阶乘函数"：
    定 阶乘 = 函 n
      若 等 n 1 则 1 否则 乘 n 阶乘 减 n 1。
    断言等 阶乘 5 120。

  测 "斐波那契数列"：
    定 斐波 = 函 n
      若 小 n 2 则 n 否则 加 斐波 减 n 1 斐波 减 n 2。
    断言等 斐波 10 55。
```

- [ ] **步骤 5：运行测试验证**

运行：`cd /g/dumategithub/newlisp/yan && python test_runner.py tests/basic_tests.yan`
预期：所有测试通过

- [ ] **步骤 6：Commit**

```bash
cd /g/dumategithub/newlisp
git add yan/examples/block.yan yan/tests/basic_tests.yan
git commit -m "refactor: remove redundant block terminators in examples and tests"
```

---

## 任务 9：文档更新

**文件：**
- 修改：`yan/docs/LANGUAGE_SPEC.md`
- 修改：`yan/examples/README.md`

- [ ] **步骤 1：更新语言规范文档**

在 `yan/docs/LANGUAGE_SPEC.md` 中更新块语法的说明：

```markdown
### 3.3 块结构

**单行块：** 无需 `：` 开始，无需结束符
```yan
定阶乘=函n 若n等1则1否则n乘阶乘n减1。
```

**多行块：** 需要 `：` 开始，最后一个 `。` 自动结束
```yan
定阶乘=函n：
  若n等1则：
    1。
  否则：
    n乘阶乘n减1。
```

**块结束规则：**
1. 遇到 `。` 且下一个 token 是新定义 → 结束当前块
2. 遇到 `。` 且下一个 token 是同层级关键字 → 结束当前块
3. 遇到 `。` 且到达文件结束 → 结束所有块
```

- [ ] **步骤 2：更新示例 README**

在 `yan/examples/README.md` 中更新示例说明。

- [ ] **步骤 3：Commit**

```bash
cd /g/dumategithub/newlisp
git add yan/docs/LANGUAGE_SPEC.md yan/examples/README.md
git commit -m "docs: update documentation for smart block inference"
```

---

## 完成检查

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 所有现有示例程序正常运行
- [ ] 文档已更新
- [ ] 代码已 commit

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 解析器复杂度增加 | 充分测试，代码审查 |
| 边界情况处理不当 | 详细的测试用例 |
| 向后兼容性问题 | 保留旧语法的支持 |
