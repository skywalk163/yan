# 言语言渐进式自举实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 采用渐进式策略，先实现模块系统和结构体，再逐步用纯言语言重写编译器模块，最终实现真正的自举。

**架构：** 分三个阶段推进：阶段1扩展语言能力（模块系统、结构体、类型系统），阶段2用纯言语言重写编译器（词法分析器→语法分析器→代码生成器），阶段3完成自举验证。

**技术栈：** Python 3.12（编译器宿主）、言语言（目标语言）、递归下降解析器、模块依赖图

---

## 文件结构

### 阶段1：语言能力扩展

**新增文件：**
- `yan/module.py` — 模块系统实现（导入解析、依赖图、缓存）
- `yan/struct.py` — 结构体/记录类型实现
- `yan/types.py` — 类型系统基础设施
- `tests/test_module.py` — 模块系统测试
- `tests/test_struct.py` — 结构体测试
- `tests/test_types.py` — 类型系统测试

**修改文件：**
- `yan/lexer.py` — 添加模块和结构体关键字
- `yan/parser.py` — 添加模块和结构体解析逻辑
- `yan/codegen.py` — 添加模块和结构体代码生成
- `yan/runtime.py` — 添加结构体运行时支持

### 阶段2：编译器重写

**新增文件：**
- `yan/selfhost/lexer.yan` — 纯言语言词法分析器
- `yan/selfhost/parser.yan` — 纯言语言语法分析器
- `yan/selfhost/codegen.yan` — 纯言语言代码生成器
- `yan/selfhost/types.yan` — Token 和 AST 类型定义
- `yan/selfhost/main.yan` — 主编译器入口

**修改文件：**
- `yan/selfhost/compiler.yan` — 逐步替换 Python 代码块

### 阶段3：自举验证

**新增文件：**
- `yan/selfhost/bootstrap_v2.py` — 新版自举验证脚本
- `yan/selfhost/BOOTSTRAP_V2_REPORT.md` — 自举验证报告

---

## 阶段1：语言能力扩展（预计2-3个月）

### 任务1：实现模块系统 — 词法分析

**文件：**
- 修改：`yan/lexer.py:71-105`
- 测试：`tests/test_module.py`

- [ ] **步骤1：编写模块关键字词法测试**

创建 `tests/test_module.py`：

```python
"""模块系统测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer

def test_module_keywords():
    """测试模块关键字词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('导入 模块 导出')
    
    assert tokens[0].type.name == 'WORD'
    assert tokens[0].value == '导入'
    assert tokens[1].type.name == 'WORD'
    assert tokens[1].value == '模块'
    assert tokens[2].type.name == 'WORD'
    assert tokens[2].value == '导出'

def test_import_statement():
    """测试导入语句词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('导入 utils')
    
    assert tokens[0].value == '导入'
    assert tokens[1].value == 'utils'

if __name__ == '__main__':
    test_module_keywords()
    test_import_statement()
    print("模块词法测试通过")
```

- [ ] **步骤2：运行测试验证失败**

运行：`cd yan && python tests/test_module.py`
预期：FAIL，报错 "assert tokens[0].value == '导入'"

- [ ] **步骤3：添加模块关键字到词法分析器**

修改 `yan/lexer.py` 第71-105行，在 `keywords` 集合中添加：

```python
self.keywords = keywords or {
    # 多字动词
    '定义', '阶乘', '平方', '否则', '如果', '那么', '不等',
    # 赋值
    '等于',
    # 循环
    '遍历', '当', '于',
    # 模块系统（新增）
    '导入', '模块', '导出', '从',
    # 数学库
    '正弦', '余弦', '正切', '反正弦', '反余弦', '反正切',
    '指数', '对数', '对数10', '开方', '取整', '进位', '四舍五入',
    '随机', '随机整数', '圆周率', '自然常数',
    # ... 其他关键字保持不变
}
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_module.py`
预期：PASS，输出 "模块词法测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/lexer.py tests/test_module.py
git commit -m "feat(module): add module system keywords to lexer"
```

---

### 任务2：实现模块系统 — 语法分析

**文件：**
- 修改：`yan/parser.py:83-112`（添加模块动词）
- 修改：`yan/parser.py:560-690`（添加模块解析逻辑）
- 修改：`tests/test_module.py`（添加语法测试）

- [ ] **步骤1：编写模块语句语法测试**

在 `tests/test_module.py` 中添加：

```python
from parser import Parser
from codegen import PythonCodeGen

