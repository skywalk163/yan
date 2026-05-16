# 言语言阶段2：纯言语言重写编译器计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 逐步减少 Python 代码块依赖，用纯言语言重写编译器核心模块，最终实现真正的自举。

**架构：** 采用渐进式策略，先从最独立的模块（utils、token、nodes）开始，逐步重写核心编译器模块（lexer、parser、codegen），最后整合为完整的纯言语言编译器。

**技术栈：** Python 3.12（宿主环境）、言语言（目标语言）、模块系统、结构体

---

## 当前状态评估

### 已完成（阶段1）

**语言特性：**
- ✅ 模块系统：`导入`、`模块`、`导出`、`从`
- ✅ 结构体：`结构 名称 字段1 类型1...`
- ✅ 测试套件：100% 通过

**自举目录文件：**
```
yan/selfhost/
├── utils.yan          (116行, 24行纯言语言, 84.5% Python)
├── token.yan          (85行, 17行纯言语言, 69.7% Python)
├── nodes.yan          (112行, 88行纯言语言, 0.0% Python) ✅
├── ast.yan            (129行, 27行纯言语言, 81.3% Python)
├── error.yan          (83行, 74行纯言语言, 0.0% Python) ✅
├── lexer.yan          (169行, 84行纯言语言, 34.2% Python)
├── parser.yan         (240行, 8行纯言语言, 96.5% Python)
├── codegen.yan        (181行, 6行纯言语言, 96.5% Python)
├── evaluator.yan      (219行, 4行纯言语言, 97.8% Python)
└── compiler.yan       (436行, 0行纯言语言, 100% Python) ❌
```

**关键发现：**
- `nodes.yan` 和 `error.yan` 已经是纯言语言实现 ✅
- `lexer.yan` 有较多纯言语言代码（84行）
- `compiler.yan` 仍然是 100% Python 代码块
- 其他模块仍大量依赖 Python 代码块

---

## 阶段2目标

**总体目标：** 将 Python 代码块占比从当前的 ~80% 降低到 < 20%

**量化指标：**
- utils.yan: 84.5% → < 30%
- token.yan: 69.7% → < 30%
- ast.yan: 81.3% → < 30%
- lexer.yan: 34.2% → < 20%
- parser.yan: 96.5% → < 30%
- codegen.yan: 96.5% → < 30%
- evaluator.yan: 97.8% → < 30%
- compiler.yan: 100% → < 30%

---

## 文件结构

### 重写优先级

**优先级1（已完成）：**
- ✅ `nodes.yan` — AST 节点定义（0% Python）
- ✅ `error.yan` — 错误处理（0% Python）

**优先级2（基础模块）：**
- `utils.yan` — 工具函数（需要重写）
- `token.yan` — Token 定义（需要重写）
- `ast.yan` — AST 辅助函数（需要重写）

**优先级3（核心编译器）：**
- `lexer.yan` — 词法分析器（部分完成，需要完善）
- `parser.yan` — 语法分析器（需要重写）
- `codegen.yan` — 代码生成器（需要重写）
- `evaluator.yan` — 求值器（需要重写）

**优先级4（整合）：**
- `compiler.yan` — 主编译器（需要重写）

---

## 任务分解

### 任务1：重写 utils.yan

**文件：**
- 修改：`yan/selfhost/utils.yan`
- 测试：`tests/test_utils_yan.py`

**目标：** 将 Python 代码块占比从 84.5% 降低到 < 30%

- [ ] **步骤1：分析当前 utils.yan 的 Python 代码块**

读取 `yan/selfhost/utils.yan`，识别所有 Python 代码块的功能：
- 字符判断函数（is_chinese_char, is_digit, is_letter）
- 字符串操作函数（substring, char_at）
- 列表操作函数

- [ ] **步骤2：编写 utils 测试**

创建 `tests/test_utils_yan.py`：

