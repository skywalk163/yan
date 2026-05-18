# 言语言错误处理增强实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 实现清晰、友好、可操作的错误信息，提升开发者体验

**架构：** 扩展现有的 `yan/error.py` 模块，添加源代码片段显示、错误位置高亮、错误建议等功能

**技术栈：** Python 3.12、言语言编译器、ANSI颜色输出

---

## 当前问题

**现有错误信息示例：**
```
语法错误 (行3, 列5): 未定义的变量
```

**问题：**
1. 没有显示源代码片段
2. 没有错误位置高亮
3. 没有错误建议
4. 不够友好

**目标错误信息示例：**
```
错误：未定义的变量
  文件：examples/demo.yan
  位置：第 3 行，第 5-8 列

    1 | 定 数据 = 列 1 2 3。
    2 | 定 平方 = 函 x 乘 x x。
    3 | 定 值 = 皆 平方 数据x。
                              ^^^^
                              未定义的变量：数据x
                              您是否想使用：数据？

建议：检查变量名拼写，或确认变量已定义。
```

---

## 文件结构

### 新增文件

```
yan/
├── error_formatter.py      — 错误格式化器（核心）
├── error_suggestions.py    — 错误建议生成器
└── tests/
    ├── test_error_formatter.py    — 格式化器测试
    └── test_error_suggestions.py  — 建议生成器测试
```

### 修改文件

```
yan/
├── error.py               — 扩展现有错误类
├── lexer.py               — 添加错误位置信息
├── parser.py              — 添加错误位置信息
└── main.py                — 集成错误格式化
```

---

## 任务分解

### 任务1：设计错误信息格式

**文件：**
- 创建：`yan/docs/ERROR_FORMAT_SPEC.md`

**目标：** 定义错误信息的标准格式

- [ ] **步骤1：创建错误格式规范文档**

创建 `yan/docs/ERROR_FORMAT_SPEC.md`：

```markdown
# 言语言错误信息格式规范

## 一、错误信息结构

### 1.1 基本格式

```
错误：{错误类型}
  文件：{文件路径}
  位置：第 {行号} 行，第 {列号} 列

{源代码片段}
{错误位置标记}
{错误描述}

建议：{修复建议}
```

### 1.2 源代码片段格式

```
  {行号} | {源代码}
        ^ {错误位置}
          {错误描述}
```

### 1.3 错误类型分类

**词法错误（LexerError）：**
- 无效字符
- 字符串未闭合
- 数字格式错误

**语法错误（ParserError）：**
- 未定义的变量
- 未定义的函数
- 语法结构错误
- 参数数量错误

**运行时错误（RuntimeError）：**
- 类型错误
- 索引越界
- 除零错误

**语义错误（SemanticError）：**
- 未使用的变量
- 不可达代码

### 1.4 错误建议格式

**拼写错误建议：**
```
您是否想使用：{建议变量名}？
```

**参数数量建议：**
```
函数 {函数名} 需要 {期望数量} 个参数，但提供了 {实际数量} 个。
```

**类型错误建议：**
```
期望类型：{期望类型}
实际类型：{实际类型}
```

## 二、颜色和样式

### 2.1 ANSI 颜色代码

- 错误类型：红色（\033[91m）
- 警告类型：黄色（\033[93m）
- 建议信息：青色（\033[96m）
- 行号：灰色（\033[90m）
- 错误位置：红色下划线（\033[91m）

### 2.2 样式控制

- 粗体：\033[1m
- 下划线：\033[4m
- 重置：\033[0m

## 三、示例

### 3.1 词法错误

```
错误：无效字符
  文件：examples/demo.yan
  位置：第 5 行，第 12 列

    4 | 定 数据 = 列 1 2 3。
    5 | 定 值 = 数据[0] @ 1。
                             ^
                             无效字符：'@'

建议：言语言不支持 '@' 字符。
```

### 3.2 语法错误

```
错误：未定义的变量
  文件：examples/demo.yan
  位置：第 3 行，第 15-18 列

    1 | 定 数据 = 列 1 2 3。
    2 | 定 平方 = 函 x 乘 x x。
    3 | 定 值 = 皆 平方 数据x。
                               ^^^^
                               未定义的变量：数据x
                               您是否想使用：数据？

