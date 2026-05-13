# 言语言智能块推断设计

**版本：** 1.0  
**日期：** 2026-05-13  
**状态：** 已批准  
**作者：** DuMate

---

## 1. 概述

### 1.1 问题陈述

当前言语言的块结构需要显式的结束符（`。`），导致代码冗余，不符合中文写作习惯。

**当前语法：**
```yan
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。  -- 冗余的结束符
```

### 1.2 设计目标

- 减少冗余符号，提高代码简洁性
- 符合中文写作习惯（自然段结束）
- 保持语法清晰，避免歧义
- 兼容现有代码，渐进式改进

### 1.3 解决方案

采用**智能推断**机制：解析器根据语法上下文自动判断块结束，最后一个语句的句号自动结束块。

**改进后语法：**
```yan
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
-- 自动结束，无需显式结束符
```

---

## 2. 核心设计

### 2.1 块结束判断规则

| 条件 | 动作 | 示例 |
|------|------|------|
| 遇到 `。` 且下一个 token 是新定义 | 结束当前块 | `定x=1。定y=2。` |
| 遇到 `。` 且下一个 token 是同层级关键字 | 结束当前块 | `若...则...。若...` |
| 遇到 `。` 且到达文件结束 | 结束所有块 | `定x=1。` |
| 遇到 `。` 且下一个 token 缩进减少 | 结束当前块 | 通过缩进判断 |
| 遇到 `。` 且下一个 token 是嵌套块开始 | 继续当前块 | `定f=函x：定y=1。` |

### 2.2 块栈机制

解析器维护一个块栈，记录当前块的状态：

```python
class BlockStack:
    def __init__(self):
        self.stack = []  # [(block_type, indent_level)]
    
    def push(self, block_type, indent_level):
        self.stack.append((block_type, indent_level))
    
    def pop(self):
        return self.stack.pop()
    
    def current(self):
        return self.stack[-1] if self.stack else None
```

**块类型：**
- `FUNC`：函数块（`函...：`）
- `IF`：条件块（`若...则...`）
- `LOOP`：循环块（`遍历...：`、`当...：`）
- `TEST`：测试块（`测...：`）
- `SUITE`：测试套件块（`套...：`）

### 2.3 缩进处理

引入"软缩进"概念：不强制要求缩进，但利用缩进辅助判断。

**规则：**
1. 解析器记录每行的缩进级别
2. 遇到 `：` 时，记录当前缩进级别
3. 遇到 `。` 时，检查下一行的缩进：
   - 如果缩进减少，结束当前块
   - 如果缩进相同或增加，继续当前块

### 2.4 关键字识别

**块开始关键字：**
- `定`：变量/函数定义
- `函`：匿名函数
- `若`：条件语句
- `遍历`：遍历循环
- `当`：当循环
- `测`：测试定义
- `套`：测试套件

**块结束触发器：**
- `。`：句号（主要）
- `；`：分号（可选）

---

## 3. 语法规范

### 3.1 EBNF 更新

```ebnf
(* 块 *)
Block       ::= '：' Statement* (Statement | '。')?
            |   Statement  -- 单行块

(* 语句 *)
Statement   ::= Expression ('。' | '；')?
            |   Define
            |   '。' | '；'  (* 空语句 *)

(* 定义 *)
Define      ::= '定' Name '=' Expression
            |   '定' Name '=' '函' Params '：' Block  -- 多行函数
            |   '定' Name '=' '函' Params Expression   -- 单行函数

(* 条件表达式 *)
IfExpr      ::= '若' Expression '则' (Block | Expression) 
                ('否则' (Block | Expression))?

(* 遍历循环 *)
ForeachExpr ::= '遍历' Name '于' Expression '：' Block

(* 当循环 *)
WhileExpr   ::= '当' Expression '：' Block
```

**关键变化：**
- `Block` 可以是单行（单个 `Statement`）或多行（`：` 开始）
- 多行块的结束由解析器智能推断
- 不再强制要求显式的结束符

### 3.2 单行 vs 多行

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

---

## 4. 实现细节

### 4.1 解析器修改

**主要修改点：**

1. **添加块栈**：在 `Parser` 类中添加 `block_stack` 属性
2. **修改 `_parse_block()`**：实现智能推断逻辑
3. **添加 `_should_end_block()`**：判断是否应该结束块
4. **修改 `_parse_define()`**：区分单行和多行函数
5. **修改 `_parse_if()`**：支持块结束推断

### 4.2 核心算法

