# 性能优化方案

## 当前性能分析

### 编译流程
1. 词法分析（Lexer）：O(n) 线性扫描
2. 语法分析（Parser）：O(n) 递归下降
3. 代码生成（CodeGen）：O(n) 树遍历

### 性能瓶颈识别

#### 1. 词法分析器
- **问题**：多字贪心匹配可能导致重复扫描
- **影响**：大型文件（>1000行）词法分析变慢
- **优化**：缓存已识别的关键字

#### 2. 语法分析器
- **问题**：两遍解析（收集用户函数 + 正常解析）
- **影响**：解析时间翻倍
- **优化**：合并两遍为一遍，使用符号表

#### 3. 代码生成器
- **问题**：频繁的字符串拼接
- **影响**：大型AST生成变慢
- **优化**：使用StringIO或列表join

## 优化方案

### 优先级1：代码生成器优化（快速见效）
```python
# 改进前
def _gen_program(self, node):
    lines = []
    for stmt in node.statements:
        code = self.generate(stmt)
        if code:
            lines.append(code)
    return '\n'.join(lines)

# 改进后
from io import StringIO

def _gen_program(self, node):
    output = StringIO()
    for stmt in node.statements:
        code = self.generate(stmt)
        if code:
            output.write(code)
            output.write('\n')
    return output.getvalue()
```

**预期效果**：大型文件生成速度提升 20-30%

### 优先级2：词法分析器缓存
```python
class Lexer:
    def __init__(self):
        self._keyword_cache = {}  # 缓存已识别的关键字
        
    def _match_keyword(self, start, text):
        cache_key = text[start:start+10]  # 最多缓存10字符
        if cache_key in self._keyword_cache:
            return self._keyword_cache[cache_key]
        # ... 匹配逻辑
        self._keyword_cache[cache_key] = result
        return result
```

**预期效果**：词法分析速度提升 10-15%

### 优先级3：语法分析器优化
```python
class Parser:
    def parse(self, tokens):
        # 合并两遍为一遍
        self.tokens = tokens
        self.pos = 0
        statements = []
        
        while not self._is_at_end():
            stmt = self._parse_statement_with_collection()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def _parse_statement_with_collection(self):
        # 解析的同时收集用户函数
        # ...
```

**预期效果**：解析速度提升 30-40%

## 性能测试基准

### 测试用例
1. **小型程序**（<100行）：应 < 10ms
2. **中型程序**（100-1000行）：应 < 100ms
3. **大型程序**（>1000行）：应 < 500ms

### 测试方法
```bash
# 创建测试文件
python benchmark.py --size small
python benchmark.py --size medium
python benchmark.py --size large
```

## 实施计划

### 阶段1：代码生成器优化（1天）
- 修改 codegen.py 使用 StringIO
- 性能测试验证
- 提交优化代码

### 阶段2：词法分析器优化（1-2天）
- 添加关键字缓存
- 性能测试验证
- 提交优化代码

### 阶段3：语法分析器优化（2-3天）
- 重构解析器为单遍解析
- 性能测试验证
- 提交优化代码

## 风险评估

- **兼容性**：优化不应改变编译结果
- **正确性**：优化后必须通过所有测试
- **可维护性**：优化代码应保持可读性

---

*创建时间：2026-05-16*