```python
"""utils.yan 功能测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen

def test_utils_compile():
    """测试 utils.yan 能够编译"""
    with open('yan/selfhost/utils.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert len(python_code) > 0
    assert 'def is_chinese_char' in python_code or 'is_chinese_char' in python_code

def test_utils_functions():
    """测试 utils 函数功能"""
    # 编译并执行 utils.yan
    with open('yan/selfhost/utils.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    # 执行生成的代码
    namespace = {}
    exec(python_code, namespace)
    
    # 测试函数
    assert namespace['is_chinese_char']('中') == True
    assert namespace['is_chinese_char']('a') == False
    assert namespace['is_digit']('5') == True
    assert namespace['is_digit']('a') == False

if __name__ == '__main__':
    test_utils_compile()
    test_utils_functions()
    print("utils.yan 测试通过")
```

- [ ] **步骤3：重写字符判断函数**

将 `utils.yan` 中的 Python 代码块替换为纯言语言：

```yan
-- 判断是否为汉字
定是汉字=函字符
    定编码={{ord(char)}}。
    返回编码大于等于19968且编码小于等于40869。
。

-- 判断是否为数字
定是数字=函字符
    返回字符大于等于"0"且字符小于等于"9"。
。

-- 判断是否为字母
定是字母=函字符
    返回字符大于等于"a"且字符小于等于"z"或字符大于等于"A"且字符小于等于"Z"。
。
```

- [ ] **步骤4：重写字符串操作函数**

```yan
-- 子串
定子串=函字符串开始结束
    若结束等于空
        返回{{s[start:]}}。
    否则
        返回{{s[start:end]}}。
    。
。

-- 字符位置
定字符位置=函字符串索引
    若索引小于长字符串
        返回{{s[index]}}。
    否则
        返回空。
    。
。
```

- [ ] **步骤5：运行测试验证**

运行：`cd yan && python tests/test_utils_yan.py`
预期：PASS

- [ ] **步骤6：验证 Python 代码块占比**

运行：`cd yan/selfhost && python -c "分析 utils.yan"`
预期：Python 代码块占比 < 30%

- [ ] **步骤7：Commit**

```bash
git add yan/selfhost/utils.yan tests/test_utils_yan.py
git commit -m "refactor(utils): rewrite utils.yan with pure Yan language"
```

---

### 任务2：重写 token.yan

**文件：**
- 修改：`yan/selfhost/token.yan`
- 测试：`tests/test_token_yan.py`

**目标：** 将 Python 代码块占比从 69.7% 降低到 < 30%

- [ ] **步骤1：分析当前 token.yan 的 Python 代码块**

识别需要重写的功能：
- Token 类型常量定义
- Token 创建函数
- Token 访问函数

- [ ] **步骤2：编写 token 测试**

创建 `tests/test_token_yan.py`：

```python
"""token.yan 功能测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_token_compile():
    """测试 token.yan 能够编译"""
    with open('yan/selfhost/token.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert len(python_code) > 0

if __name__ == '__main__':
    test_token_compile()
    print("token.yan 测试通过")
```

- [ ] **步骤3：重写 Token 定义**

使用结构体定义 Token：

```yan
-- Token 类型定义
结构 Token
    类型 串。
    值 串。
    行 数。
    列 数。
。

-- Token 类型常量
定TOKEN_NUM="NUM"。
定TOKEN_STR="STR"。
定TOKEN_WORD="WORD"。
定TOKEN_DOT="DOT"。
定TOKEN_COMMA="COMMA"。
定TOKEN_EQUALS="EQUALS"。
定TOKEN_COLON="COLON"。
定TOKEN_EOF="EOF"。

-- 创建 Token
定创建Token=函类型值行列
    返回Token类型值行列。
。

-- 获取 Token 类型
定取类型=函Token
    返回Token类型。
。

-- 获取 Token 值
定取值=函Token
    返回Token值。
。

导出 Token 创建Token 取类型 取值 TOKEN_NUM TOKEN_STR TOKEN_WORD TOKEN_DOT TOKEN_COMMA TOKEN_EQUALS TOKEN_COLON TOKEN_EOF。
```

- [ ] **步骤4：运行测试验证**

运行：`cd yan && python tests/test_token_yan.py`
预期：PASS

- [ ] **步骤5：验证 Python 代码块占比**

预期：Python 代码块占比 < 30%

- [ ] **步骤6：Commit**