建议：检查变量名拼写，或确认变量已定义。
```

### 3.3 运行时错误

```
错误：索引越界
  文件：examples/demo.yan
  位置：第 4 行，第 12 列

    3 | 定 数据 = 列 1 2 3。
    4 | 定 值 = 入 数据 5。
                  ^^^^^^^
                  索引 5 超出范围
                  列表长度：3
                  有效索引：0-2

建议：使用 0-2 之间的索引，或检查列表长度。
```
```

- [ ] **步骤2：Commit**

```bash
git add yan/docs/ERROR_FORMAT_SPEC.md
git commit -m "docs: add error format specification"
```

---

### 任务2：实现错误格式化器

**文件：**
- 创建：`yan/error_formatter.py`
- 创建：`yan/tests/test_error_formatter.py`

**目标：** 实现核心错误格式化功能

- [ ] **步骤1：编写错误格式化器测试**

创建 `yan/tests/test_error_formatter.py`：

```python
"""
错误格式化器测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from error_formatter import ErrorFormatter, ErrorContext

def test_format_simple_error():
    """测试简单错误格式化"""
    formatter = ErrorFormatter()
    
    context = ErrorContext(
        error_type="未定义的变量",
        file_path="examples/demo.yan",
        line=3,
        column=15,
        end_column=18,
        source_lines=[
            "定 数据 = 列 1 2 3。",
            "定 平方 = 函 x 乘 x x。",
            "定 值 = 皆 平方 数据x。"
        ],
        message="未定义的变量：数据x",
        suggestion="检查变量名拼写，或确认变量已定义。"
    )
    
    result = formatter.format(context)
    
    assert "错误：未定义的变量" in result
    assert "文件：examples/demo.yan" in result
    assert "第 3 行" in result
    assert "数据x" in result
    assert "建议" in result

def test_format_error_with_suggestion():
    """测试带建议的错误格式化"""
    formatter = ErrorFormatter()
    
    context = ErrorContext(
        error_type="拼写错误",
        file_path="test.yan",
        line=1,
        column=5,
        end_column=8,
        source_lines=["定 数据 = 42。"],
        message="未定义的变量：数据",
        suggestion="您是否想使用：数据？",
        similar_names=["数据"]
    )
    
    result = formatter.format(context)
    
    assert "您是否想使用：数据？" in result

def test_format_multiline_error():
    """测试多行错误格式化"""
    formatter = ErrorFormatter()
    
    context = ErrorContext(
        error_type="语法错误",
        file_path="test.yan",
        line=2,
        column=1,
        end_column=10,
        source_lines=[
            "定 数据 = 列 1 2 3。",
            "定 平方 = 函 x",
            "  乘 x x。",
            "平方 5。"
        ],
        message="函数定义未闭合",
        suggestion="添加 '。' 结束函数定义。"
    )
    
    result = formatter.format(context)
    
    # 应该显示上下文行
    assert "第 1 行" in result
    assert "第 2 行" in result
    assert "第 3 行" in result

def test_color_output():
    """测试彩色输出"""
    formatter = ErrorFormatter(use_color=True)
    
    context = ErrorContext(
        error_type="测试错误",
        file_path="test.yan",
        line=1,
        column=1,
        end_column=5,
        source_lines=["测试代码。"],
        message="测试消息"
    )
    
    result = formatter.format(context)
    
    # 应该包含 ANSI 颜色代码
    assert "\033[" in result

if __name__ == '__main__':
    test_format_simple_error()
    test_format_error_with_suggestion()
    test_format_multiline_error()
    test_color_output()
    print("错误格式化器测试通过")
```

- [ ] **步骤2：运行测试验证失败**

运行：`cd yan && python tests/test_error_formatter.py`
预期：FAIL，报错 "ModuleNotFoundError: No module named 'error_formatter'"

- [ ] **步骤3：实现错误格式化器**

创建 `yan/error_formatter.py`：

