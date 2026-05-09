# 言语言 ANTLR 实现

## 为什么使用 ANTLR？

### 当前实现的问题

1. **错误处理困难**
   - 手写的递归下降解析器错误信息不友好
   - 难以定位语法错误的具体位置
   - 错误恢复机制不完善

2. **调试复杂**
   - 解析器状态难以追踪
   - 需要手动添加调试代码
   - 缺乏可视化工具

3. **维护成本高**
   - 语法定义分散在代码中
   - 修改语法需要改动多处代码
   - 难以保证一致性

### ANTLR 的优势

1. **清晰的语法定义**
   - 集中在一个 `.g4` 文件中
   - 类似正则表达式的语法，易于理解
   - 支持语法继承和组合

2. **强大的错误处理**
   - 自动生成详细的错误信息
   - 支持错误恢复策略
   - 可以自定义错误处理逻辑

3. **可视化工具**
   - ANTLR Works: 图形化语法编辑器
   - parse-viewer: 可视化解析树
   - IntelliJ 插件: 语法高亮和调试

4. **多语言支持**
   - 可生成 Python, Java, JavaScript, C#, Go 等解析器
   - 同一份语法文件，多种目标语言

5. **成熟的生态系统**
   - 大量现成的语法文件可供参考
   - 活跃的社区支持
   - 丰富的文档和教程

## 安装 ANTLR

### 方法 1: 使用 pip (推荐)

```bash
# 安装 ANTLR 运行时
pip install antlr4-python3-runtime

# 安装 ANTLR 工具
pip install antlr4-tools
```

### 方法 2: 手动安装

```bash
# 下载 ANTLR jar
curl -O https://www.antlr.org/download/antlr-4.13.1-complete.jar

# 添加到 PATH
export CLASSPATH=".:$(pwd)/antlr-4.13.1-complete.jar:$CLASSPATH"

# 创建别名
alias antlr4='java -jar antlr-4.13.1-complete.jar'
```

## 生成解析器

```bash
cd yan/antlr
python generate_parser.py
```

这将生成以下文件：
- `generated/YanLexer.py` - 词法分析器
- `generated/YanParser.py` - 语法分析器
- `generated/YanVisitor.py` - 访问者基类

## 使用示例

### 1. 基本解析

```python
from antlr4 import *
from generated.YanLexer import YanLexer
from generated.YanParser import YanParser

# 输入代码
code = """
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。
印距离3 7。
"""

# 创建词法分析器
input_stream = InputStream(code)
lexer = YanLexer(input_stream)
token_stream = CommonTokenStream(lexer)

# 创建语法分析器
parser = YanParser(token_stream)

# 解析程序
tree = parser.program()

# 打印解析树
print(tree.toStringTree(recog=parser))
```

### 2. 自定义访问者

```python
from generated.YanVisitor import YanVisitor

class MyVisitor(YanVisitor):
    def visitDefineStmt(self, ctx):
        name = ctx.ID().getText()
        print(f"定义: {name}")
        return self.visitChildren(ctx)
    
    def visitFunctionCall(self, ctx):
        func_name = ctx.ID().getText()
        print(f"调用: {func_name}")
        return self.visitChildren(ctx)

# 使用访问者
visitor = MyVisitor()
visitor.visit(tree)
```

### 3. 错误处理

```python
from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"语法错误 (行 {line}, 列 {column}): {msg}")
        print(f"意外的符号: {offendingSymbol.text}")

# 添加错误监听器
parser.removeErrorListeners()
parser.addErrorListener(MyErrorListener())
```

## 语法定义说明

### 词法规则

```
// 关键字
IF: '若';
THEN: '则';
ELSE: '否则';
DEFINE: '定';
FUNC: '函';

// 标识符（汉字序列）
ID: [\u4e00-\u9fa5]+;

// 数字
NUMBER: [0-9]+ ('.' [0-9]+)?;

// 字符串
STRING: '"' ~'"'* '"';
```

### 语法规则

```
// 程序
program: statement* EOF;

// 语句
statement
    : defineStmt
    | exprStmt
    | DOT
    ;

// 定义语句
defineStmt
    : DEFINE ID EQUALS value    # DefineWithKeyword
    | ID EQUALS value           # DefineWithoutKeyword
    ;

// Lambda 表达式
lambda
    : FUNC ID* COLON block      # LambdaWithBlock
    | FUNC ID* expression       # LambdaWithExpr
    ;
```

## 下一步计划

1. **实现完整的访问者**
   - 生成 AST 节点
   - 支持所有语法结构

2. **代码生成器**
   - 从 AST 生成 Python 代码
   - 支持其他目标语言

3. **IDE 支持**
   - VSCode 插件
   - 语法高亮
   - 自动补全

4. **调试工具**
   - 解析树可视化
   - 步骤追踪
   - 变量监视

## 参考资料

- [ANTLR 官方文档](https://www.antlr.org/)
- [ANTLR 4 权威指南](https://pragprog.com/titles/tpantlr2/)
- [ANTLR 语法库](https://github.com/antlr/grammars-v4)
- [Python 目标文档](https://github.com/antlr/antlr4/blob/master/doc/python-target.md)