```bash
git add yan/selfhost/token.yan tests/test_token_yan.py
git commit -m "refactor(token): rewrite token.yan with pure Yan language"
```

---

### 任务3：重写 ast.yan

**文件：**
- 修改：`yan/selfhost/ast.yan`
- 测试：`tests/test_ast_yan.py`

**目标：** 将 Python 代码块占比从 81.3% 降低到 < 30%

- [ ] **步骤1：分析当前 ast.yan 的 Python 代码块**

识别需要重写的功能：
- AST 节点创建函数
- AST 节点访问函数

- [ ] **步骤2：编写 ast 测试**

创建 `tests/test_ast_yan.py`：

```python
"""ast.yan 功能测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ast_compile():
    """测试 ast.yan 能够编译"""
    with open('yan/selfhost/ast.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert len(python_code) > 0

if __name__ == '__main__':
    test_ast_compile()
    print("ast.yan 测试通过")
```

- [ ] **步骤3：重写 AST 辅助函数**

```yan
-- AST 节点类型判断
定是定义=函节点
    返回节点类型等于"Define"。
。

定是函数=函节点
    返回节点类型等于"Function"。
。

定是条件=函节点
    返回节点类型等于"If"。
。

-- AST 节点访问
定取节点名称=函节点
    返回节点名称。
。

定取节点值=函节点
    返回节点值。
。

导出 是定义 是函数 是条件 取节点名称 取节点值。
```

- [ ] **步骤4：运行测试验证**

运行：`cd yan && python tests/test_ast_yan.py`
预期：PASS

- [ ] **步骤5：Commit**

```bash
git add yan/selfhost/ast.yan tests/test_ast_yan.py
git commit -m "refactor(ast): rewrite ast.yan with pure Yan language"
```

---

### 任务4：完善 lexer.yan

**文件：**
- 修改：`yan/selfhost/lexer.yan`
- 测试：`tests/test_lexer_yan.py`

**目标：** 将 Python 代码块占比从 34.2% 降低到 < 20%

- [ ] **步骤1：分析当前 lexer.yan 的 Python 代码块**

识别剩余的 Python 代码块：
- 字符编码转换（ord, chr）
- 字符串切片
- 复杂的条件判断

- [ ] **步骤2：编写 lexer 功能测试**

创建 `tests/test_lexer_yan.py`：

```python
"""lexer.yan 功能测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_lexer_yan_tokenize():
    """测试 lexer.yan 的 tokenize 函数"""
    # 编译 lexer.yan
    with open('yan/selfhost/lexer.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    # 执行生成的代码
    namespace = {}
    exec(python_code, namespace)
    
    # 测试 tokenize 函数
    tokenize = namespace.get('tokenize')
    if tokenize:
        result = tokenize('定x=42。')
        assert len(result) > 0
        print(f"Tokenize 结果: {result}")

if __name__ == '__main__':
    test_lexer_yan_tokenize()
    print("lexer.yan 测试通过")
```

- [ ] **步骤3：逐步替换 Python 代码块**

优先替换简单的 Python 代码块：
- 字符判断 → 使用纯言语言比较
- 简单的字符串操作 → 使用内置函数

保留复杂的 Python 代码块（如 ord, chr），标记为待优化。

- [ ] **步骤4：运行测试验证**

运行：`cd yan && python tests/test_lexer_yan.py`
预期：PASS

- [ ] **步骤5：验证 Python 代码块占比**

预期：Python 代码块占比 < 20%

- [ ] **步骤6：Commit**

```bash
git add yan/selfhost/lexer.yan tests/test_lexer_yan.py
git commit -m "refactor(lexer): reduce Python code blocks in lexer.yan"
```

---

### 任务5：重写 parser.yan

**文件：**
- 修改：`yan/selfhost/parser.yan`
- 测试：`tests/test_parser_yan.py`

**目标：** 将 Python 代码块占比从 96.5% 降低到 < 30%

**策略：** 这是最大的挑战，需要大量重写。采用分步策略：

- [ ] **步骤1：分析 parser.yan 的核心功能**