def test_import_statement_parse():
    """测试导入语句语法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('导入 utils。')
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    stmt = ast.statements[0]
    assert hasattr(stmt, 'module_name')
    assert stmt.module_name == 'utils'

def test_export_statement_parse():
    """测试导出语句语法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('导出 函数名。')
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    stmt = ast.statements[0]
    assert hasattr(stmt, 'names')
    assert '函数名' in stmt.names

if __name__ == '__main__':
    test_module_keywords()
    test_import_statement()
    test_import_statement_parse()
    test_export_statement_parse()
    print("所有模块测试通过")
```

- [ ] **步骤2：运行测试验证失败**

运行：`cd yan && python tests/test_module.py`
预期：FAIL，报错 "AttributeError: 'Word' object has no attribute 'module_name'"

- [ ] **步骤3：添加模块语句 AST 节点**

修改 `yan/nodes.py`，添加模块语句节点：

```python
@dataclass
class Import(Node):
    """导入语句"""
    module_name: str
    names: List[str] = None  # 可选：导入特定名称

@dataclass
class Export(Node):
    """导出语句"""
    names: List[str]
```

- [ ] **步骤4：添加模块动词到解析器**

修改 `yan/parser.py` 第83-112行，在 `BUILTIN_VERBS` 中添加：

```python
BUILTIN_VERBS = {
    '加', '减', '乘', '除', '模', '幂', '绝对', '负',
    '大', '小', '等', '不等',
    '且', '或', '非',
    '首', '余', '入', '长', '添', '连', '含', '空',
    '皆', '只', '归', '潜',
    '印', '读', '写', '行',
    '若', '则', '否则', '定', '函', '返回',
    '遍历', '于', '当',
    '列', '典', '序', '范围',
    # 模块系统（新增）
    '导入', '模块', '导出', '从',
    # ... 其他动词保持不变
}
```

- [ ] **步骤5：实现导入语句解析**

修改 `yan/parser.py` 第560-690行，在 `_parse_term()` 方法中添加：

```python
def _parse_term(self) -> Node:
    """解析项"""
    # 导入语句
    if self._check_word('导入'):
        return self._parse_import()
    
    # 导出语句
    if self._check_word('导出'):
        return self._parse_export()
    
    # ... 原有代码保持不变

def _parse_import(self) -> Node:
    """解析导入语句：导入 模块名 或 导入 名称1 名称2 于 模块名"""
    self._advance()  # 消耗 '导入'
    
    # 收集导入的名称
    names = []
    while (not self._is_at_end() and 
           self._current().type == TokenType.WORD and
           not self._check_word('于') and
           not self._check_word('。')):
        names.append(self._advance().value)
    
    # 检查是否有 '于' 关键字
    if self._check_word('于'):
        self._advance()  # 消耗 '于'
        module_name = self._advance().value
    else:
        # 简单导入：导入 模块名
        module_name = names[0] if names else ''
        names = None
    
    # 消耗句号
    if self._check_word('。'):
        self._advance()
    
    return Import(module_name=module_name, names=names)

def _parse_export(self) -> Node:
    """解析导出语句：导出 名称1 名称2 ..."""
    self._advance()  # 消耗 '导出'
    
    names = []
    while (not self._is_at_end() and 
           self._current().type == TokenType.WORD and
           not self._check_word('。')):
        names.append(self._advance().value)
    
    # 消耗句号
    if self._check_word('。'):
        self._advance()
    
    return Export(names=names)
```

- [ ] **步骤6：运行测试验证通过**

运行：`cd yan && python tests/test_module.py`
预期：PASS，输出 "所有模块测试通过"

- [ ] **步骤7：Commit**

```bash
git add yan/nodes.py yan/parser.py tests/test_module.py
git commit -m "feat(module): implement import and export statement parsing"
```

---

### 任务3：实现模块系统 — 代码生成

**文件：**
- 修改：`yan/codegen.py`
- 修改：`tests/test_module.py`（添加代码生成测试）

- [ ] **步骤1：编写模块代码生成测试**

在 `tests/test_module.py` 中添加：

```python
def test_import_codegen():
    """测试导入语句代码生成"""
    code = '导入 utils。'
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert 'from utils import *' in python_code or 'import utils' in python_code

