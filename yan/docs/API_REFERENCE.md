# 言语言 API 参考文档

本文档提供言语言编译器核心模块的完整 API 参考。

## 编译器核心

### YanCompiler

言语言主编译器类。

**模块位置：** `yan/codegen.py`

```python
from yan import YanCompiler

compiler = YanCompiler()
result = compiler.compile("输出 \"你好\"")
print(result)
```

**构造函数：**

```python
def __init__(self, optimize_level: str = "O1")
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `optimize_level` | `str` | `"O1"` | 优化级别，可选 `O0`、`O1`、`O2`、`Os` |

**方法：**

#### compile(source: str) -> str

编译源代码并返回生成的 Python 代码。

```python
source = """
函数 加法(甲, 乙)
    返回 甲 + 乙
结束

输出 加法(1, 2)
"""

result = compiler.compile(source)
print(result)
# 输出 Python 代码
```

#### compile_file(path: str) -> str

编译文件并返回生成的 Python 代码。

```python
result = compiler.compile_file("主.yan")
```

#### execute(source: str) -> Any

编译并执行源代码。

```python
result = compiler.execute("输出 1 + 2")
# 输出: 3
```

#### execute_file(path: str) -> Any

编译并执行文件。

```python
result = compiler.execute_file("主.yan")
```

---

### Lexer

词法分析器，将源代码转换为 Token 序列。

**模块位置：** `yan/lexer.py`

```python
from yan.lexer import Lexer

lexer = Lexer()
tokens = lexer.tokenize("输出 \"你好\"")
for token in tokens:
    print(token)
```

**构造函数：**

```python
def __init__(self, source: str = "")
```

**方法：**

#### tokenize(source: str) -> List[Token]

对源代码进行词法分析。

```python
tokens = lexer.tokenize("变量 x = 10")
```

#### next_token() -> Token

获取下一个 Token。

#### peek() -> Token

预览下一个 Token（不消耗）。

#### reset()

重置分析器状态。

---

### Parser

语法解析器，将 Token 序列转换为 AST。

**模块位置：** `yan/parser.py`

```python
from yan.parser import Parser
from yan.lexer import Lexer

lexer = Lexer("变量 x = 10")
parser = Parser(lexer)
ast = parser.parse()
```

**构造函数：**

```python
def __init__(self, lexer: Lexer)
```

**方法：**

#### parse() -> ProgramNode

解析 Token 序列生成 AST。

#### parse_expression() -> ExpressionNode

解析表达式。

---

## AST 节点

### ASTNode

所有 AST 节点的基类。

**模块位置：** `yan/nodes.py`

```python
from yan.nodes import ASTNode

class ASTNode:
    def accept(self, visitor: 'ASTVisitor') -> Any:
        """接受访问者"""
        pass
    
    def __repr__(self) -> str:
        """返回节点描述"""
        pass
```

### ProgramNode

程序根节点。

```python
from yan.nodes import ProgramNode

node = ProgramNode()
node.statements = []  # 语句列表
```

**属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `statements` | `List[StatementNode]` | 语句列表 |
| `source_file` | `str` | 源文件路径 |

### FunctionNode

函数定义节点。

```python
from yan.nodes import FunctionNode

node = FunctionNode(
    name="加法",
    params=["甲", "乙"],
    body=[...],
    return_type=None
)
```

**属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 函数名 |
| `params` | `List[str]` | 参数列表 |
| `body` | `List[StatementNode]` | 函数体 |
| `return_type` | `Optional[str]` | 返回类型 |

### CallNode

函数调用节点。

```python
from yan.nodes import CallNode

node = CallNode(
    callee="输出",
    arguments=[LiteralNode(42)]
)
```

**属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `callee` | `str` | 函数名 |
| `arguments` | `List[ExpressionNode]` | 参数列表 |

### IfNode

条件语句节点。

```python
from yan.nodes import IfNode

node = IfNode(
    condition=BinaryOpNode(">", IdentifierNode("x"), LiteralNode(10)),
    then_branch=[...],
    else_branch=[...]
)
```

**属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `condition` | `ExpressionNode` | 条件表达式 |
| `then_branch` | `List[StatementNode]` | 条件为真时执行 |
| `else_branch` | `Optional[List[StatementNode]]` | 条件为假时执行 |

### LoopNode

循环语句节点。

```python
from yan.nodes import LoopNode