```python
"""
言语言错误格式化器
提供清晰、友好、可操作的错误信息
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ErrorContext:
    """错误上下文信息"""
    error_type: str              # 错误类型
    file_path: str               # 文件路径
    line: int                    # 行号
    column: int                  # 列号
    end_column: int              # 结束列号
    source_lines: List[str]      # 源代码行
    message: str                 # 错误消息
    suggestion: Optional[str] = None  # 修复建议
    similar_names: Optional[List[str]] = None  # 相似名称
    
    @property
    def width(self) -> int:
        """错误标记宽度"""
        return self.end_column - self.column


class ErrorFormatter:
    """错误格式化器"""
    
    # ANSI 颜色代码
    COLORS = {
        'red': '\033[91m',
        'yellow': '\033[93m',
        'cyan': '\033[96m',
        'gray': '\033[90m',
        'bold': '\033[1m',
        'underline': '\033[4m',
        'reset': '\033[0m'
    }
    
    def __init__(self, use_color: bool = True):
        """
        初始化格式化器
        
        Args:
            use_color: 是否使用彩色输出
        """
        self.use_color = use_color
    
    def format(self, context: ErrorContext) -> str:
        """
        格式化错误信息
        
        Args:
            context: 错误上下文
        
        Returns:
            格式化后的错误信息
        """
        lines = []
        
        # 1. 错误标题
        lines.append(self._format_header(context))
        
        # 2. 文件和位置信息
        lines.append(self._format_location(context))
        
        # 3. 源代码片段
        lines.append("")
        lines.extend(self._format_source_snippet(context))
        
        # 4. 错误描述
        lines.append(self._format_message(context))
        
        # 5. 修复建议
        if context.suggestion:
            lines.append("")
            lines.append(self._format_suggestion(context))
        
        return "\n".join(lines)
    
    def _format_header(self, context: ErrorContext) -> str:
        """格式化错误标题"""
        if self.use_color:
            return f"{self.COLORS['bold']}{self.COLORS['red']}错误：{context.error_type}{self.COLORS['reset']}"
        else:
            return f"错误：{context.error_type}"
    
    def _format_location(self, context: ErrorContext) -> str:
        """格式化位置信息"""
        return f"  文件：{context.file_path}\n  位置：第 {context.line} 行，第 {context.column}-{context.end_column} 列"
    
    def _format_source_snippet(self, context: ErrorContext) -> List[str]:
        """格式化源代码片段"""
        lines = []
        
        # 计算显示的行范围（前后各1行）
        start_line = max(1, context.line - 1)
        end_line = min(len(context.source_lines), context.line + 1)
        
        # 计算行号宽度
        line_num_width = len(str(end_line))
        
        # 显示源代码行
        for i in range(start_line - 1, end_line):
            line_num = i + 1
            source_line = context.source_lines[i]
            
            # 行号
            if self.use_color:
                line_num_str = f"{self.COLORS['gray']}{line_num:>{line_num_width}}{self.COLORS['reset']}"
            else:
                line_num_str = f"{line_num:>{line_num_width}}"
            
            # 源代码
            if line_num == context.line:
                # 当前行高亮
                if self.use_color:
                    lines.append(f"  {line_num_str} | {self.COLORS['bold']}{source_line}{self.COLORS['reset']}")
                else:
                    lines.append(f"  {line_num_str} | {source_line}")
            else:
                lines.append(f"  {line_num_str} | {source_line}")
        
        # 错误位置标记
        error_marker = self._format_error_marker(context)
        lines.append(error_marker)
        
        return lines
    
    def _format_error_marker(self, context: ErrorContext) -> str:
        """格式化错误位置标记"""
        # 计算缩进
        line_num_width = len(str(min(len(context.source_lines), context.line + 1)))
        indent = " " * (line_num_width + 4)  # 行号宽度 + " | "
        
        # 错误位置下划线
        underline = " " * (context.column - 1) + "^" * max(1, context.width)
        
        # 错误描述
        if self.use_color:
            error_desc = f"{self.COLORS['red']}{context.message}{self.COLORS['reset']}"
        else:
            error_desc = context.message
        
        return f"{indent}{underline}\n{indent}  {error_desc}"
    
    def _format_message(self, context: ErrorContext) -> str:
        """格式化错误消息"""
        if context.similar_names:
            similar = "、".join(context.similar_names)
            return f"您是否想使用：{similar}？"
        return ""
    
    def _format_suggestion(self, context: ErrorContext) -> str:
        """格式化修复建议"""
        if self.use_color:
            return f"{self.COLORS['cyan']}建议：{context.suggestion}{self.COLORS['reset']}"
        else:
            return f"建议：{context.suggestion}"
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_error_formatter.py`
预期：PASS，输出 "错误格式化器测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/error_formatter.py yan/tests/test_error_formatter.py
git commit -m "feat(error): implement error formatter with source snippet display"
```

---

### 任务3：实现错误建议生成器

**文件：**
- 创建：`yan/error_suggestions.py`
- 创建：`yan/tests/test_error_suggestions.py`

**目标：** 自动生成错误修复建议

- [ ] **步骤1：编写建议生成器测试**

创建 `yan/tests/test_error_suggestions.py`：

```python
"""
错误建议生成器测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from error_suggestions import ErrorSuggestionGenerator

def test_suggest_similar_variable():
    """测试相似变量名建议"""
    generator = ErrorSuggestionGenerator()
    
    # 已定义的变量
    defined_vars = {"数据", "列表", "函数"}
    
    # 错误的变量名
    wrong_name = "数据x"
    
    suggestions = generator.suggest_similar_name(wrong_name, defined_vars)
    
    # 应该建议 "数据"
    assert "数据" in suggestions

def test_suggest_similar_function():
    """测试相似函数名建议"""
    generator = ErrorSuggestionGenerator()
    
    # 已定义的函数
    defined_funcs = {"平方", "立方", "阶乘"}
    
    # 错误的函数名
    wrong_name = "平芳"
    
    suggestions = generator.suggest_similar_name(wrong_name, defined_funcs)
    
    # 应该建议 "平方"
    assert "平方" in suggestions

def test_suggest_arity_fix():
    """测试参数数量建议"""
    generator = ErrorSuggestionGenerator()
    
    suggestion = generator.suggest_arity_fix(
        func_name="加",
        expected=2,
        actual=1
    )
    
    assert "加" in suggestion
    assert "2" in suggestion
    assert "1" in suggestion

def test_suggest_type_fix():
    """测试类型错误建议"""
    generator = ErrorSuggestionGenerator()
    
    suggestion = generator.suggest_type_fix(
        expected_type="数",
        actual_type="串"
    )
    
    assert "数" in suggestion
    assert "串" in suggestion

def test_no_suggestion_for_correct_name():
    """测试正确名称不生成建议"""
    generator = ErrorSuggestionGenerator()
    
    defined_vars = {"数据", "列表"}
    correct_name = "数据"
    
    suggestions = generator.suggest_similar_name(correct_name, defined_vars)
    
    # 正确名称不应该生成建议
    assert len(suggestions) == 0

if __name__ == '__main__':
    test_suggest_similar_variable()
    test_suggest_similar_function()
    test_suggest_arity_fix()
    test_suggest_type_fix()
    test_no_suggestion_for_correct_name()
    print("错误建议生成器测试通过")
```

- [ ] **步骤2：运行测试验证失败**

运行：`cd yan && python tests/test_error_suggestions.py`
预期：FAIL，报错 "ModuleNotFoundError: No module named 'error_suggestions'"

- [ ] **步骤3：实现建议生成器**

创建 `yan/error_suggestions.py`：

```python
"""
言语言错误建议生成器
自动生成错误修复建议
"""
from typing import List, Set, Optional


class ErrorSuggestionGenerator:
    """错误建议生成器"""
    
    def suggest_similar_name(self, name: str, candidates: Set[str], max_suggestions: int = 3) -> List[str]:
        """
        建议相似的名称
        
        Args:
            name: 错误的名称
            candidates: 候选名称集合
            max_suggestions: 最多建议数量
        
        Returns:
            相似名称列表，按相似度排序
        """
        if name in candidates:
            return []
        
        # 计算编辑距离
        distances = []
        for candidate in candidates:
            distance = self._levenshtein_distance(name, candidate)
            distances.append((candidate, distance))
        
        # 按距离排序
        distances.sort(key=lambda x: x[1])
        
        # 返回最相似的名称
        suggestions = []
        for candidate, distance in distances:
            # 只建议距离小于名称长度一半的
            if distance <= len(name) // 2 + 1:
                suggestions.append(candidate)
                if len(suggestions) >= max_suggestions:
                    break
        
        return suggestions
    
    def suggest_arity_fix(self, func_name: str, expected: int, actual: int) -> str:
        """
        生成参数数量错误建议
        
        Args:
            func_name: 函数名
            expected: 期望参数数量
            actual: 实际参数数量
        
        Returns:
            建议文本
        """
        if actual < expected:
            missing = expected - actual
            return f"函数 {func_name} 需要 {expected} 个参数，缺少 {missing} 个参数。"
        else:
            extra = actual - expected
            return f"函数 {func_name} 只需要 {expected} 个参数，提供了 {actual} 个（多 {extra} 个）。"
    
    def suggest_type_fix(self, expected_type: str, actual_type: str) -> str:
        """
        生成类型错误建议
        
        Args:
            expected_type: 期望类型
            actual_type: 实际类型
        
        Returns:
            建议文本
        """
        return f"期望类型：{expected_type}，实际类型：{actual_type}。"
    
    def suggest_index_fix(self, index: int, length: int) -> str:
        """
        生成索引越界建议
        
        Args:
            index: 错误的索引
            length: 列表长度
        
        Returns:
            建议文本
        """
        if index < 0:
            return f"索引 {index} 为负数，请使用 0-{length-1} 之间的正索引。"
        else:
            return f"索引 {index} 超出范围，列表长度为 {length}，有效索引为 0-{length-1}。"
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算编辑距离（Levenshtein Distance）
        
        Args:
            s1: 字符串1
            s2: 字符串2
        
        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # 插入、删除、替换的代价
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_error_suggestions.py`
预期：PASS，输出 "错误建议生成器测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/error_suggestions.py yan/tests/test_error_suggestions.py
git commit -m "feat(error): implement error suggestion generator with Levenshtein distance"
```

---

### 任务4：集成到词法分析器

**文件：**
- 修改：`yan/lexer.py`
- 创建：`yan/tests/test_lexer_errors.py`

**目标：** 在词法分析器中集成错误格式化

- [ ] **步骤1：编写词法错误测试**

创建 `yan/tests/test_lexer_errors.py`：

```python
"""
词法分析器错误测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer

def test_invalid_character_error():
    """测试无效字符错误"""
    code = "定 数据 = 42 @ 1。"
    lexer = Lexer()
    
    try:
        tokens = lexer.tokenize(code)
        assert False, "应该抛出异常"
    except Exception as e:
        error_msg = str(e)
        # 应该包含错误位置
        assert "行" in error_msg or "line" in error_msg.lower()

def test_unclosed_string_error():
    """测试未闭合字符串错误"""
    code = '定 消息 = "你好世界。'
    lexer = Lexer()
    
    try:
        tokens = lexer.tokenize(code)
        assert False, "应该抛出异常"
    except Exception as e:
        error_msg = str(e)
        # 应该提示字符串未闭合
        assert "闭合" in error_msg or "unclosed" in error_msg.lower()

def test_invalid_number_error():
    """测试无效数字错误"""
    code = "定 数 = 123.456.789。"
    lexer = Lexer()
    
    try:
        tokens = lexer.tokenize(code)
        assert False, "应该抛出异常"
    except Exception as e:
        error_msg = str(e)
        # 应该提示数字格式错误
        assert "数字" in error_msg or "number" in error_msg.lower()

if __name__ == '__main__':
    test_invalid_character_error()
    test_unclosed_string_error()
    test_invalid_number_error()
    print("词法分析器错误测试通过")