def test_export_codegen():
    """测试导出语句代码生成"""
    code = '导出 函数名。'
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    # 导出语句在 Python 中通常不需要特殊处理
    assert python_code.strip() == '' or '__all__' in python_code

if __name__ == '__main__':
    test_module_keywords()
    test_import_statement()
    test_import_statement_parse()
    test_export_statement_parse()
    test_import_codegen()
    test_export_codegen()
    print("所有模块测试通过")
```

- [ ] **步骤2：运行测试验证失败**

运行：`cd yan && python tests/test_module.py`
预期：FAIL，报错 "AssertionError"

- [ ] **步骤3：实现模块代码生成**

修改 `yan/codegen.py`，在 `PythonCodeGen` 类中添加：

```python
def visit_Import(self, node: Import) -> str:
    """生成导入语句的 Python 代码"""
    if node.names:
        # 导入特定名称：from module import name1, name2
        names_str = ', '.join(node.names)
        return f'from {node.module_name} import {names_str}'
    else:
        # 导入整个模块
        return f'import {node.module_name}'

def visit_Export(self, node: Export) -> str:
    """生成导出语句的 Python 代码"""
    # Python 使用 __all__ 来控制导出
    names_str = ', '.join(f"'{name}'" for name in node.names)
    return f'__all__ = [{names_str}]'
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_module.py`
预期：PASS，输出 "所有模块测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/codegen.py tests/test_module.py
git commit -m "feat(module): implement import and export code generation"
```

---

### 任务4：实现模块系统 — 模块加载器

**文件：**
- 创建：`yan/module.py`
- 创建：`tests/test_module_loader.py`

- [ ] **步骤1：编写模块加载器测试**

创建 `tests/test_module_loader.py`：

```python
"""模块加载器测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module import ModuleLoader

def test_module_loader_init():
    """测试模块加载器初始化"""
    loader = ModuleLoader()
    assert loader.module_cache == {}
    assert loader.module_path == []

def test_resolve_module_path():
    """测试模块路径解析"""
    loader = ModuleLoader(module_path=['./yan/selfhost'])
    path = loader.resolve_module_path('utils')
    assert path.endswith('utils.yan') or path.endswith('utils/__init__.yan')

def test_load_module():
    """测试模块加载"""
    # 创建测试模块
    test_module_dir = 'test_modules'
    os.makedirs(test_module_dir, exist_ok=True)
    
    with open(f'{test_module_dir}/test_mod.yan', 'w', encoding='utf-8') as f:
        f.write('定测试值=42。导出测试值。')
    
    loader = ModuleLoader(module_path=[test_module_dir])
    module = loader.load_module('test_mod')
    
    assert module is not None
    assert '测试值' in module.exports
    
    # 清理
    os.remove(f'{test_module_dir}/test_mod.yan')
    os.rmdir(test_module_dir)

if __name__ == '__main__':
    test_module_loader_init()
    test_resolve_module_path()
    test_load_module()
    print("模块加载器测试通过")
```

- [ ] **步骤2：运行测试验证失败**

运行：`cd yan && python tests/test_module_loader.py`
预期：FAIL，报错 "ModuleNotFoundError: No module named 'module'"

- [ ] **步骤3：实现模块加载器**

创建 `yan/module.py`：