node = LoopNode(
    variable="i",
    start=LiteralNode(0),
    end=LiteralNode(10),
    body=[...]
)
```

**属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `str` | 循环类型 (`for`/`while`) |
| `condition` | `Optional[ExpressionNode]` | 循环条件（while） |
| `variable` | `Optional[str]` | 循环变量（for） |
| `start` | `Optional[ExpressionNode]` | 起始值（for） |
| `end` | `Optional[ExpressionNode]` | 结束值（for） |
| `body` | `List[StatementNode]` | 循环体 |

### BinaryOpNode

二元运算节点。

```python
from yan.nodes import BinaryOpNode

node = BinaryOpNode(
    operator="+",
    left=IdentifierNode("甲"),
    right=LiteralNode(1)
)
```

**属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `operator` | `str` | 运算符 |
| `left` | `ExpressionNode` | 左操作数 |
| `right` | `ExpressionNode` | 右操作数 |

### LiteralNode

字面量节点。

```python
from yan.nodes import LiteralNode

# 数字
num = LiteralNode(42)

# 字符串
text = LiteralNode("你好")

# 布尔值
flag = LiteralNode(True)

# 列表
arr = LiteralNode([1, 2, 3])
```

### IdentifierNode

标识符节点。

```python
from yan.nodes import IdentifierNode

node = IdentifierNode("变量名")
```

**属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 标识符名称 |

---

## 优化器

### Optimizer

主优化器类。

**模块位置：** `yan/optimizer/optimizer.py`

```python
from yan.optimizer import Optimizer

optimizer = Optimizer(level="O2")
optimized_ast = optimizer.optimize(ast)
```

**构造函数：**

```python
def __init__(self, level: str = "O1")
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `level` | `str` | `"O1"` | 优化级别 |

**优化级别：**

| 级别 | 启用优化 |
|------|----------|
| `O0` | 无优化 |
| `O1` | 常量折叠、死代码消除 |
| `O2` | +表达式简化、尾递归优化 |
| `Os` | 空间优化 |

**方法：**

#### optimize(node: ASTNode) -> ASTNode

对 AST 进行优化。

```python
optimized = optimizer.optimize(ast)
```

#### set_strategy(strategy: OptimizationStrategy)

设置优化策略。

```python
from yan.optimizer import ConstantFolding

optimizer.set_strategy(ConstantFolding())
```

---

### OptimizationStrategy

优化策略接口。

**模块位置：** `yan/optimizer/strategy.py`

```python
from yan.optimizer.strategy import OptimizationStrategy

class MyOptimization(OptimizationStrategy):
    @property
    def name(self) -> str:
        return "my_optimization"
    
    def can_apply(self, node: ASTNode) -> bool:
        # 检查是否适用
        pass
    
    def apply(self, node: ASTNode) -> ASTNode:
        # 应用优化
        pass
```

### 常量折叠 (Constant Folding)

**模块位置：** `yan/optimizer/optimizations/constant_folding.py`

```python
from yan.optimizer.optimizations import ConstantFolding

optimizer = ConstantFolding()
optimized = optimizer.optimize(ast)
```

将编译时可计算的常量表达式直接求值。

```yan
# 优化前
变量 x = 1 + 2 + 3

# 优化后
变量 x = 6
```

### 死代码消除 (Dead Code Elimination)

**模块位置：** `yan/optimizer/optimizations/dead_code_elimination.py`

```python
from yan.optimizer.optimizations import DeadCodeElimination

optimizer = DeadCodeElimination()
optimized = optimizer.optimize(ast)
```

移除不可达代码和无用赋值。

```yan
# 优化前
如果 假 则
    输出 "永不执行"
结束

# 优化后
# (整个 if 语句被移除)
```

### 表达式简化 (Expression Simplification)

**模块位置：** `yan/optimizer/optimizations/expression_simplification.py`

```python
from yan.optimizer.optimizations import ExpressionSimplification

optimizer = ExpressionSimplification()
optimized = optimizer.optimize(ast)
```

代数化简表达式。

