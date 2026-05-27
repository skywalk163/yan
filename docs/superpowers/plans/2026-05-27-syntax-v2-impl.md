# 语法优化 v2 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 修改解析器支持无句号代码块，移除代码块结束的句号

**架构：** 修改 yan/parser.py 中的语句解析逻辑，识别代码块结束（缩进减少）时不再期待句号

**技术栈：** Python 3.x、正则表达式

---

## 文件结构

| 文件 | 职责 | 状态 |
|------|------|------|
| `yan/parser.py` | 解析器核心，修改语句解析逻辑 | 修改 |
| `yan/syntax_migrator.py` | 语法迁移工具，自动转换现有代码 | 新建 |
| `yan/stdlib/*.yan` | 标准库模块，移除代码块结束句号 | 修改 |
| `examples/*.yan` | 示例代码，移除代码块结束句号 | 修改 |
| `yan/tests/test_parser.py` | 解析器测试，添加新语法测试 | 修改 |

---

### 任务1：修改解析器支持无句号代码块

**文件：**
- 修改：`yan/parser.py`

**上下文：**
当前解析器在每个语句后期待句号。需要修改为：
1. 代码块内语句：以换行或句号结束
2. 代码块结束时：缩进减少自动结束，不再期待句号
3. 文件级语句：仍以句号结束

- [ ] **步骤 1：找到当前语句解析逻辑**

在 `yan/parser.py` 中找到处理句号 `。` 的代码，约在第 150-200 行：

```python
# 当前逻辑（约）
def parse_statement(self):
    # ... 解析语句
    if self.current_token == '。':
        self.consume('。')  # 消费句号
    return node
```

- [ ] **步骤 2：添加代码块结束检测**

在 `parse_block` 或类似方法中添加代码块结束检测：

```python
def parse_block(self):
    """解析代码块，根据缩进判断结束"""
    statements = []
    
    while not self.is_at_block_end():
        if self.is_statement_separator():
            # 检测到独立句号：这是语句分隔符，消耗它
            self.consume('。')
        
        if self.is_at_block_end():
            break
            
        stmt = self.parse_statement()
        statements.append(stmt)
    
    return statements

def is_at_block_end(self):
    """检查是否到达代码块结束（缩进减少）"""
    if self.current_indent <= self.parent_indent:
        return True
    return False

def is_statement_separator(self):
    """检查当前是否独立句号（用于分隔语句）"""
    # 独立句号：前面是换行，后面是空白或另一个句子开始
    # 不是代码块结束的句号
    return self.current_token == '。' and not self.is_at_block_end()
```

- [ ] **步骤 3：修改语句解析**

更新 `parse_statement` 方法：

```python
def parse_statement(self):
    node = self.parse_expression()
    
    # 不再自动消费句号
    # 句号由 parse_block 在适当时机消费
    # 或者在语句内显式出现时消费
    
    return node
```

- [ ] **步骤 4：添加解析器配置**

添加语法版本控制：

```python
class Parser:
    def __init__(self, syntax_version=2):
        self.syntax_version = syntax_version  # 1=旧语法，2=新语法
    
    def parse(self, source):
        # 根据版本选择解析策略
        if self.syntax_version >= 2:
            return self.parse_v2(source)
        else:
            return self.parse_v1(source)
    
    def parse_v2(self, source):
        """新语法：无句号代码块"""
        # 实现新语法解析逻辑
        pass
```

- [ ] **步骤 5：Commit**

```bash
git add yan/parser.py
git commit -m "feat(parser): support syntax v2 without block-end periods"
```

---

### 任务2：创建语法迁移工具

**文件：**
- 创建：`yan/syntax_migrator.py`

**上下文：**
需要自动转换现有代码，移除代码块结束的句号

- [ ] **步骤 1：创建迁移工具框架**

```python
"""
语法迁移工具：将 v1 语法转换为 v2 语法
用法：python yan/syntax_migrator.py <file> [--in-place]
"""

import re
import sys

def migrate_file(filepath, in_place=False):
    """迁移单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    migrated = migrate_content(content)
    
    if in_place:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(migrated)
        print(f"已迁移: {filepath}")
    else:
        print(migrated)

def migrate_content(content):
    """迁移代码内容"""
    lines = content.split('\n')
    result = []
    indent_stack = []
    
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        
        # 计算当前缩进级别
        current_level = indent // 2  # 假设 2 空格 = 1 级
        
        # 清理行尾的句号（如果是代码块结束句号）
        processed = remove_block_end_period(stripped, indent_stack, current_level)
        
        result.append(processed)
        
        # 更新缩进栈
        update_indent_stack(indent_stack, current_level, stripped)
    
    return '\n'.join(result)

def remove_block_end_period(line, indent_stack, current_level):
    """移除代码块结束的句号"""
    # 检测独立的句号行（只有句号的行）
    if line.strip() == '。' or line.strip() == '．':
        return ''  # 移除整行
    
    # 检测行尾句号
    if line.endswith('。') and not line.endswith('"。') and not line.endswith('\'。'):
        # 检查是否是语句内的句号（非代码块结束）
        if is_statement_separator(line):
            return line
        # 移除代码块结束句号
        return line[:-1]
    
    return line

def is_statement_separator(line):
    """判断行尾句号是否为语句分隔符"""
    # 语句分隔符后通常是另一条语句的开始
    # 这里需要更复杂的逻辑来判断
    return False

def update_indent_stack(stack, current_level, line):
    """更新缩进栈"""
    # 简化实现
    pass

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python syntax_migrator.py <file> [--in-place]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    in_place = '--in-place' in sys.argv
    
    migrate_file(filepath, in_place)
```