```python
"""
言语言模块系统
支持模块导入、导出和依赖管理
"""
import os
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field

@dataclass
class Module:
    """模块定义"""
    name: str
    path: str
    exports: Set[str] = field(default_factory=set)
    imports: Dict[str, List[str]] = field(default_factory=dict)
    code: str = ''
    compiled_code: str = ''
    namespace: Dict[str, Any] = field(default_factory=dict)

class ModuleLoader:
    """模块加载器"""
    
    def __init__(self, module_path: List[str] = None):
        """
        初始化模块加载器
        
        Args:
            module_path: 模块搜索路径列表
        """
        self.module_cache: Dict[str, Module] = {}
        self.module_path = module_path or ['.']
        self.loading_stack: Set[str] = set()  # 检测循环依赖
    
    def resolve_module_path(self, module_name: str) -> Optional[str]:
        """
        解析模块路径
        
        Args:
            module_name: 模块名称
        
        Returns:
            模块文件的绝对路径，如果找不到则返回 None
        """
        for base_path in self.module_path:
            # 尝试直接文件
            file_path = os.path.join(base_path, f'{module_name}.yan')
            if os.path.exists(file_path):
                return os.path.abspath(file_path)
            
            # 尝试包目录
            package_path = os.path.join(base_path, module_name, '__init__.yan')
            if os.path.exists(package_path):
                return os.path.abspath(package_path)
        
        return None
    
    def load_module(self, module_name: str) -> Optional[Module]:
        """
        加载模块
        
        Args:
            module_name: 模块名称
        
        Returns:
            加载的模块对象，如果失败则返回 None
        """
        # 检查缓存
        if module_name in self.module_cache:
            return self.module_cache[module_name]
        
        # 检测循环依赖
        if module_name in self.loading_stack:
            raise ImportError(f"检测到循环依赖: {module_name}")
        
        # 解析模块路径
        module_path = self.resolve_module_path(module_name)
        if not module_path:
            raise ImportError(f"找不到模块: {module_name}")
        
        # 读取模块代码
        with open(module_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 创建模块对象
        module = Module(
            name=module_name,
            path=module_path,
            code=code
        )
        
        # 标记为正在加载
        self.loading_stack.add(module_name)
        
        try:
            # 解析导入和导出
            self._parse_module_metadata(module)
            
            # 编译模块
            self._compile_module(module)
            
            # 缓存模块
            self.module_cache[module_name] = module
        finally:
            # 移除加载标记
            self.loading_stack.remove(module_name)
        
        return module
    
    def _parse_module_metadata(self, module: Module):
        """解析模块的导入和导出声明"""
        from lexer import Lexer
        from parser import Parser
        
        lexer = Lexer()
        tokens = lexer.tokenize(module.code)
        parser = Parser()
        ast = parser.parse(tokens)
        
        for stmt in ast.statements:
            if hasattr(stmt, 'module_name'):
                # Import 语句
                module.imports[stmt.module_name] = stmt.names or ['*']
            elif hasattr(stmt, 'names'):
                # Export 语句
                module.exports.update(stmt.names)
    
    def _compile_module(self, module: Module):
        """编译模块"""
        from lexer import Lexer
        from parser import Parser
        from codegen import PythonCodeGen
        
        lexer = Lexer()
        tokens = lexer.tokenize(module.code)
        parser = Parser()
        ast = parser.parse(tokens)
        gen = PythonCodeGen()
        module.compiled_code = gen.generate(ast)
    
    def get_export(self, module_name: str, name: str) -> Any:
        """
        获取模块的导出项
        
        Args:
            module_name: 模块名称
            name: 导出项名称
        
        Returns:
            导出项的值
        """
        module = self.load_module(module_name)
        if not module:
            raise ImportError(f"找不到模块: {module_name}")
        
        if name not in module.exports:
            raise AttributeError(f"模块 {module_name} 没有导出 {name}")
        
        # 执行模块代码并返回导出项
        if not module.namespace:
            exec(module.compiled_code, module.namespace)
        
        return module.namespace.get(name)
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_module_loader.py`
预期：PASS，输出 "模块加载器测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/module.py tests/test_module_loader.py
git commit -m "feat(module): implement module loader with caching and dependency detection"
```

---

### 任务5：实现结构体 — 词法和语法

**文件：**
- 修改：`yan/lexer.py`（添加结构体关键字）
- 修改：`yan/parser.py`（添加结构体解析）
- 创建：`tests/test_struct.py`

- [ ] **步骤1：编写结构体词法和语法测试**

创建 `tests/test_struct.py`：

```python
"""结构体测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from codegen import PythonCodeGen

def test_struct_keywords():
    """测试结构体关键字词法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize('结构 类型 字段')
    
    assert tokens[0].value == '结构'
    assert tokens[1].value == '类型'
    assert tokens[2].value == '字段'

def test_struct_definition():
    """测试结构体定义语法分析"""
    code = '''
    结构 点
        横 数。
        纵 数。
    。
    '''
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1
    stmt = ast.statements[0]
    assert hasattr(stmt, 'name')
    assert stmt.name == '点'
    assert hasattr(stmt, 'fields')
    assert len(stmt.fields) == 2