```yan
# 优化前
变量 x = a * 1 + 0

# 优化后
变量 x = a
```

### 尾递归优化 (Tail Recursion Optimization)

**模块位置：** `yan/optimizer/optimizations/tail_recursion_optimization.py`

```python
from yan.optimizer.optimizations import TailRecursionOptimization

optimizer = TailRecursionOptimization()
optimized = optimizer.optimize(ast)
```

将尾递归转换为循环。

```yan
# 优化前
函数 阶乘(n, acc)
    如果 n == 0 则
        返回 acc
    否则
        返回 阶乘(n - 1, n * acc)
    结束
结束

# 优化后 (转换为循环)
函数 阶乘(n, acc)
    循环 当 n > 0
        acc = n * acc
        n = n - 1
    结束
    返回 acc
结束
```

---

## 模块系统

### ModuleSystem

模块系统，支持模块导入和热更新。

**模块位置：** `yan/module_system.py`

```python
from yan.module_system import ModuleSystem

system = ModuleSystem()
module = system.import_module("math")
```

**构造函数：**

```python
def __init__(self, search_paths: List[str] = None)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `search_paths` | `List[str]` | `None` | 模块搜索路径 |

**方法：**

#### import_module(name: str) -> ModuleInfo

导入模块。

```python
module = system.import_module("json")
```

#### reload_module(name: str) -> ModuleInfo

重新加载模块。

```python
system.reload_module("json")
```

#### get_module_info(name: str) -> Optional[ModuleInfo]

获取模块信息。

```python
info = system.get_module_info("json")
print(info.version)
```

#### list_modules() -> List[str]

列出已加载模块。

```python
modules = system.list_modules()
```

### ModuleInfo

模块信息数据结构。

```python
from yan.module_system import ModuleInfo

@dataclass
class ModuleInfo:
    name: str
    version: str
    path: str
    exports: Dict[str, Any]
    dependencies: List[str]
    loaded_at: datetime
    hot_reload: bool
```

---

## 包管理器

### YanPackageManager

言语言包管理器。

**模块位置：** `yan/yan_package_manager.py`

```python
from yan.yan_package_manager import YanPackageManager

manager = YanPackageManager()
result = manager.install("json")
```

**构造函数：**

```python
def __init__(self, registry_url: str = None)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `registry_url` | `str` | `None` | 包注册中心 URL |

**方法：**

#### install(package: str, version: str = None) -> PackageInfo

安装包。

```python
info = manager.install("json", "^1.0.0")
```

#### uninstall(package: str) -> bool

卸载包。

```python
manager.uninstall("json")
```

#### update(package: str = None) -> List[PackageInfo]

更新包。

```python
# 更新所有
updates = manager.update()

# 更新指定包
updates = manager.update("json")
```

#### search(query: str) -> List[PackageInfo]

搜索包。

```python
results = manager.search("json")
for pkg in results:
    print(f"{pkg.name}@{pkg.version}")
```

#### list_installed() -> List[PackageInfo]

列出已安装包。

```python
installed = manager.list_installed()
```

### PackageInfo

包信息数据结构。

```python
@dataclass
class PackageInfo:
    name: str
    version: str
    description: str
    author: str
    dependencies: Dict[str, str]
    path: str
```

---

## 调试器

### YanDebuggerEnhanced

增强版调试器。

**模块位置：** `yan/debugger_enhanced.py`

```python
from yan.debugger_enhanced import YanDebuggerEnhanced

debugger = YanDebuggerEnhanced()
debugger.set_breakpoint(10, "主.yan")
debugger.start()
```

**方法：**

#### set_breakpoint(line, file, condition, hit_condition, log_message) -> Breakpoint

设置断点。

```python
# 基础断点
bp = debugger.set_breakpoint(10, "主.yan")

# 条件断点
bp = debugger.set_breakpoint(15, "主.yan", condition="x > 10")

# 命中条件断点
bp = debugger.set_breakpoint(20, "主.yan", hit_condition="hitCount > 5")

# 日志点
bp = debugger.set_breakpoint(25, "主.yan", log_message="x = {x}")
```

#### remove_breakpoint(line, file) -> bool

移除断点。

```python
debugger.remove_breakpoint(10, "主.yan")
```

