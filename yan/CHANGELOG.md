# 言语言 changelog

所有重要的言语言项目更改都将记录在此文件中。

## [未发布] - 开发中

### 新增

- `pytest.ini` - pytest 配置文件，配置测试路径和忽略文件
- `yan_test.py` - 言语言测试框架核心模块
  - 新增 `YanTestFramework` 类 - 测试框架
  - 新增 `YanTestReport` 类 - 测试报告
  - 新增断言函数：`等`、`为真`、`为假`、`引发异常`
  - 新增装饰器：`suite`、`test`
- `yan_assertions.py` - 言语言断言库
  - 新增 `断言等`、`断言包含`、`断言为真`、`断言为假` 函数

### 修改

- `parser.py` - 语法分析器
  - 修复了中缀动词延续问题，支持 `盘子数减1` 正确解析为 `减(盘子数, 1)`
  - 添加了高阶函数管道操作支持（`皆`、`只`、`归`）
  - 恢复原始解析器代码，修复了函数调用解析问题

- `codegen.py` - 代码生成器
  - 移除了条件语句和函数体中自动添加的 `return` 关键字
  - 修复了汉诺塔等递归函数的正确执行

- `main.py` - 主入口
  - 修复了执行逻辑，避免重复执行函数调用
  - 不再 eval 包含函数调用的行

- `tests/test_smart_block.py` - 智能块测试
  - 修复了 `test_nested_loops` 测试用例以适应 Block 结构

- `tests/test_collections.py` - 集合测试
  - 添加了正确的 sys.path 设置

## [0.1.0] - 2026-05-17

### 新增

- 词法分析器 (`lexer.py`)
- 语法分析器 (`parser.py`)
- 代码生成器 (`codegen.py`)
- 运行时函数 (`runtime.py`)
- 错误处理 (`error.py`, `error_formatter.py`, `error_suggestions.py`)
- 测试框架 (`tests/`)
- VS Code 扩展 (`vscode-extension/`)

### 示例

- 汉诺塔 (`examples/hanoi_full.yan`)
- 基本运算 (`examples/basic.yan`)
- 阶乘 (`examples/factorial.yan`)

---

**更新日期**：2026-05-18