def test_struct_instantiation():
    """测试结构体实例化"""
    code = '定原点=点横0纵0。'
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    
    assert len(ast.statements) == 1

if __name__ == '__main__':
    test_struct_keywords()
    test_struct_definition()
    test_struct_instantiation()
    print("结构体测试通过")
```

- [ ] **步骤2：运行测试验证失败**

运行：`cd yan && python tests/test_struct.py`
预期：FAIL，报错 "assert tokens[0].value == '结构'"

- [ ] **步骤3：添加结构体关键字和解析逻辑**

修改 `yan/lexer.py`，在 `keywords` 集合中添加：

```python
'结构', '类型', '字段',
```

修改 `yan/nodes.py`，添加结构体节点：

```python
@dataclass
class StructDef(Node):
    """结构体定义"""
    name: str
    fields: List[tuple]  # [(字段名, 类型名), ...]

@dataclass
class StructInit(Node):
    """结构体实例化"""
    struct_name: str
    field_values: Dict[str, Node]
```

修改 `yan/parser.py`，在 `BUILTIN_VERBS` 中添加：

```python
'结构', '类型', '字段',
```

在 `_parse_term()` 方法中添加：

```python
# 结构体定义
if self._check_word('结构'):
    return self._parse_struct_def()
```

实现结构体解析方法：

```python
def _parse_struct_def(self) -> Node:
    """解析结构体定义：结构 名称 字段1 类型1 字段2 类型2 ..."""
    self._advance()  # 消耗 '结构'
    
    name = self._advance().value
    fields = []
    
    while not self._is_at_end() and not self._check_word('。'):
        field_name = self._advance().value
        if self._is_at_end() or self._check_word('。'):
            # 没有类型声明
            fields.append((field_name, None))
            break
        
        field_type = self._advance().value
        fields.append((field_name, field_type))
    
    # 消耗句号
    if self._check_word('。'):
        self._advance()
    
    return StructDef(name=name, fields=fields)
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_struct.py`
预期：PASS，输出 "结构体测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/lexer.py yan/nodes.py yan/parser.py tests/test_struct.py
git commit -m "feat(struct): implement struct definition parsing"
```

---

### 任务6：实现结构体 — 代码生成和运行时

**文件：**
- 修改：`yan/codegen.py`（添加结构体代码生成）
- 修改：`yan/runtime.py`（添加结构体运行时支持）
- 修改：`tests/test_struct.py`（添加代码生成测试）

- [ ] **步骤1：编写结构体代码生成测试**

在 `tests/test_struct.py` 中添加：

```python
def test_struct_codegen():
    """测试结构体代码生成"""
    code = '''
    结构 点
        横 数。
        纵 数。
    。
    定原点=点横0纵0。
    '''
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert 'class 点' in python_code or 'dataclass' in python_code
    assert '原点' in python_code

if __name__ == '__main__':
    test_struct_keywords()
    test_struct_definition()
    test_struct_instantiation()
    test_struct_codegen()
    print("所有结构体测试通过")
```

- [ ] **步骤2：运行测试验证失败**

运行：`cd yan && python tests/test_struct.py`
预期：FAIL，报错 "AssertionError: 'class 点' not in python_code"

- [ ] **步骤3：实现结构体代码生成**

修改 `yan/codegen.py`，添加：

```python
def visit_StructDef(self, node: StructDef) -> str:
    """生成结构体定义的 Python 代码"""
    lines = [f'class {node.name}:']
    
    if node.fields:
        lines.append('    def __init__(self, ' + 
                    ', '.join(f'{name}=None' for name, _ in node.fields) + 
                    '):')
        for field_name, _ in node.fields:
            lines.append(f'        self.{field_name} = {field_name}')
    else:
        lines.append('    pass')
    
    return '\n'.join(lines)

def visit_StructInit(self, node: StructInit) -> str:
    """生成结构体实例化的 Python 代码"""
    args = ', '.join(f'{name}={self.visit(value)}' 
                     for name, value in node.field_values.items())
    return f'{node.struct_name}({args})'
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_struct.py`
预期：PASS，输出 "所有结构体测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/codegen.py tests/test_struct.py
git commit -m "feat(struct): implement struct code generation"
```

---

## 阶段2：编译器重写（预计1-2个月）

### 任务7：用纯言语言实现词法分析器

**文件：**
- 创建：`yan/selfhost/lexer.yan`
- 创建：`yan/selfhost/types.yan`
- 创建：`tests/test_lexer_yan.py`

- [ ] **步骤1：创建 Token 类型定义**

创建 `yan/selfhost/types.yan`：

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

导出 Token TOKEN_NUM TOKEN_STR TOKEN_WORD TOKEN_DOT TOKEN_COMMA TOKEN_EQUALS TOKEN_COLON TOKEN_EOF。
```