识别关键解析函数：
- `parse_program` — 解析程序
- `parse_statement` — 解析语句
- `parse_define` — 解析变量定义
- `parse_function` — 解析函数定义
- `parse_if` — 解析条件语句

- [ ] **步骤2：编写 parser 测试**

创建 `tests/test_parser_yan.py`：

```python
"""parser.yan 功能测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_parser_yan_compile():
    """测试 parser.yan 能够编译"""
    with open('yan/selfhost/parser.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert len(python_code) > 0
    assert 'def parse' in python_code or 'parse' in python_code

if __name__ == '__main__':
    test_parser_yan_compile()
    print("parser.yan 测试通过")
```

- [ ] **步骤3：重写简单解析函数**

从最简单的解析函数开始：

```yan
-- 解析程序
定解析程序=函Token列表
    定语句列表=列。
    定位置=0。
    
    当位置小于长Token列表
        定语句=解析语句Token列表位置。
        若语句不等于空
            语句列表=添语句列表语句。
        。
        位置=位置加1。
    。
    
    返回Program语句列表。
。

-- 解析语句
定解析语句=函Token列表位置
    定Token=入Token列表位置。
    
    若Token类型等于"WORD"且Token值等于"定"
        返回解析定义Token列表位置。
    否则若Token类型等于"WORD"且Token值等于"若"
        返回解析条件Token列表位置。
    否则
        返回空。
    。
。
```

- [ ] **步骤4：逐步重写复杂解析函数**

对于复杂的解析逻辑，可以暂时保留 Python 代码块，但添加注释说明：

```yan
-- 解析表达式（复杂，暂时保留 Python）
定解析表达式=函Token列表位置
    {{# TODO: 用纯言语言重写
    # 当前保留 Python 实现
    return parse_expression_impl(tokens, pos)
    }}
。
```

- [ ] **步骤5：运行测试验证**

运行：`cd yan && python tests/test_parser_yan.py`
预期：PASS

- [ ] **步骤6：验证 Python 代码块占比**

预期：Python 代码块占比 < 30%

- [ ] **步骤7：Commit**

```bash
git add yan/selfhost/parser.yan tests/test_parser_yan.py
git commit -m "refactor(parser): rewrite parser.yan with pure Yan language (partial)"
```

---

### 任务6：重写 codegen.yan

**文件：**
- 修改：`yan/selfhost/codegen.yan`
- 测试：`tests/test_codegen_yan.py`

**目标：** 将 Python 代码块占比从 96.5% 降低到 < 30%

- [ ] **步骤1：分析 codegen.yan 的核心功能**

识别关键代码生成函数：
- `generate` — 主生成函数
- `generate_statement` — 生成语句
- `generate_define` — 生成变量定义
- `generate_function` — 生成函数定义

- [ ] **步骤2：编写 codegen 测试**

创建 `tests/test_codegen_yan.py`：

```python
"""codegen.yan 功能测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_codegen_yan_compile():
    """测试 codegen.yan 能够编译"""
    with open('yan/selfhost/codegen.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert len(python_code) > 0

if __name__ == '__main__':
    test_codegen_yan_compile()
    print("codegen.yan 测试通过")
```

- [ ] **步骤3：重写代码生成函数**

```yan
-- 生成 Python 代码
定生成代码=函AST
    定代码=""。
    
    遍历语句于AST语句列表
        代码=连代码生成语句语句。
        代码=连代码换行符。
    。
    
    返回代码。
。

-- 生成语句代码
定生成语句=函语句
    若语句类型等于"Define"
        返回生成定义语句。
    否则若语句类型等于"Function"
        返回生成函数语句。
    否则
        返回""。
    。
。

-- 生成变量定义
定生成定义=函语句
    返回连语句名称" = "语句值。
。
```

- [ ] **步骤4：运行测试验证**

运行：`cd yan && python tests/test_codegen_yan.py`
预期：PASS

- [ ] **步骤5：Commit**

```bash
git add yan/selfhost/codegen.yan tests/test_codegen_yan.py
git commit -m "refactor(codegen): rewrite codegen.yan with pure Yan language (partial)"
```

---

### 任务7：重写 compiler.yan