#### clear_breakpoints()

清除所有断点。

```python
debugger.clear_breakpoints()
```

#### step_into()

单步进入。

```python
debugger.step_into()
```

#### step_over()

单步跳过。

```python
debugger.step_over()
```

#### step_out()

单步跳出。

```python
debugger.step_out()
```

#### resume()

继续执行。

```python
debugger.resume()
```

#### pause()

暂停执行。

```python
debugger.pause()
```

#### add_watch_expression(expression: str) -> WatchExpression

添加监视表达式。

```python
watch = debugger.add_watch_expression("x + y")
print(f"当前值: {watch.value}")
```

#### evaluate_expression(expr: str) -> Any

计算表达式。

```python
result = debugger.evaluate_expression("x * 2 + 1")
```

#### get_call_stack() -> List[Frame]

获取调用栈。

```python
stack = debugger.get_call_stack()
for frame in stack:
    print(f"{frame.name} at line {frame.line}")
```

#### get_variables(scope: str) -> List[VariableInfo]

获取变量列表。

```python
# 获取局部变量
locals = debugger.get_variables("local")

# 获取全局变量
globals = debugger.get_variables("global")
```

### Breakpoint

断点数据结构。

```python
@dataclass
class Breakpoint:
    id: str
    line: int
    file: str
    condition: Optional[str] = None
    hit_condition: Optional[str] = None
    log_message: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0
    verified: bool = False
```

### WatchExpression

监视表达式数据结构。

```python
@dataclass
class WatchExpression:
    id: str
    expression: str
    value: Any = None
    type_name: str = ""
    enabled: bool = True
    error: Optional[str] = None
```

### Frame

调用栈帧数据结构。

```python
@dataclass
class Frame:
    id: int
    name: str
    line: int
    column: int = 0
    file: str = ""
    scope_variables: Dict[str, Any] = field(default_factory=dict)
```

---

## 错误处理

### ErrorRecovery

错误恢复管理器。

**模块位置：** `yan/error_recovery.py`

```python
from yan.error_recovery import ErrorRecovery, RecoveryStrategy

recovery = ErrorRecovery()
recovery.set_strategy(RecoveryStrategy.INSERT_MISSING_TOKEN)
```

**方法：**

#### recover(error: CompileError) -> RecoveryAction

尝试恢复错误。

```python
action = recovery.recover(error)
if action.success:
    print(f"已恢复: {action.description}")
```

#### add_strategy(strategy: RecoveryStrategy)

添加恢复策略。

```python
recovery.add_strategy(RecoveryStrategy.SKIP_STATEMENT)
```

### SmartErrorSuggester

智能错误建议器。

**模块位置：** `yan/smart_error_suggestor.py`

```python
from yan.smart_error_suggestor import SmartErrorSuggester

suggester = SmartErrorSuggester()
suggestions = suggester.suggest(error)
```

**方法：**

#### suggest(error: Error) -> List[Suggestion]

获取错误建议。

```python
suggestions = suggester.suggest(error)
for s in suggestions:
    print(f"{s.type}: {s.message}")
    if s.fix:
        print(f"修复: {s.fix}")
```

#### add_pattern(pattern: str, handler: Callable)

添加错误模式。

```python
def handle_custom_error(error):
    return [Suggestion(type="fix", message="...", fix="...")]

suggester.add_pattern(r"未定义的标识符.*", handle_custom_error)
```

### Suggestion

建议数据结构。

```python
@dataclass
class Suggestion:
    type: SuggestionType  # suggestion/fix/reference/example
    message: str
    confidence: float = 0.8
    fix: Optional[str] = None
    code: Optional[str] = None
    reference: Optional[str] = None
```

---

## 运行时

### Runtime

运行时环境。

**模块位置：** `yan/runtime.py`

```python
from yan.runtime import Runtime

runtime = Runtime()
result = runtime.execute(code)
```

**方法：**

#### execute(code: str) -> Any

执行代码。

```python
result = runtime.execute("1 + 2")
```

#### set_global(name: str, value: Any)

设置全局变量。

```python
runtime.set_global("PI", 3.14159)
```

#### get_global(name: str) -> Any

获取全局变量。

```python
pi = runtime.get_global("PI")
```