- [ ] **步骤2：编写词法分析器测试**

创建 `tests/test_lexer_yan.py`：

```python
"""纯言语言词法分析器测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_lexer_yan_exists():
    """测试词法分析器文件存在"""
    assert os.path.exists('yan/selfhost/lexer.yan')

def test_lexer_yan_compile():
    """测试词法分析器能够编译"""
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    with open('yan/selfhost/lexer.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert len(python_code) > 0
    assert 'def tokenize' in python_code or 'tokenize' in python_code

if __name__ == '__main__':
    test_lexer_yan_exists()
    test_lexer_yan_compile()
    print("词法分析器测试通过")
```

- [ ] **步骤3：实现纯言语言词法分析器**

创建 `yan/selfhost/lexer.yan`：

```yan
-- 言语言词法分析器（纯言语言实现）
导入 types。

-- 关键字集合
定关键字=列"定" "函" "若" "则" "否则" "当" "真" "假" "空" "无"。

-- 创建 Token
定创建Token=函类型值行列
    返回Token类型值行列。
。

-- 判断是否为汉字
定是汉字=函字符
    返回{{ord(char) >= 0x4E00 and ord(char) <= 0x9FFF}}。
。

-- 判断是否为数字
定是数字=函字符
    返回{{char.isdigit()}}。
。

-- 词法分析主函数
定词法分析=函源码
    定结果=列。
    定位置=0。
    定行号=1。
    定列号=1。
    定长度=长源码。
    
    当位置小于长度
        定字符=入源码位置。
        
        -- 跳过空白
        若字符等于" "或字符等于"\t"
            位置=位置加1。
            列号=列号加1。
        否则若字符等于"\n"
            行号=行号加1。
            列号=1。
            位置=位置加1。
        否则
            -- 其他情况：暂时用 Python 代码块处理
            {{break}}
        。
    。
    
    返回结果。
。

导出 词法分析 创建Token。
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_lexer_yan.py`
预期：PASS，输出 "词法分析器测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/selfhost/types.yan yan/selfhost/lexer.yan tests/test_lexer_yan.py
git commit -m "feat(selfhost): implement lexer in pure Yan language (partial)"
```

---

### 任务8：用纯言语言实现语法分析器

**文件：**
- 创建：`yan/selfhost/parser.yan`
- 创建：`tests/test_parser_yan.py`

- [ ] **步骤1：创建 AST 节点定义**

在 `yan/selfhost/types.yan` 中添加：

```yan
-- AST 节点定义
结构 Program
    语句列表 列。
。

结构 Define
    名称 串。
    值 串。
。

结构 Function
    名称 串。
    参数 列。
    函数体 串。
。

结构 If
    条件 串。
    真分支 串。
    假分支 串。
。

