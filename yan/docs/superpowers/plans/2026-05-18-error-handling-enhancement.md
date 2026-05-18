# 言语言错误处理增强计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 提供开发者友好的错误信息，显著提升调试体验

**架构：** 在现有错误处理基础上，增强错误诊断、建议和可视化能力

**技术栈：** Python 3.8+、言语言编译器、错误格式化器

---

## 当前状态

**已完成：**
- ✅ 基础错误处理（error.py）
- ✅ 错误格式化器（error_formatter.py）
- ✅ 错误建议生成器（error_suggestions.py）
- ✅ 源代码片段显示
- ✅ 错误位置高亮

**当前成熟度：** 60%

**目标成熟度：** 80%+

---

## 问题分析

### 1. 错误信息不够友好

**现状：**
```
SyntaxError: Unexpected token at line 10, column 5
```

**期望：**
```
错误：缺少右括号
位置：第10行，第5列
代码：  定 结果 = 加 1 2
              ^
建议：检查括号是否匹配，可能需要在表达式末尾添加右括号
```

### 2. 错误建议不够智能

**现状：**
- 简单的错误提示
- 缺少上下文信息
- 没有修复建议

**期望：**
- 智能错误诊断
- 上下文相关建议
- 自动修复提示

### 3. 错误追踪困难

**现状：**
- 只有错误位置
- 没有调用栈
- 难以定位问题根源

**期望：**
- 完整的调用栈
- 错误链追踪
- 源码映射支持

---

## 改进方案

### 方案1：增强错误信息（P0，1周）

**目标：** 提供清晰、友好的错误信息

**任务：**

#### 任务1.1：错误分类系统

- [ ] 定义错误类型枚举
- [ ] 实现错误严重级别
- [ ] 添加错误代码系统
- [ ] 创建错误消息模板

**文件：** `yan/error_types.py`

**示例：**
```python
class ErrorType(Enum):
    SYNTAX_ERROR = "E001"
    TYPE_ERROR = "E002"
    NAME_ERROR = "E003"
    RUNTIME_ERROR = "E004"
    
class ErrorSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
```

#### 任务1.2：上下文感知错误

- [ ] 提取错误上下文
- [ ] 显示相关代码片段
- [ ] 高亮错误位置
- [ ] 显示变量状态

**文件：** `yan/error_context.py`

**示例：**
```python
def extract_context(source, line, column, context_lines=3):
    """提取错误上下文"""
    lines = source.split('\n')
    start = max(0, line - context_lines)
    end = min(len(lines), line + context_lines + 1)
    
    context = {
        'lines': lines[start:end],
        'error_line': line,
        'error_column': column,
        'variables': get_local_variables()
    }
    return context
```

#### 任务1.3：错误消息模板

- [ ] 创建错误消息模板库
- [ ] 支持参数化消息
- [ ] 多语言支持（中文优先）
- [ ] 错误消息格式化

**文件：** `yan/error_messages.yaml`

**示例：**
```yaml
E001:
  template: "语法错误：{message}"
  suggestion: "请检查第{line}行的语法"
  examples:
    - "缺少右括号"
    - "多余的分隔符"
    
E002:
  template: "类型错误：期望{expected}，实际得到{actual}"
  suggestion: "请检查变量类型是否正确"
```

### 方案2：智能错误建议（P0，1周）

**目标：** 提供智能的修复建议

**任务：**

#### 任务2.1：常见错误模式识别

- [ ] 收集常见错误模式
- [ ] 实现模式匹配
- [ ] 生成修复建议
- [ ] 提供示例代码

**文件：** `yan/error_patterns.py`

**示例：**
```python
ERROR_PATTERNS = {
    'missing_bracket': {
        'pattern': r'缺少.*括号',
        'suggestion': '检查括号是否匹配',
        'auto_fix': lambda code: fix_brackets(code)
    },
    'undefined_variable': {
        'pattern': r'未定义的变量',
        'suggestion': '检查变量名是否正确拼写',
        'similar_names': lambda name: find_similar(name)
    }
}
```

#### 任务2.2：智能建议引擎

- [ ] 实现建议评分系统
- [ ] 基于上下文生成建议
- [ ] 提供多个修复选项
- [ ] 学习用户习惯

**文件：** `yan/error_suggestions_v2.py`

**示例：**
```python
def generate_suggestions(error, context):
    """生成智能建议"""
    suggestions = []
    
    # 基于错误类型
    type_suggestions = get_type_suggestions(error.type)
    
    # 基于上下文
    context_suggestions = get_context_suggestions(context)
    
    # 基于历史
    history_suggestions = get_history_suggestions(error)
    
    # 评分排序
    all_suggestions = merge_and_score(
        type_suggestions,
        context_suggestions,
        history_suggestions
    )
    
    return all_suggestions[:5]  # 返回前5个建议
```

#### 任务2.3：自动修复提示

- [ ] 实现简单错误自动修复
- [ ] 生成修复代码片段
- [ ] 提供修复预览
- [ ] 一键应用修复

**文件：** `yan/error_auto_fix.py`

**示例：**
```python
def auto_fix(error, source):
    """自动修复简单错误"""
    fixes = []
    
    # 缺少括号
    if error.type == 'missing_bracket':
        fixed = add_missing_bracket(source, error.position)
        fixes.append({
            'description': '添加缺少的括号',
            'code': fixed,
            'confidence': 0.9
        })
    
    # 拼写错误
    if error.type == 'undefined_variable':
        similar = find_similar_variable(error.name)
        if similar:
            fixed = replace_variable(source, error.name, similar)
            fixes.append({
                'description': f'将 {error.name} 替换为 {similar}',
                'code': fixed,
                'confidence': 0.7
            })
    
    return fixes
```