---

## 工具函数

### error_formatter

错误消息格式化。

**模块位置：** `yan/error_formatter.py`

```python
from yan.error_formatter import ErrorFormatter

formatter = ErrorFormatter()
output = formatter.format(error)
print(output)
```

### yan_fmt

代码格式化工具。

**模块位置：** `yan/yan_fmt.py`

```python
from yan.yan_fmt import format_code

formatted = format_code(source)
```

---

## 常量

### 优化级别

```python
from yan.optimizer import OptimizationLevel

OptimizationLevel.O0  # 无优化
OptimizationLevel.O1  # 基础优化
OptimizationLevel.O2  # 高级优化
OptimizationLevel.Os # 空间优化
```

### 调试状态

```python
from yan.debugger_enhanced import DebugState

DebugState.STOPPED    # 已停止
DebugState.RUNNING    # 运行中
DebugState.PAUSED     # 已暂停
DebugState.STEPPING   # 步进中
DebugState.BREAKPOINT # 断点命中
```

### 步进模式

```python
from yan.debugger_enhanced import StepMode

StepMode.NONE       # 无
StepMode.STEP_INTO  # 单步进入
StepMode.STEP_OVER  # 单步跳过
StepMode.STEP_OUT   # 单步跳出
```

### 恢复策略

```python
from yan.error_recovery import RecoveryStrategy

RecoveryStrategy.INSERT_MISSING_TOKEN     # 插入缺失令牌
RecoveryStrategy.REPLACE_INVALID_TOKEN    # 替换无效令牌
RecoveryStrategy.SKIP_STATEMENT           # 跳过语句
RecoveryStrategy.CONTINUE_AFTER_ERROR     # 错误后继续
```

---

## 异常

### YanError

言语言基础异常。

```python
from yan.error import YanError

raise YanError("编译错误")
```

### LexerError

词法分析错误。

```python
from yan.error import LexerError

raise LexerError("非法字符", line=10, column=5)
```

### ParserError

语法解析错误。

```python
from yan.error import ParserError

raise ParserError("语法错误", token=current_token)
```

### SemanticError

语义分析错误。

```python
from yan.error import SemanticError

raise SemanticError("类型不匹配", node=node)
```

---

## 示例

### 完整编译流程

```python
from yan import YanCompiler
from yan.optimizer import Optimizer
from yan.debugger_enhanced import YanDebuggerEnhanced

# 创建编译器
compiler = YanCompiler(optimize_level="O2")

# 创建调试器
debugger = YanDebuggerEnhanced()

# 设置断点
debugger.set_breakpoint(10, "主.yan")

# 源代码
source = """
函数 阶乘(n)
    如果 n <= 1 则
        返回 1
    否则
        返回 n * 阶乘(n - 1)
    结束
结束

输出 阶乘(5)
"""

# 编译
result = compiler.compile(source)
print("生成的 Python 代码:")
print(result)

# 执行
print("\n执行结果:")
compiler.execute(source)
```

### 使用模块系统

```python
from yan.module_system import ModuleSystem

system = ModuleSystem(search_paths=["./modules", "./stdlib"])

# 导入模块
math_module = system.import_module("math")

# 使用模块
result = system.execute_module_func("math", "sin", [3.14159 / 2])

# 启用热更新
system.enable_hot_reload(True)

# 重新加载
system.reload_module("math")
```

### 调试会话

```python
from yan.debugger_enhanced import YanDebuggerEnhanced

debugger = YanDebuggerEnhanced()

# 设置断点
debugger.set_breakpoint(5, "test.yan", condition="x > 10")

# 添加监视
debugger.add_watch_expression("x * y")
debugger.add_watch_expression("sum(x for x in range(10))")

# 开始调试
debugger.start()

# 在断点处检查
print(f"调用栈: {debugger.get_call_stack()}")
print(f"变量: {debugger.get_variables('local')}")

# 单步执行
debugger.step_over()

# 修改变量
debugger.set_variable("x", 100)

# 继续执行
debugger.resume()
```

---

## 相关文档

- [架构文档](./ARCHITECTURE.md)
- [语言规范](./LANGUAGE_SPEC.md)
- [使用教程](./TUTORIAL.md)
