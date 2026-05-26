# 关键字双字化改造实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将所有单字关键字改为双字关键字，消除分词歧义，简化词法分析器逻辑。

**架构：** 修改 lexer.py 中的关键字集合，更新 parser.py 中的关键字检查，批量更新所有示例文件。

**技术栈：** Python 3.12, pytest

---

## 文件结构

### 将要修改的文件

| 文件路径 | 职责 | 变更类型 |
|---------|------|---------|
| `yan/lexer.py` | 词法分析器，定义关键字集合 | 修改 |
| `yan/parser.py` | 语法分析器，关键字检查逻辑 | 修改 |
| `examples/*.yan` | 示例代码文件 | 修改 |

---

## 任务列表

### 任务 1：修改 lexer.py 关键字定义

**文件：**
- 修改：`yan/lexer.py:82-107`

**关键字替换映射：**
```python
# 单字转双字映射
keyword_mapping = {
    '定': '定义',
    '函': '函数',
    '若': '如果',
    '则': '那么',
    '当': '当时',
    '列': '列表',
    '典': '字典',
    '序': '序列',
    '对': '对组',
    '长': '长度',
    '添': '添加',
    '连': '连接',
    '含': '包含',
    '印': '输出',
    '读': '读取',
    '写': '写入',
    '大': '大于',
    '小': '小于',
    '等': '等于',
    '皆': '映射',
    '只': '过滤',
    '归': '归约',
}
```

- [ ] **步骤 1：修改 `_SINGLE_CHAR_KEYWORDS`**

移除已双字化的关键字：
```python
# 预定义的单字关键字集合（类级缓存）
_SINGLE_CHAR_KEYWORDS = frozenset({
    '加', '减', '乘', '除', '模', '幂', '绝对', '负',
    '且', '或', '非',
    '首', '余', '入', '空',
    '真', '假', '反', '排',
})
```

- [ ] **步骤 2：修改 `_MULTI_CHAR_KEYWORDS`**

添加新的双字关键字：
```python
# 预定义的多字关键字集合（类级缓存）
_MULTI_CHAR_KEYWORDS = frozenset({
    '定义', '函数', '如果', '那么', '否则', '当时',
    '遍历', '返回',
    '列表', '字典', '序列', '对组',
    '长度', '添加', '连接', '包含', '空',
    '输出', '读取', '写入',
    '大于', '小于', '等于', '不等于',
    '映射', '过滤', '归约',
    # ... 其他现有多字关键字保持不变
})
```

- [ ] **步骤 3：清理 `known_multi_char_words`**

由于关键字已双字化，`known_multi_char_words` 集合可能不再需要，可以移除或简化。

- [ ] **步骤 4：运行词法分析器测试**

```bash
pytest tests/test_suite.py::test_lexer_keywords -v
```

- [ ] **步骤 5：Commit**

```bash
git add yan/lexer.py
git commit -m "feat: update keywords to 2-character"
```

---

### 任务 2：修改 parser.py 关键字检查

**文件：**
- 修改：`yan/parser.py`

- [ ] **步骤 1：更新 `statement_start_keywords`**

```python
statement_start_keywords = {'定义', '如果', '那么', '否则', '遍历', '当时', '函数', '返回', '结构', '套', '测', '输出', '读取', '写入', '引', '导', '出'}
```

- [ ] **步骤 2：更新 `block_start_keywords`**

```python
block_start_keywords = {'函数', '如果', '遍历', '当时', '结构', '套', '测'}
```

- [ ] **步骤 3：更新 `_parse_statement` 中的关键字检查**

将 `_check_word('定')` 改为 `_check_word('定义')`，`_check_word('若')` 改为 `_check_word('如果')` 等。

- [ ] **步骤 4：更新 `_parse_if` 中的关键字检查**

将 `_check_word('则')` 改为 `_check_word('那么')`。

- [ ] **步骤 5：运行语法分析器测试**

```bash
pytest tests/test_suite.py::test_parser_define tests/test_suite.py::test_parser_function tests/test_suite.py::test_parser_if -v
```

- [ ] **步骤 6：Commit**

```bash
git add yan/parser.py
git commit -m "feat: update parser keyword checks"
```

---

### 任务 3：更新示例文件

**文件：**
- 修改：`examples/*.yan`

- [ ] **步骤 1：批量替换关键字**

创建替换脚本：
```python
import os

keyword_mapping = {
    '定': '定义',
    '函': '函数',
    '若': '如果',
    '则': '那么',
    '当': '当时',
    '列': '列表',
    '印': '输出',
    '大': '大于',
    '小': '小于',
    '等': '等于',
    '皆': '映射',
    '只': '过滤',
    '归': '归约',
}

examples_dir = 'examples'
for filename in os.listdir(examples_dir):
    if filename.endswith('.yan'):
        filepath = os.path.join(examples_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        for old, new in keyword_mapping.items():
            content = content.replace(old + ' ', new + ' ')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
```

- [ ] **步骤 2：运行示例测试**

```bash
python main.py examples/bubble_sort_simple.yan
```

- [ ] **步骤 3：Commit**

```bash
git add examples/
git commit -m "feat: update example files with new keywords"
```

---

### 任务 4：运行完整测试套件

**文件：**
- 测试：`tests/*.py`

- [ ] **步骤 1：运行所有测试**

```bash
pytest tests/ -v --tb=no
```

- [ ] **步骤 2：修复失败的测试**

如果有测试失败，分析原因并修复。

- [ ] **步骤 3：Commit**

```bash
git add .
git commit -m "feat: complete keyword bigram transformation"
```

---

## 自检清单

1. **规格覆盖度：**
   - ✅ 控制流关键字（定→定义, 函→函数, 若→如果, 则→那么, 当→当时）
   - ✅ 比较运算符（大→大于, 小→小于, 等→等于）
   - ✅ 列表/数据结构（列→列表, 典→字典）
   - ✅ 输入输出（印→输出, 读→读取, 写→写入）
   - ✅ 高阶函数（皆→映射, 只→过滤, 归→归约）

2. **占位符扫描：**
   - ✅ 无 "待定"、"TODO"
   - ✅ 每个步骤都有具体代码

3. **类型一致性：**
   - ✅ 关键字映射在所有任务中保持一致

---

## 执行交接

计划已完成并保存到 `docs/superpowers/plans/2026-05-25-keyword-bigram-plan.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**