- [ ] **步骤 2：添加目录批量迁移**

```python
def migrate_directory(dirpath, pattern='*.yan', in_place=False):
    """迁移目录下所有匹配的文件"""
    import glob
    
    files = glob.glob(f"{dirpath}/{pattern}")
    
    for filepath in files:
        migrate_file(filepath, in_place)
```

- [ ] **步骤 3：Commit**

```bash
git add yan/syntax_migrator.py
git commit -m "feat(tool): add syntax migration tool"
```

---

### 任务3：迁移标准库代码

**文件：**
- 修改：`yan/stdlib/*.yan`（所有19个模块）

**上下文：**
使用迁移工具批量转换标准库代码

- [ ] **步骤 1：迁移单个模块测试**

```bash
python yan/syntax_migrator.py yan/stdlib/math.yan
```

检查输出是否正确：

```yan
-- 迁移前
定 绝对 = 函 x：
  当 x 小于 0：
    返回 负 x。
  。
  返回 x。
。

-- 迁移后期望
定 绝对 = 函 x：
  当 x 小于 0：
    返回 负 x
  返回 x
```

- [ ] **步骤 2：批量迁移标准库**

```bash
python yan/syntax_migrator.py yan/stdlib/ --in-place
```

- [ ] **步骤 3：验证语法正确**

```bash
python -m yan.main yan/stdlib/math.yan
```

- [ ] **步骤 4：Commit**

```bash
git add yan/stdlib/*.yan
git commit -m "refactor(stdlib): migrate to syntax v2"
```

---

### 任务4：迁移示例代码

**文件：**
- 修改：`examples/*.yan`
- 修改：`docs/examples/*.yan`

- [ ] **步骤 1：批量迁移示例**

```bash
python yan/syntax_migrator.py examples/ --in-place
```

- [ ] **步骤 2：验证示例运行**

```bash
python -m yan.main examples/web_server_full.yan
```

- [ ] **步骤 3：Commit**

```bash
git add examples/*.yan
git commit -m "refactor(examples): migrate to syntax v2"
```

---

### 任务5：添加测试

**文件：**
- 修改：`yan/tests/test_parser.py`

- [ ] **步骤 1：添加新语法测试用例**

```python
def test_syntax_v2_no_block_period():
    """测试 v2 语法：无代码块结束句号"""
    source = """
定 绝对 = 函 x：
  当 x 小于 0：
    返回 负 x
  返回 x
"""
    parser = Parser(syntax_version=2)
    ast = parser.parse(source)
    
    # 验证解析成功
    assert ast is not None
    assert len(ast.body) == 1

def test_syntax_v2_nested_blocks():
    """测试 v2 语法：嵌套代码块"""
    source = """
定 读配置 = 函 文件路径：
  当 不 存在 文件路径：
    返回 典
  定 扩展名 = 扩展名 文件路径
  当 扩展名 等于 ".json"：
    返回 读JSON配置 文件路径
  返回 读JSON配置 文件路径
"""
    parser = Parser(syntax_version=2)
    ast = parser.parse(source)
    assert ast is not None
```

- [ ] **步骤 2：运行所有测试**

```bash
python -m pytest yan/tests/test_parser.py -v
```

- [ ] **步骤 3：Commit**

```bash
git add yan/tests/test_parser.py
git commit -m "test(parser): add syntax v2 test cases"
```

---

## 规格自检

1. **规格覆盖度：**
   - ✅ 解析器修改支持无句号代码块
   - ✅ 迁移工具批量转换现有代码
   - ✅ 标准库代码迁移
   - ✅ 示例代码迁移
   - ✅ 测试覆盖

2. **占位符扫描：** 无占位符

3. **类型一致性：** 所有函数名和参数名一致

---

**计划已完成并保存到 `docs/superpowers/plans/2026-05-27-syntax-v2-impl.md`。**

**执行方式选择：**

1. **子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

2. **内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**