```python
def parse_block(self, block_type):
    """解析块，智能推断结束"""
    statements = []
    block_start_indent = self.current_indent()
    
    while not self.is_at_end():
        # 跳过句号
        if self.current().type == TokenType.DOT:
            self.advance()
            
            # 检查是否应该结束块
            if self.should_end_block(block_start_indent):
                break
            continue
        
        # 解析语句
        stmt = self.parse_statement()
        if stmt:
            statements.append(stmt)
    
    return Block(statements) if len(statements) > 1 else statements[0] if statements else Nil()

def should_end_block(self, block_start_indent):
    """判断是否应该结束块"""
    # 情况 1：文件结束
    if self.is_at_end():
        return True
    
    # 情况 2：遇到新的定义
    if self.check_word('定'):
        return True
    
    # 情况 3：遇到同层级关键字
    if self.current().type == TokenType.WORD:
        word = self.current().value
        if word in {'若', '遍历', '当', '测', '套'}:
            return True
    
    # 情况 4：缩进减少
    next_indent = self.peek_next_line_indent()
    if next_indent < block_start_indent:
        return True
    
    return False
```

### 4.3 缩进跟踪

**Lexer 修改：**

```python
class Lexer:
    def __init__(self):
        self.indent_stack = [0]  # 缩进栈
        self.current_indent = 0  # 当前缩进
    
    def tokenize(self, source):
        lines = source.split('\n')
        tokens = []
        
        for line in lines:
            # 计算缩进
            indent = len(line) - len(line.lstrip())
            self.current_indent = indent
            
            # 解析 token
            tokens.extend(self._tokenize_line(line))
        
        return tokens
```

**Parser 修改：**

```python
class Parser:
    def current_indent(self):
        """获取当前行的缩进级别"""
        return self._lexer.current_indent
    
    def peek_next_line_indent(self):
        """获取下一行的缩进级别"""
        # 保存当前位置
        saved_pos = self.pos
        
        # 跳到下一行
        while not self.is_at_end() and self.current().type != TokenType.NEWLINE:
            self.advance()
        
        if self.is_at_end():
            return 0
        
        self.advance()  # 跳过换行
        
        # 计算下一行缩进
        indent = 0
        while self.current().type == TokenType.SPACE:
            indent += 1
            self.advance()
        
        # 恢复位置
        self.pos = saved_pos
        return indent
```

---

## 5. 示例对比

### 5.1 函数定义

**改进前：**
```yan
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。

定统计=函语文 数学 英语：
  定总分=$(语文 + 数学 + 英语)。
  定均值=$(总分 / 3)。
  列总分 均值。
。
```

**改进后：**
```yan
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。

定统计=函语文 数学 英语：
  定总分=$(语文 + 数学 + 英语)。
  定均值=$(总分 / 3)。
  列总分 均值。
```

**效果：** 减少 2 个冗余的 `。`

### 5.2 条件语句

**改进前：**
```yan
若x大0则：
  印"正数"。
  印x。
。
```

**改进后：**
```yan
若x大0则：
  印"正数"。
  印x。
```

**效果：** 减少 1 个冗余的 `。`

### 5.3 测试套件

**改进前：**
```yan
套 "算术运算测试"：
  测 "加法运算"：
    断言等 加1 2 3。
  。
。
```

**改进后：**
```yan
套 "算术运算测试"：
  测 "加法运算"：
    断言等 加1 2 3。
```

**效果：** 减少 2 个冗余的 `。`

---

## 6. 边界情况

### 6.1 单行函数

```yan
-- 无需块结构
定阶乘=函n 若n等1则1否则n乘阶乘n减1。
```

**解析：** `函n` 后面没有 `：`，所以是单行函数。

### 6.2 嵌套块

```yan
定阶乘=函n：
  若n等1则：
    1。
  否则：
    n乘阶乘n减1。
```

**解析：**
- `函n：` 开始函数块
- `若n等1则：` 开始 if-then 块
- `1。` 结束 then 块
- `否则：` 开始 else 块
- `n乘阶乘n减1。` 结束 else 块
- 函数块结束（通过缩进判断）

### 6.3 连续定义

```yan
定x=1。
定y=2。
定z=函a b：
  加a b。
```

**解析：**
- `定x=1。` 后遇到 `定`，结束当前定义
- `定y=2。` 后遇到 `定`，结束当前定义
- `加a b。` 后到达文件结束，结束函数块

### 6.4 空块

```yan
定空函数=函x：
  。
```

**解析：** 空块，只有 `。`，立即结束。

---

## 7. 兼容性

### 7.1 向后兼容

**原则：** 现有代码无需修改即可运行。

**实现：**
- 解析器同时支持旧的显式结束符和新的智能推断
- 如果检测到显式的结束符，使用旧逻辑
- 如果没有显式的结束符，使用新的智能推断

**示例：**
```yan
-- 旧代码（仍然有效）
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。

-- 新代码（推荐）
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
```

