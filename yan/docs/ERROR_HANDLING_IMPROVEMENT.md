# 言语言错误处理改进

## 概述

本次更新显著改进了言语言的错误处理系统，提供更清晰、更友好、更可操作的错误信息。

## 新增文件

### 1. `error_formatter.py`
错误格式化器，负责生成格式化的错误信息。

**主要功能：**
- 格式化错误标题和位置信息
- 生成源代码片段（带行号）
- 标记错误位置（使用 `^` 符号）
- 支持彩色输出（ANSI 颜色代码）

**使用示例：**
```python
from error_formatter import ErrorFormatter, ErrorContext

formatter = ErrorFormatter()
context = ErrorContext(
    error_type="未定义的变量",
    file_path="demo.yan",
    line=3,
    column=15,
    end_column=18,
    source_lines=["定 数据 = 列 1 2 3。", "定 值 = 数据x。"],
    message="未定义的变量：数据x",
    suggestion="检查变量名拼写。"
)
print(formatter.format(context))
```

### 2. `error_suggestions.py`
错误建议生成器，自动生成修复建议。

**主要功能：**
- 基于编辑距离的相似名称建议
- 参数数量错误建议
- 类型错误建议
- 索引越界建议

**使用示例：**
```python
from error_suggestions import ErrorSuggestionGenerator

suggester = ErrorSuggestionGenerator()

# 相似名称建议
suggestions = suggester.suggest_similar_name("数据x", {"数据", "列表"})
# 返回: ["数据"]

# 参数数量建议
suggestion = suggester.suggest_arity_fix("加", 2, 1)
# 返回: "函数 加 需要 2 个参数，缺少 1 个参数。"
```

### 3. `docs/ERROR_FORMAT_SPEC.md`
错误格式规范文档，定义了错误信息的结构和样式。

## 错误信息格式

### 基本结构
```
错误：{错误类型}
  文件：{文件路径}
  位置：第 {行号} 行，第 {列号} 列

{源代码片段}
{错误位置标记}
{错误描述}

建议：{修复建议}
```

### 示例输出
```
错误：未定义的变量
  文件：examples/demo.yan
  位置：第 3 行，第 15-18 列

  第 2 行 | 定 平方 = 函 x 乘 x x。
  第 3 行 | 定 值 = 皆 平方 数据x。
                   ^^^
       未定义的变量：数据x
您是否想使用：数据？

建议：检查变量名拼写，或确认变量已定义。
```

## 集成变更

### `error.py`
- 集成了 `ErrorFormatter` 和 `ErrorSuggestionGenerator`
- `YanError` 类现在使用新的格式化器生成错误信息

### `parser.py`
- `ParserError` 类现在支持源代码上下文和建议
- `_create_error` 方法接受可选的建议参数

## 测试覆盖

新增测试文件：
- `tests/test_error_formatter.py` - 错误格式化器测试
- `tests/test_error_suggestions.py` - 错误建议生成器测试
- `tests/test_lexer_errors.py` - 词法分析器错误测试
- `tests/test_parser_errors.py` - 语法分析器错误测试

## 演示

运行演示：
```bash
python examples/error_demo.py
```

演示包含以下场景：
1. 未定义变量错误
2. 参数数量错误
3. 索引越界错误
4. 类型错误
5. 语法错误

## 未来改进

1. **更多错误类型**：添加更多特定错误类型的建议
2. **多语言支持**：支持英文错误信息
3. **IDE 集成**：生成 LSP 兼容的错误格式
4. **错误恢复**：在解析错误后尝试恢复并继续解析