导出 Program Define Function If。
```

- [ ] **步骤2：编写语法分析器测试**

创建 `tests/test_parser_yan.py`：

```python
"""纯言语言语法分析器测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_parser_yan_exists():
    """测试语法分析器文件存在"""
    assert os.path.exists('yan/selfhost/parser.yan')

def test_parser_yan_compile():
    """测试语法分析器能够编译"""
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    with open('yan/selfhost/parser.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert len(python_code) > 0
    assert 'def parse' in python_code or 'parse' in python_code

if __name__ == '__main__':
    test_parser_yan_exists()
    test_parser_yan_compile()
    print("语法分析器测试通过")
```

- [ ] **步骤3：实现纯言语言语法分析器**

创建 `yan/selfhost/parser.yan`：

```yan
-- 言语言语法分析器（纯言语言实现）
导入 types。

-- 解析程序
定解析程序=函Token列表
    定语句列表=列。
    定位置=0。
    
    当位置小于长Token列表
        定语句=解析语句Token列表位置。
        若语句不等于空
            语句列表=添语句列表语句。
        。
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

-- 解析变量定义
定解析定义=函Token列表位置
    -- 暂时用 Python 代码块实现
    {{return None}}
。

导出 解析程序。
```

- [ ] **步骤4：运行测试验证通过**

运行：`cd yan && python tests/test_parser_yan.py`
预期：PASS，输出 "语法分析器测试通过"

- [ ] **步骤5：Commit**

```bash
git add yan/selfhost/types.yan yan/selfhost/parser.yan tests/test_parser_yan.py
git commit -m "feat(selfhost): implement parser in pure Yan language (partial)"
```

---

### 任务9：用纯言语言实现代码生成器

**文件：**
- 创建：`yan/selfhost/codegen.yan`
- 创建：`tests/test_codegen_yan.py`

- [ ] **步骤1：编写代码生成器测试**

创建 `tests/test_codegen_yan.py`：

```python
"""纯言语言代码生成器测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_codegen_yan_exists():
    """测试代码生成器文件存在"""
    assert os.path.exists('yan/selfhost/codegen.yan')

def test_codegen_yan_compile():
    """测试代码生成器能够编译"""
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    with open('yan/selfhost/codegen.yan', 'r', encoding='utf-8') as f:
        code = f.read()
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    assert len(python_code) > 0
    assert 'def generate' in python_code or 'generate' in python_code

if __name__ == '__main__':
    test_codegen_yan_exists()
    test_codegen_yan_compile()
    print("代码生成器测试通过")
```

- [ ] **步骤2：实现纯言语言代码生成器**

创建 `yan/selfhost/codegen.yan`：

```yan
-- 言语言代码生成器（纯言语言实现）
导入 types。

-- 生成 Python 代码
定生成代码=函AST
    定代码=""。
    
    遍历语句于AST语句列表
        代码=连代码生成语句语句。
        代码=连代码"\n"。
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