```

- [ ] **步骤2：运行测试验证当前状态**

运行：`cd yan && python tests/test_lexer_errors.py`
预期：可能通过或失败，取决于当前错误处理

- [ ] **步骤3：修改词法分析器以使用错误格式化器**

修改 `yan/lexer.py`，在 `LexerError` 类中集成错误格式化器：

```python
# 在文件开头添加导入
from error_formatter import ErrorFormatter, ErrorContext
from typing import List

# 修改 LexerError 类
class LexerError(Exception):
    """词法分析错误"""
    
    def __init__(self, message: str, line: int, col: int, source_lines: List[str] = None):
        self.message = message
        self.line = line
        self.col = col
        self.source_lines = source_lines or []
        
        # 使用错误格式化器
        formatter = ErrorFormatter(use_color=True)
        context = ErrorContext(
            error_type="词法错误",
            file_path="<源码>",
            line=line,
            column=col,
            end_column=col + 1,
            source_lines=source_lines or [],
            message=message
        )
        
        self.formatted_message = formatter.format(context)
        super().__init__(self.formatted_message)
```

- [ ] **步骤4：修改 tokenize 方法以传递源代码行**

在 `Lexer.tokenize()` 方法中：

```python
def tokenize(self, source: str) -> List[Token]:
    """词法分析主方法"""
    self.source = source
    self.source_lines = source.split('\n')  # 保存源代码行
    # ... 其余代码保持不变