### 7.2 迁移策略

**阶段 1：** 解析器支持两种语法
**阶段 2：** 文档推荐新语法
**阶段 3：** 工具自动转换旧代码
**阶段 4：** 逐步淘汰旧语法（可选）

---

## 8. 测试计划

### 8.1 单元测试

| 测试用例 | 输入 | 期望输出 |
|----------|------|----------|
| 单行函数 | `定f=函x x。` | 正确解析 |
| 多行函数 | `定f=函x：x。` | 正确解析 |
| 嵌套块 | `定f=函x：若x则：1。` | 正确解析 |
| 连续定义 | `定x=1。定y=2。` | 正确解析 |
| 空块 | `定f=函x：。` | 正确解析 |

### 8.2 集成测试

| 测试用例 | 文件 | 期望结果 |
|----------|------|----------|
| 阶乘函数 | `factorial.yan` | 正确执行 |
| 汉诺塔 | `hanoi.yan` | 正确执行 |
| 测试套件 | `basic_tests.yan` | 全部通过 |

### 8.3 回归测试

运行所有现有示例程序，确保行为不变。

---

## 9. 风险与缓解

### 9.1 潜在风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 解析器复杂度增加 | 高 | 中 | 充分测试，代码审查 |
| 边界情况处理不当 | 中 | 高 | 详细的测试用例 |
| 用户混淆新旧语法 | 低 | 低 | 清晰的文档和示例 |
| 性能下降 | 低 | 低 | 性能基准测试 |

### 9.2 回退方案

如果智能推断出现问题，可以：
1. 禁用智能推断，回退到显式结束符
2. 提供配置选项，让用户选择语法风格

---

## 10. 未来扩展

### 10.1 数据流网

为未来的数据流网特性预留空间：
- 块栈机制可以扩展为节点栈
- 缩进处理可以扩展为连接关系
- 智能推断可以扩展为自动布局

### 10.2 可视化编辑器

块栈和缩进信息可以用于：
- 代码折叠
- 语法高亮
- 自动缩进
- 结构化编辑

---

## 11. 参考资料

- [Python 缩进规则](https://docs.python.org/3/reference/lexical_analysis.html#indentation)
- [Haskell 布局规则](https://www.haskell.org/onlinereport/haskell2010/haskellch10.html)
- [YAML 规范](https://yaml.org/spec/)

---

## 12. 附录

### A. 完整示例

#### A.1 阶乘函数

```yan
-- 递归版本
定阶乘=函n：
  若n等1则：
    1。
  否则：
    n乘阶乘n减1。

-- 迭代版本
定阶乘迭代=函n：
  定结果=1。
  定计数=1。
  当计数小等于n：
    定结果=乘结果计数。
    定计数=加计数 1。
  结果。

印阶乘5。
印阶乘迭代5。
```

#### A.2 快速排序

```yan
定快排=函列表：
  若空列表则：
    列。
  否则：
    定基准=首列表。
    定其余=余列表。
    定小=只函x 小x基准 其余。
    定大=只函x 大x基准 其余。
    连快排小 列基准 快排大。

印快排列3 1 4 1 5 9 2 6。
```

#### A.3 测试套件

```yan
套 "算术运算测试"：
  测 "加法运算"：
    断言等 加1 2 3。

  测 "减法运算"：
    断言等 减5 3 2。

  测 "乘法运算"：
    断言等 乘3 4 12。

  测 "除法运算"：
    断言等 除10 2 5。

套 "高阶函数测试"：
  测 "映射函数"：
    定数据=列1 2 3。
    定平方=函x 乘x x。
    断言等 皆平方数据 列1 4 9。

  测 "过滤函数"：
    定数据=列1 2 3 4 5。
    定是偶数=函x 等模x 2 0。
    断言等 只是偶数数据 列2 4。

  测 "归约函数"：
    定数据=列1 2 3 4 5。
    断言等 归加0数据 15。
```

### B. 实现检查清单

- [ ] 添加 `BlockStack` 类
- [ ] 修改 `Parser` 类，添加 `block_stack` 属性
- [ ] 实现 `_should_end_block()` 方法
- [ ] 修改 `_parse_block()` 方法
- [ ] 修改 `_parse_define()` 方法
- [ ] 修改 `_parse_if()` 方法
- [ ] 修改 `_parse_foreach()` 方法
- [ ] 修改 `_parse_while()` 方法
- [ ] 修改 `_parse_test()` 方法
- [ ] 修改 `_parse_test_suite()` 方法
- [ ] 添加缩进跟踪（Lexer）
- [ ] 编写单元测试
- [ ] 编写集成测试
- [ ] 更新文档
- [ ] 更新示例代码