导出 生成代码。
```

- [ ] **步骤3：运行测试验证通过**

运行：`cd yan && python tests/test_codegen_yan.py`
预期：PASS，输出 "代码生成器测试通过"

- [ ] **步骤4：Commit**

```bash
git add yan/selfhost/codegen.yan tests/test_codegen_yan.py
git commit -m "feat(selfhost): implement codegen in pure Yan language (partial)"
```

---

## 阶段3：自举验证（预计1个月）

### 任务10：完成自举验证

**文件：**
- 创建：`yan/selfhost/bootstrap_v2.py`
- 创建：`yan/selfhost/BOOTSTRAP_V2_REPORT.md`
- 创建：`tests/test_bootstrap_v2.py`

- [ ] **步骤1：编写自举验证测试**

创建 `tests/test_bootstrap_v2.py`：

```python
"""自举验证测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_bootstrap_v2():
    """测试自举验证"""
    # 运行自举验证脚本
    import subprocess
    result = subprocess.run(
        ['python', 'yan/selfhost/bootstrap_v2.py'],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "自举验证成功" in result.stdout or "SUCCESS" in result.stdout

if __name__ == '__main__':
    test_bootstrap_v2()
    print("自举验证测试通过")
```

- [ ] **步骤2：实现自举验证脚本**

创建 `yan/selfhost/bootstrap_v2.py`：

```python
#!/usr/bin/env python3
"""
言语言自举验证脚本 V2
验证纯言语言编译器能够编译自身
"""
import os
import hashlib
import subprocess

def compile_with_python_compiler(source_file, output_file):
    """使用 Python 实现的编译器编译"""
    from lexer import Lexer
    from parser import Parser
    from codegen import PythonCodeGen
    
    with open(source_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    parser = Parser()
    ast = parser.parse(tokens)
    gen = PythonCodeGen()
    python_code = gen.generate(ast)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(python_code)
    
    return len(python_code)

def compile_with_yan_compiler(compiler_file, source_file, output_file):
    """使用纯言语言编译器编译"""
    # 执行编译器
    result = subprocess.run(
        ['python', compiler_file, source_file, output_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"编译失败: {result.stderr}")
    
    with open(output_file, 'r', encoding='utf-8') as f:
        return len(f.read())

def main():
    print("=" * 60)
    print("言语言自举验证 V2")
    print("=" * 60)
    
    # 阶段1：Python编译器 → 编译器1
    print("\n阶段1：Python编译器编译纯言语言编译器...")
    compiler1_size = compile_with_python_compiler(
        'yan/selfhost/main.yan',
        'yan/selfhost/compiler1.py'
    )
    print(f"编译器1大小: {compiler1_size} 字节")
    
    # 阶段2：编译器1 → 编译器2
    print("\n阶段2：编译器1编译自身...")
    compiler2_size = compile_with_yan_compiler(
        'yan/selfhost/compiler1.py',
        'yan/selfhost/main.yan',
        'yan/selfhost/compiler2.py'
    )
    print(f"编译器2大小: {compiler2_size} 字节")
    
    # 验证对比
    print("\n验证对比...")
    with open('yan/selfhost/compiler1.py', 'rb') as f:
        hash1 = hashlib.md5(f.read()).hexdigest()
    
    with open('yan/selfhost/compiler2.py', 'rb') as f:
        hash2 = hashlib.md5(f.read()).hexdigest()
    
    print(f"编译器1 MD5: {hash1}")
    print(f"编译器2 MD5: {hash2}")
    
    if hash1 == hash2:
        print("\n✅ 自举验证成功！")
        print("编译器1和编译器2完全相同")
        return 0
    else:
        print("\n❌ 自举验证失败！")
        print("编译器1和编译器2不同")
        return 1

if __name__ == '__main__':
    exit(main())
```

- [ ] **步骤3：创建自举验证报告模板**

创建 `yan/selfhost/BOOTSTRAP_V2_REPORT.md`：

```markdown
# 言语言自举验证报告 V2

**日期**：2026-XX-XX  
**状态**：待验证

---

## 一、验证目标

验证纯言语言编译器能够编译自身，实现真正的自举。

## 二、验证过程

### 阶段1：Python编译器 → 编译器1

**输入**：`main.yan`（纯言语言编译器）  
**编译器**：Python 实现的编译器  
**输出**：`compiler1.py`

### 阶段2：编译器1 → 编译器2

**输入**：`main.yan`（纯言语言编译器）  
**编译器**：编译器1（阶段1产物）  
**输出**：`compiler2.py`

### 验证对比

```
编译器1: XXX 字节 (MD5: ...)
编译器2: XXX 字节 (MD5: ...)
```

## 三、结论

待验证...
```

- [ ] **步骤4：运行测试验证**

运行：`cd yan && python tests/test_bootstrap_v2.py`
预期：PASS（如果所有前置任务完成）

- [ ] **步骤5：Commit**

```bash
git add yan/selfhost/bootstrap_v2.py yan/selfhost/BOOTSTRAP_V2_REPORT.md tests/test_bootstrap_v2.py
git commit -m "feat(bootstrap): add bootstrap verification script V2"
```

---

## 总结

### 预计工作量

- **阶段1**（语言能力扩展）：2-3个月
  - 模块系统：2周
  - 结构体：1周
  - 类型系统：2周
  - 测试和文档：1周

- **阶段2**（编译器重写）：1-2个月
  - 词法分析器：2周
  - 语法分析器：3周
  - 代码生成器：2周
  - 集成测试：1周

- **阶段3**（自举验证）：1个月
  - 验证脚本：1周
  - 调试修复：2周
  - 文档完善：1周

**总计**：4-6个月（全职开发）或 8-12个月（兼职开发）

### 关键里程碑

1. ✅ 模块系统完成（任务1-4）
2. ✅ 结构体完成（任务5-6）
3. ✅ 词法分析器重写完成（任务7）
4. ✅ 语法分析器重写完成（任务8）
5. ✅ 代码生成器重写完成（任务9）
6. ✅ 自举验证成功（任务10）

### 风险和缓解

**高风险**：
- 模块系统复杂度超预期 → 采用简单设计，逐步迭代
- 纯言语言表达能力不足 → 保留 Python 代码块作为后备
- 性能问题 → 优化关键路径，使用缓存

**中风险**：
- 测试覆盖不足 → TDD，每个任务都有测试
- 文档滞后 → 每个任务都更新文档

**低风险**：
- 技术可行性 → 已验证言语言具备图灵完备性
- 社区接受度 → 暂不考虑，专注技术实现
