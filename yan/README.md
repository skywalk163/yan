# 言 (Yán) — 中文函数式编程语言

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/skywalk163/yan)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-green.svg)](https://github.com/skywalk163/yan)

一门以中文为语法核心的函数式编程语言，转译到 Python 执行。

## 特性

- **中文语法** — 用中文写代码，自然流畅
- **无空格分词** — 汉字连续书写，自动断词
- **管道操作** — 数据流动，`，` 连接
- **双轨设计** — 中文负责逻辑，`$()` 数学表达式，`{{}}` Python 代码
- **块结构** — 函数支持多语句、局部变量
- **Python 生态** — 可直接调用 Python 库
- **智能错误提示** — 源代码片段、位置高亮、智能建议
- **性能优化** — Token缓存、惰性列表、流式处理

## 快速开始

```bash
# 进入 yan 目录
cd yan

# 运行文件
python main.py examples/basic.yan

# 交互式环境
python main.py

# 调试模式
python main.py examples/factorial.yan --debug
```

## 示例

### 基本运算

```
印10加5，乘2。        -- 30
印列1 2 3，首。       -- 1
```

### 函数定义

```
定平方=函x乘x x。
印平方5。             -- 25
```

### 块结构

```
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。
印距离3 7。           -- 4
```

### 递归

```
定阶乘=函n若n等1则1否则n乘阶乘n减1。
印阶乘5。             -- 120
```

### 双轨制语法

```
定面积=$(3.14 * r * r)。
定数据={{import numpy as np; np.array([1, 2, 3])}}。
```

### 引用（Quote）

```
'加1 2。              -- 返回 AST，不执行
```

### 错误提示

```
错误：未定义的变量
  文件：demo.yan
  位置：第 3 行，第 5-8 列

    1 | 定 数据 = 列 1 2 3。
    2 | 定 平方 = 函 x 乘 x x。
    3 | 定 值 = 皆 平方 数据x。
                              ^^^^
                              未定义的变量：数据x
                              您是否想使用：数据？

建议：检查变量名拼写，或确认变量已定义。
```

### 性能优化

```
-- 惰性列表（延迟计算）
定 大数据 = 惰性列表 1 1000000。
定 平方 = 函 x 乘 x x。
定 结果 = 皆 平方 大数据。  -- 不立即计算

-- 流式处理
大数据，过滤大10，映射平方，取首10。
```

## 项目结构

```
yan/
├── lexer.py              # 词法分析
├── parser.py             # 语法分析
├── codegen.py            # Python 代码生成
├── nodes.py              # AST 节点定义
├── runtime.py            # 运行时函数
├── main.py               # 入口
├── test.py               # 测试用例
├── error_types.py        # 错误分类系统
├── error_context.py      # 上下文感知错误
├── error_messages.py     # 错误消息模板
├── error_suggestions_v2.py # 智能建议引擎
├── lexer_optimized.py    # 词法分析器优化版
├── list_optimized.py     # 惰性列表实现
├── docs/
│   ├── SYNTAX.md         # 语法手册
│   ├── LANGUAGE_SPEC.md  # 语言规范
│   └── ERROR_FORMAT_SPEC.md # 错误格式规范
└── examples/             # 示例代码
```

## 文档

### 教程
- [入门教程（第1章）](docs/tutorial/01-intro.md) — 环境搭建和第一个程序
- [入门教程（第2章）](docs/tutorial/02-basics.md) — 基础语法
- [入门教程（第3章）](docs/tutorial/03-functional.md) — 函数式编程
- [入门教程（第4章）](docs/tutorial/04-modules.md) — 模块系统
- [入门教程（第5章）](docs/tutorial/05-project.md) — 综合实战
- [进阶教程（第6章）](docs/tutorial/06-advanced.md) — 高阶函数、闭包、递归
- [进阶教程（第7章）](docs/tutorial/07-stdlib.md) — 标准库深度解析
- [进阶教程（第8章）](docs/tutorial/08-project.md) — 项目实战
- [进阶教程（第9章）](docs/tutorial/09-best-practices.md) — 最佳实践
- [进阶教程（第10章）](docs/tutorial/10-deployment.md) — 部署与发布

### 参考
- [语法手册](docs/SYNTAX.md) — 语言语法规范
- [语言规范](docs/LANGUAGE_SPEC.md) — 完整语言规范
- [错误格式规范](docs/ERROR_FORMAT_SPEC.md) — 错误处理规范
- [CHANGELOG](CHANGELOG.md) — 版本变更记录

## 核心概念

### 动词吞噬

动词根据参数数量自动收集参数：

```
加1 2 3。            -- 6，加吞噬 1, 2, 3
列1 2 3。            -- [1, 2, 3]，列吞噬所有参数
```

### 管道

用 `，` 连接操作，前一步的结果传给后一步：

```
10加5，乘2，减3。    -- ((10 + 5) * 2) - 3 = 27
```

### 高阶函数

```
列1 2 3，皆乘2。     -- [2, 4, 6]（map）
列1 2 3 4 5，只大2。 -- [3, 4, 5]（filter）
列1 2 3，归加0。     -- 6（reduce）
```

### 测试框架

言语言提供完整的测试框架，支持断言、发现和覆盖率统计：

```
-- 断言函数示例
断言等 加 1 2 3。
断言大 5 3。
断言包含 列 1 2 3 2。
断言串包含 "hello world" "world"。

-- 测试套件
套 "数学运算测试"：
  测 "加法运算"：
    断言等 加 1 2 3。
  。
  
  测 "列表映射"：
    定 数据 = 列 1 2 3。
    定 平方 = 函 x 乘 x x。
    断言等 皆 平方 数据 列 1 4 9。
  。
。

-- 代码覆盖率
覆盖率统计：
  行覆盖率：95%
  分支覆盖率：87%
  函数覆盖率：100%
```

**断言函数库（40+函数）：**
- 基础断言：等、不等、为真、为假、为空、不为空
- 比较断言：大于、小于、大于等于、小于等于
- 类型断言：是数、是串、是表、是字典、是函
- 异常断言：引发异常、不引发异常
- 集合断言：包含、不包含、包含所有
- 字符串断言：串包含、串开始于、串匹配
- 列表断言：列表长度、列表为空、列表相等
- 字典断言：字典包含键、字典相等
- 组合断言：全部通过、任意通过

### 标准库

言语言提供完整的标准库，涵盖网络、数据处理、加密等常用功能：

**网络模块（net）：**
```
-- HTTP 请求
定 响应 = 请求 "https://api.example.com/data"。
定 内容 = 响应.内容。

-- 文件下载
下载 "https://example.com/file.zip" "本地文件.zip"。

-- 文件上传
上传 "https://api.example.com/upload" "文件路径"。
```

**JSON 模块：**
```
-- JSON 编码
定 数据 = 典 "name" "张三" "age" 25。
定 JSON串 = 编码 数据。

-- JSON 解码
定 解析数据 = 解码 JSON串。
印 解析数据.name。
```

**正则模块（regex）：**
```
-- 模式匹配
定 文本 = "邮箱：test@example.com"。
定 结果 = 匹配 文本 "\\w+@\\w+\\.\\w+"。
印 结果.组0。

-- 替换
定 新文本 = 替换 文本 "\\d+" "数字"。

-- 分割
定 列表 = 分割 "a,b,c" ","。
```

**日期模块（datetime）：**
```
-- 当前时间
定 现在 = 当前时间。
印 格式化 现在 "%Y-%m-%d %H:%M:%S"。

-- 日期计算
定 明天 = 加天数 现在 1。
定 差值 = 日期差 现在 明天。

-- 解析日期
定 日期 = 解析日期 "2026-05-18" "%Y-%m-%d"。
```

**加密模块（crypto）：**
```
-- 哈希
定 哈希值 = 哈希 "password" "sha256"。

-- Base64 编码
定 编码串 = 编码Base64 "Hello"。
定 原文 = 解码Base64 编码串。

-- 对称加密
定 密文 = 加密 "敏感数据" "密钥"。
定 明文 = 解密 密文 "密钥"。
```

**数据库模块（database）：**
```
-- 连接数据库
定 连接 = 连接数据库 "sqlite:///test.db"。

-- 执行查询
定 结果 = 查询 连接 "SELECT * FROM users WHERE age > ?" 列 18。

-- 执行更新
执行 连接 "INSERT INTO users (name, age) VALUES (?, ?)" 列 "张三" 25。

-- 事务
开始事务 连接。
执行 连接 "UPDATE accounts SET balance = balance - 100"。
执行 连接 "UPDATE accounts SET balance = balance + 100"。
提交 连接。
```

**标准库统计：**
- 总模块数：11个（collections、io、math、time、string、net、json、regex、datetime、crypto、database）
- 总函数数：~120个
- 覆盖领域：数据处理、网络通信、加密安全、数据库访问

## 运行测试

```bash
cd yan
python test.py
```

## 许可证

MIT

## 致谢

本项目在开发过程中使用了 AI 辅助编程，特别感谢：

- **[Trae](https://trae.ai/)** — 提供智能代码补全、错误诊断和重构建议
- **Duamte** — 协助代码审查和功能实现

AI 助手在语法解析、错误处理、性能优化等方面提供了宝贵的建议，帮助项目不断完善。