**文件：**
- 修改：`yan/selfhost/compiler.yan`
- 测试：`tests/test_compiler_yan.py`

**目标：** 将 Python 代码块占比从 100% 降低到 < 30%

**策略：** 整合所有模块，用纯言语言实现主编译器

- [ ] **步骤1：分析 compiler.yan 的功能**

识别编译器的主要功能：
- 导入所有模块
- 整合编译流程
- 提供编译入口

- [ ] **步骤2：编写 compiler 测试**

创建 `tests/test_compiler_yan.py`：

```python
"""compiler.yan 功能测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_compiler_yan_compile():
    """测试 compiler.yan 能够编译"""
    with open('yan/selfhost/compiler.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert len(python_code) > 0

if __name__ == '__main__':
    test_compiler_yan_compile()
    print("compiler.yan 测试通过")
```

- [ ] **步骤3：重写 compiler.yan**

```yan
-- 言语言自举编译器
导入 utils。
导入 token。
导入 nodes。
导入 ast。
导入 lexer。
导入 parser。
导入 codegen。

-- 编译函数
定编译=函源码
    定Token列表=词法分析源码。
    定AST=语法分析Token列表。
    定代码=生成代码AST。
    返回代码。
。

-- 主函数
定主=函
    {{# 主函数实现
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            source = f.read()
        result = compile(source)
        print(result)
    }}
。

导出 编译 主。
```

- [ ] **步骤4：运行测试验证**

运行：`cd yan && python tests/test_compiler_yan.py`
预期：PASS

- [ ] **步骤5：验证 Python 代码块占比**

预期：Python 代码块占比 < 30%

- [ ] **步骤6：Commit**

```bash
git add yan/selfhost/compiler.yan tests/test_compiler_yan.py
git commit -m "refactor(compiler): rewrite compiler.yan with pure Yan language (partial)"
```

---

### 任务8：完成自举验证

**文件：**
- 修改：`yan/selfhost/bootstrap_v2.py`
- 创建：`yan/selfhost/BOOTSTRAP_V2_REPORT.md`
- 测试：`tests/test_bootstrap_v2.py`

**目标：** 验证纯言语言编译器能够编译自身

- [ ] **步骤1：运行自举验证**

运行：`cd yan/selfhost && python bootstrap_v2.py`

- [ ] **步骤2：对比编译器输出**

验证 compiler1.py 和 compiler2.py 是否相同

- [ ] **步骤3：生成验证报告**

更新 `BOOTSTRAP_V2_REPORT.md`

- [ ] **步骤4：Commit**

```bash
git add yan/selfhost/bootstrap_v2.py yan/selfhost/BOOTSTRAP_V2_REPORT.md
git commit -m "feat(bootstrap): complete bootstrap verification V2"
```

---

## 总结

### 预计工作量

- **任务1-3**（基础模块重写）：1-2周
- **任务4**（完善 lexer）：1周
- **任务5-6**（核心编译器重写）：2-3周
- **任务7**（整合 compiler）：1周
- **任务8**（自举验证）：1周

**总计**：6-8周（全职开发）或 12-16周（兼职开发）

### 关键里程碑

1. ✅ 基础模块重写完成（utils, token, ast）
2. ✅ 词法分析器完善（lexer.yan < 20% Python）
3. ✅ 语法分析器重写（parser.yan < 30% Python）
4. ✅ 代码生成器重写（codegen.yan < 30% Python）
5. ✅ 主编译器重写（compiler.yan < 30% Python）
6. ✅ 自举验证成功

### 风险和缓解

**高风险**：
- 纯言语言表达能力不足 → 保留必要的 Python 代码块
- 性能问题 → 优化关键路径
- 调试困难 → 充分的测试覆盖

**缓解策略**：
- 采用渐进式重写，每步都验证
- 保留 Python 代码块作为后备
- 完善测试套件

### 成功标准

**阶段2完成标准**：
- 所有模块 Python 代码块占比 < 30%
- 自举验证通过（compiler1 == compiler2）
- 所有测试通过
- 文档完善

---

**下一步**：开始执行任务1，重写 utils.yan