### 方案3：错误追踪增强（P1，1周）

**目标：** 提供完整的错误追踪能力

**任务：**

#### 任务3.1：调用栈追踪

- [ ] 实现调用栈记录
- [ ] 显示函数调用链
- [ ] 过滤系统调用
- [ ] 格式化调用栈

**文件：** `yan/error_stack.py`

**示例：**
```python
class CallStack:
    def __init__(self):
        self.frames = []
    
    def push(self, function, line, column):
        self.frames.append({
            'function': function,
            'line': line,
            'column': column,
            'locals': get_locals()
        })
    
    def pop(self):
        return self.frames.pop()
    
    def format(self):
        """格式化调用栈"""
        result = "调用栈：\n"
        for i, frame in enumerate(reversed(self.frames)):
            result += f"  #{i} {frame['function']} at line {frame['line']}\n"
        return result
```

#### 任务3.2：错误链追踪

- [ ] 记录错误传播路径
- [ ] 显示错误因果关系
- [ ] 提供错误历史
- [ ] 支持错误重放

**文件：** `yan/error_chain.py`

**示例：**
```python
class ErrorChain:
    def __init__(self):
        self.errors = []
    
    def add_error(self, error, cause=None):
        self.errors.append({
            'error': error,
            'cause': cause,
            'timestamp': time.time()
        })
    
    def format(self):
        """格式化错误链"""
        result = "错误链：\n"
        for i, entry in enumerate(self.errors):
            result += f"  {i+1}. {entry['error']}\n"
            if entry['cause']:
                result += f"     由 {entry['cause']} 引起\n"
        return result
```

#### 任务3.3：源码映射

- [ ] 实现源码映射
- [ ] 支持生成代码到源码映射
- [ ] 提供源码位置查询
- [ ] 支持多文件映射

**文件：** `yan/source_map.py`

**示例：**
```python
class SourceMap:
    def __init__(self):
        self.mappings = {}
    
    def add_mapping(self, generated_line, source_line, source_file):
        self.mappings[generated_line] = {
            'source_line': source_line,
            'source_file': source_file
        }
    
    def lookup(self, generated_line):
        """查找源码位置"""
        return self.mappings.get(generated_line)
```

---

## 实施计划

### 第1周：错误信息增强

**Day 1-2：** 错误分类系统
- 定义错误类型
- 实现错误级别
- 创建错误代码

**Day 3-4：** 上下文感知错误
- 提取错误上下文
- 显示代码片段
- 高亮错误位置

**Day 5：** 错误消息模板
- 创建模板库
- 实现参数化
- 测试验证

### 第2周：智能建议

**Day 1-2：** 错误模式识别
- 收集错误模式
- 实现模式匹配
- 生成建议

**Day 3-4：** 智能建议引擎
- 实现建议评分
- 上下文建议
- 多选项建议

**Day 5：** 自动修复提示
- 简单错误修复
- 代码片段生成
- 测试验证

### 第3周：错误追踪

**Day 1-2：** 调用栈追踪
- 实现调用栈记录
- 格式化显示
- 测试验证

**Day 3-4：** 错误链追踪
- 记录错误传播
- 显示因果关系
- 测试验证

**Day 5：** 源码映射
- 实现源码映射
- 集成测试
- 文档更新

---

## 验收标准

### 功能验收

- [ ] 所有错误都有清晰的分类和代码
- [ ] 错误信息包含上下文和位置
- [ ] 每个错误至少提供3个修复建议
- [ ] 支持调用栈追踪
- [ ] 支持错误链追踪
- [ ] 支持源码映射

### 性能验收

- [ ] 错误处理时间 < 10ms
- [ ] 建议生成时间 < 50ms
- [ ] 内存占用 < 5MB

### 质量验收

- [ ] 测试覆盖率 > 80%
- [ ] 所有测试通过
- [ ] 无性能回归
- [ ] 文档完整

---

## 成功指标

**短期（1个月）：**
- 错误处理成熟度：60% → 80%
- 用户满意度提升：+30%
- 调试时间减少：-40%

**中期（3个月）：**
- 错误处理成熟度：80% → 90%
- 用户满意度提升：+50%
- 调试时间减少：-60%

---

## 风险与缓解

### 风险1：性能影响

**风险：** 错误处理增强可能影响编译速度

**缓解：**
- 使用缓存机制
- 延迟加载建议
- 异步生成建议

### 风险2：建议准确性

**风险：** 自动建议可能不准确

**缓解：**
- 使用评分系统
- 提供多个选项
- 收集用户反馈

### 风险3：兼容性

**风险：** 可能破坏现有代码

**缓解：**
- 保持向后兼容
- 渐进式迁移
- 完整测试覆盖

---

## 后续工作

1. **错误报告系统**（1周）
   - 自动收集错误统计
   - 生成错误报告
   - 提供改进建议

2. **调试器集成**（2周）
   - VS Code调试适配器
   - 断点支持
   - 变量查看

3. **在线帮助**（1周）
   - 错误代码查询
   - 在线文档链接
   - 示例代码库

---

**最后更新：** 2026-05-18  
**预计完成：** 2026-06-08  
**负责人：** AI代理