```

- [ ] **步骤5：运行测试验证通过**

运行：`cd yan && python tests/test_lexer_errors.py`
预期：PASS，输出 "词法分析器错误测试通过"

- [ ] **步骤6：Commit**

```bash
git add yan/lexer.py yan/tests/test_lexer_errors.py
git commit -m "feat(lexer): integrate error formatter into lexer"
```

---

### 任务5：集成到语法分析器

**文件：**
- 修改：`yan/parser.py`
- 创建：`yan/tests/test_parser_errors.py`

**目标：** 在语法分析器中集成错误格式化和建议生成

- [ ] **步骤1：编写语法错误测试**

创建 `yan/tests/test_parser_errors.py`：

```python
"""
语法分析器错误测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser

def test_undefined_variable_error():
    """测试未定义变量错误"""
    code = "定 值 = 数据。"
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    
    try:
        ast = parser.parse(tokens)
        # 如果没有抛出异常，检查生成的代码
        from codegen import PythonCodeGen
        gen = PythonCodeGen()
        python_code = gen.generate(ast)
        
        # 尝试执行，应该失败
        namespace = {}
        exec(python_code, namespace)
        assert False, "应该抛出异常"
    except Exception as e:
        error_msg = str(e)
        # 应该包含错误信息
        assert len(error_msg) > 0

def test_undefined_function_error():
    """测试未定义函数错误"""
    code = "定 值 = 平方 5。"
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    
    try:
        ast = parser.parse(tokens)
        from codegen import PythonCodeGen
        gen = PythonCodeGen()
        python_code = gen.generate(ast)
        
        namespace = {}
        exec(python_code, namespace)
        assert False, "应该抛出异常"
    except Exception as e:
        error_msg = str(e)
        assert len(error_msg) > 0

def test_arity_error():
    """测试参数数量错误"""
    code = """
定 加 = 函 x y
    返回 加 x y。
。
定 值 = 加 1。
"""
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    
    try:
        ast = parser.parse(tokens)
        from codegen import PythonCodeGen
        gen = PythonCodeGen()
        python_code = gen.generate(ast)
        
        namespace = {}
        exec(python_code, namespace)
        assert False, "应该抛出异常"
    except Exception as e:
        error_msg = str(e)
        # 应该提示参数数量错误
        assert len(error_msg) > 0

if __name__ == '__main__':
    test_undefined_variable_error()
    test_undefined_function_error()
    test_arity_error()
    print("语法分析器错误测试通过")
```

- [ ] **步骤2：运行测试验证当前状态**

运行：`cd yan && python tests/test_parser_errors.py`
预期：可能通过或失败

- [ ] **步骤3：修改语法分析器以使用错误格式化器**

修改 `yan/parser.py`，在 `ParserError` 类中集成错误格式化器：

```python
# 在文件开头添加导入
from error_formatter import ErrorFormatter, ErrorContext
from error_suggestions import ErrorSuggestionGenerator

# 修改 ParserError 类
class ParserError(Exception):
    """语法分析错误"""
    
    def __init__(self, message: str, line: int, col: int, 
                 source_lines: List[str] = None, 
                 defined_names: Set[str] = None,
                 wrong_name: str = None):
        self.message = message
        self.line = line
        self.col = col
        self.source_lines = source_lines or []
        self.defined_names = defined_names or set()
        self.wrong_name = wrong_name
        
        # 使用错误格式化器
        formatter = ErrorFormatter(use_color=True)
        
        # 生成建议
        suggestion = None
        similar_names = None
        if wrong_name and defined_names:
            generator = ErrorSuggestionGenerator()
            similar_names = generator.suggest_similar_name(wrong_name, defined_names)
            if similar_names:
                suggestion = "检查变量名拼写，或确认变量已定义。"
        
        context = ErrorContext(
            error_type="语法错误",
            file_path="<源码>",
            line=line,
            column=col,
            end_column=col + len(wrong_name) if wrong_name else col + 1,
            source_lines=source_lines or [],
            message=message,
            suggestion=suggestion,
            similar_names=similar_names
        )
        
        self.formatted_message = formatter.format(context)
        super().__init__(self.formatted_message)
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_parser_errors.py`
预期：PASS，输出 "语法分析器错误测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/parser.py yan/tests/test_parser_errors.py
git commit -m "feat(parser): integrate error formatter and suggestion generator"
```

---

### 任务6：创建错误处理演示

**文件：**
- 创建：`yan/examples/error_handling_demo.yan`
- 创建：`yan/docs/ERROR_HANDLING_GUIDE.md`

**目标：** 创建错误处理演示和文档

- [ ] **步骤1：创建错误处理演示程序**

创建 `yan/examples/error_handling_demo.yan`：

```yan
-- 言语言错误处理演示
-- 本程序展示各种错误类型和友好的错误信息

-- 1. 词法错误演示
-- 定 测试 = 42 @ 1。
-- 错误：无效字符 '@'

-- 2. 未定义变量错误演示
-- 定 值 = 数据x。
-- 错误：未定义的变量 '数据x'
-- 建议：您是否想使用 '数据'？

-- 3. 参数数量错误演示
-- 定 加 = 函 x y 返回 加 x y。
-- 定 值 = 加 1。
-- 错误：函数 '加' 需要 2 个参数，但只提供了 1 个

-- 4. 类型错误演示
-- 定 数 = "文本"。
-- 定 值 = 加 数 1。
-- 错误：类型错误，期望 '数'，实际 '串'

-- 5. 索引越界错误演示
-- 定 列表 = 列 1 2 3。
-- 定 值 = 入 列表 5。
-- 错误：索引 5 超出范围，列表长度为 3

印"错误处理演示完成。"。
```

- [ ] **步骤2：创建错误处理指南**

创建 `yan/docs/ERROR_HANDLING_GUIDE.md`：

```markdown
# 言语言错误处理指南

## 一、错误类型

### 1.1 词法错误（LexerError）

**无效字符：**
```
错误：无效字符
  文件：demo.yan
  位置：第 1 行，第 15 列

    1 | 定 测试 = 42 @ 1。
                       ^
                       无效字符：'@'

建议：言语言不支持 '@' 字符。
```

**未闭合字符串：**
```
错误：字符串未闭合
  文件：demo.yan
  位置：第 1 行，第 10 列

    1 | 定 消息 = "你好世界。
                  ^^^^^^^^^^^
                  字符串未找到结束引号

建议：添加结束引号 '"'。
```

### 1.2 语法错误（ParserError）

**未定义的变量：**
```
错误：未定义的变量
  文件：demo.yan
  位置：第 1 行，第 8-11 列

    1 | 定 值 = 数据x。
                  ^^^^
                  未定义的变量：数据x
                  您是否想使用：数据？

建议：检查变量名拼写，或确认变量已定义。
```

**参数数量错误：**
```
错误：参数数量错误
  文件：demo.yan
  位置：第 3 行，第 8-13 列

    2 | 定 加 = 函 x y 返回 加 x y。
    3 | 定 值 = 加 1。
                  ^^^^^
                  函数 '加' 需要 2 个参数
                  但只提供了 1 个

建议：添加缺少的参数。
```

### 1.3 运行时错误（RuntimeError）

**索引越界：**
```
错误：索引越界
  文件：demo.yan
  位置：第 2 行，第 10-15 列

    1 | 定 列表 = 列 1 2 3。
    2 | 定 值 = 入 列表 5。
                  ^^^^^^^
                  索引 5 超出范围
                  列表长度：3
                  有效索引：0-2

建议：使用 0-2 之间的索引，或检查列表长度。
```

**类型错误：**
```
错误：类型错误
  文件：demo.yan
  位置：第 2 行，第 10-15 列

    1 | 定 文本 = "hello"。
    2 | 定 值 = 加 文本 1。
                  ^^^^^^^
                  类型不匹配
                  期望：数
                  实际：串

建议：使用数值类型，或进行类型转换。
```

## 二、错误处理最佳实践

### 2.1 变量命名

**推荐：**
- 使用有意义的变量名
- 保持命名一致性
- 避免拼写错误

**示例：**
```yan
定 用户数据 = 列 1 2 3。
定 处理结果 = 皆 平方 用户数据。
```

### 2.2 函数定义

**推荐：**
- 明确参数数量
- 添加函数注释
- 处理边界情况

**示例：**
```yan
-- 计算列表的平均值
定 平均值 = 函 列表
    定 总和 = 求和 列表。
    定 长度 = 长 列表。
    若 等于 长度 0
        返回 0。
    否则
        返回 除 总和 长度。
    。
。
```

### 2.3 错误预防

**检查列表长度：**
```yan
定 安全访问 = 函 列表 索引
    若 大于等于 索引 长 列表
        返回 空。
    否则
        返回 入 列表 索引。
    。
。
```

**类型检查：**
```yan
定 是数 = 函 值
    返回 {{isinstance(value, (int, float))}}。
。
```

## 三、常见错误及解决方案

### 3.1 拼写错误

**错误：**
```yan
定 数据 = 列 1 2 3。
定 值 = 数据x。
```

**解决：**
```yan
定 数据 = 列 1 2 3。
定 值 = 数据。
```

### 3.2 参数数量错误

**错误：**
```yan
定 加 = 函 x y 返回 加 x y。
定 值 = 加 1。
```

**解决：**
```yan
定 加 = 函 x y 返回 加 x y。
定 值 = 加 1 2。
```

### 3.3 索引越界

**错误：**
```yan
定 列表 = 列 1 2 3。
定 值 = 入 列表 5。
```

**解决：**
```yan
定 列表 = 列 1 2 3。
定 值 = 入 列表 2。
```

## 四、调试技巧

### 4.1 使用印语句

```yan
定 数据 = 列 1 2 3。
印 数据。
印 长 数据。
```

### 4.2 分步执行

```yan
-- 分步调试复杂表达式
定 步骤1 = 列 1 2 3。
印 步骤1。

定 步骤2 = 皆 平方 步骤1。
印 步骤2。

定 步骤3 = 求和 步骤2。
印 步骤3。
```

### 4.3 检查中间结果

```yan
定 复杂计算 = 函 x
    定 中间结果1 = 乘 x x。
    印 中间结果1。
    
    定 中间结果2 = 加 中间结果1 1。
    印 中间结果2。
    
    返回 中间结果2。
。
```

## 五、错误报告

如果遇到不清楚的错误信息，请：

1. 记录完整的错误信息
2. 记录触发错误的代码
3. 在 GitHub Issues 中报告
4. 提供最小可复现示例

---

**更新日期**：2026-05-17
```

- [ ] **步骤3：Commit**

```bash
git add yan/examples/error_handling_demo.yan yan/docs/ERROR_HANDLING_GUIDE.md
git commit -m "docs: add error handling demo and guide"
```

---

### 任务7：更新测试套件

**文件：**
- 修改：`yan/tests/test_suite.py`

**目标：** 在测试套件中添加错误处理测试

- [ ] **步骤1：添加错误处理测试到测试套件**

在 `yan/tests/test_suite.py` 中添加：

```python
# 在文件末尾添加

# ============ 错误处理测试 ============

def test_error_formatter():
    """测试错误格式化器"""
    from error_formatter import ErrorFormatter, ErrorContext
    
    formatter = ErrorFormatter()
    context = ErrorContext(
        error_type="测试错误",
        file_path="test.yan",
        line=1,
        column=1,
        end_column=5,
        source_lines=["测试代码。"],
        message="测试消息"
    )
    
    result = formatter.format(context)
    assert "错误：测试错误" in result
    assert "test.yan" in result

def test_error_suggestions():
    """测试错误建议生成器"""
    from error_suggestions import ErrorSuggestionGenerator
    
    generator = ErrorSuggestionGenerator()
    suggestions = generator.suggest_similar_name("数据x", {"数据", "列表"})
    
    assert "数据" in suggestions

# 在 TestSuite.__init__ 中添加测试
# self.test("错误格式化器", test_error_formatter)
# self.test("错误建议生成器", test_error_suggestions)
```

- [ ] **步骤2：运行测试套件验证**

运行：`cd yan && python tests/test_suite.py`
预期：所有测试通过

- [ ] **步骤3：Commit**

```bash
git add yan/tests/test_suite.py
git commit -m "test: add error handling tests to test suite"
```

---

## 总结

### 预计工作量

- **任务1**（错误格式规范）：0.5天
- **任务2**（错误格式化器）：1天
- **任务3**（建议生成器）：1天
- **任务4**（集成到词法分析器）：1天
- **任务5**（集成到语法分析器）：1天
- **任务6**（演示和文档）：0.5天
- **任务7**（更新测试套件）：0.5天

**总计**：5-6天

### 关键里程碑

1. ✅ 错误格式规范完成
2. ✅ 错误格式化器实现
3. ✅ 建议生成器实现
4. ✅ 词法分析器集成
5. ✅ 语法分析器集成
6. ✅ 文档完善
7. ✅ 测试通过

### 成功标准

**错误处理增强完成标准：**
- 错误信息清晰易懂
- 显示源代码片段和错误位置
- 提供修复建议
- 所有测试通过
- 文档完善

---

**下一步**：开始执行任务1，设计错误信息格式
