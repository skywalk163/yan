# 言语言示例项目库

欢迎来到言语言示例项目库！这里收集了各种难度和类型的示例项目，帮助您快速学习和掌握言语言。

## 📚 项目分类

### 🟢 基础示例（Basic）

适合初学者，展示言语言的基础语法和概念。

| 项目 | 文件 | 说明 | 难度 |
|------|------|------|------|
| Hello World | [basic/hello.yan](basic/hello.yan) | 最简单的程序 | ⭐ |
| 基础运算 | [basic/arithmetic.yan](basic/arithmetic.yan) | 算术运算和表达式 | ⭐ |
| 变量定义 | [basic/variables.yan](basic/variables.yan) | 变量定义和使用 | ⭐ |
| 条件判断 | [basic/conditions.yan](basic/conditions.yan) | if-else条件语句 | ⭐⭐ |
| 循环结构 | [basic/loops.yan](basic/loops.yan) | 遍历循环和当循环 | ⭐⭐ |
| 函数定义 | [basic/functions.yan](basic/functions.yan) | 函数定义和调用 | ⭐⭐ |

### 🟡 中级示例（Intermediate）

展示言语言的进阶特性，包括函数式编程、模块系统等。

| 项目 | 文件 | 说明 | 难度 |
|------|------|------|------|
| 列表操作 | [intermediate/list_operations.yan](intermediate/list_operations.yan) | 列表的创建、操作和高阶函数 | ⭐⭐⭐ |
| 字符串处理 | [intermediate/string_operations.yan](intermediate/string_operations.yan) | 字符串操作和格式化 | ⭐⭐⭐ |
| 高阶函数 | [intermediate/high_order_functions.yan](intermediate/high_order_functions.yan) | map、filter、reduce | ⭐⭐⭐ |
| 递归算法 | [intermediate/recursion.yan](intermediate/recursion.yan) | 递归函数实现 | ⭐⭐⭐ |
| 文件操作 | [intermediate/file_operations.yan](intermediate/file_operations.yan) | 文件读写和目录操作 | ⭐⭐⭐ |
| 模块系统 | [intermediate/modules.yan](intermediate/modules.yan) | 模块导入和导出 | ⭐⭐⭐ |
| JSON处理 | [intermediate/json_processing.yan](intermediate/json_processing.yan) | JSON解析和生成 | ⭐⭐⭐ |
| 计算器 | [intermediate/calculator.yan](intermediate/calculator.yan) | 表达式解析和计算 | ⭐⭐⭐⭐ |

### 🔴 高级示例（Advanced）

展示言语言的高级应用，包括算法实现、数据结构、Web应用等。

| 项目 | 文件 | 说明 | 难度 |
|------|------|------|------|
| 斐波那契数列 | [advanced/fibonacci.yan](advanced/fibonacci.yan) | 多种实现方式对比 | ⭐⭐⭐⭐ |
| 汉诺塔 | [advanced/hanoi.yan](advanced/hanoi.yan) | 经典递归问题 | ⭐⭐⭐⭐ |
| 八皇后问题 | [advanced/8queens.yan](advanced/8queens.yan) | 回溯算法 | ⭐⭐⭐⭐⭐ |
| 图灵机 | [advanced/turing_machine.yan](advanced/turing_machine.yan) | 计算理论模拟 | ⭐⭐⭐⭐⭐ |
| 待办事项 | [advanced/todo.yan](advanced/todo.yan) | 实用应用程序 | ⭐⭐⭐⭐ |
| 词频统计 | [advanced/wordcount.yan](advanced/wordcount.yan) | 文本处理 | ⭐⭐⭐⭐ |
| 网络请求 | [advanced/web_request.yan](advanced/web_request.yan) | HTTP请求处理 | ⭐⭐⭐⭐ |
| 猜数字游戏 | [advanced/guess_number.yan](advanced/guess_number.yan) | 交互式游戏 | ⭐⭐⭐⭐ |

## 🚀 快速开始

### 运行示例

```bash
# 进入项目根目录
cd newlisp

# 运行基础示例
python main.py yan/examples-gallery/basic/hello.yan

# 运行中级示例
python main.py yan/examples-gallery/intermediate/calculator.yan

# 运行高级示例
python main.py yan/examples-gallery/advanced/fibonacci.yan
```

### 在VS Code中运行

1. 安装言语言VS Code插件
2. 打开 `.yan` 文件
3. 右键选择"言语言：运行当前文件"

## 📖 学习路径

### 初学者路径（1-2周）

1. **第1天：** Hello World → 基础运算 → 变量定义
2. **第2-3天：** 条件判断 → 循环结构
3. **第4-5天：** 函数定义 → 列表操作
4. **第6-7天：** 字符串处理 → 高阶函数
5. **第2周：** 完成所有基础和中级示例

### 进阶路径（2-3周）

1. **第1周：** 递归算法 → 文件操作 → 模块系统
2. **第2周：** JSON处理 → 计算器 → 词频统计
3. **第3周：** 斐波那契 → 汉诺塔 → 八皇后

### 实战路径（持续）

- 待办事项管理器
- 网络请求应用
- 图灵机模拟
- 自己的项目想法！

## 🎯 项目目标

每个示例项目都旨在：

1. **教学性** - 清晰展示特定概念或技术
2. **实用性** - 解决实际问题或演示实用功能
3. **渐进性** - 从简单到复杂，循序渐进
4. **完整性** - 包含注释、错误处理和完整逻辑

## 🤝 贡献示例

欢迎贡献新的示例项目！

### 贡献指南

1. 选择合适的难度级别（basic/intermediate/advanced）
2. 遵循命名规范：`功能描述.yan`
3. 添加详细注释（使用 `注` 关键字）
4. 确保代码可以运行
5. 更新本README文件

### 示例模板

```yan
注 项目名称 - 简短描述
注 作者：您的名字
注 难度：⭐⭐⭐

导入 标准库模块。

定 主函数 = 函 参数
  注 函数说明
  定 结果 = 处理 参数。
  返回 结果。
。

印 主函数 输入。
```

## 📊 统计信息

- **总示例数：** 32个
- **基础示例：** 6个
- **中级示例：** 8个
- **高级示例：** 8个
- **总代码行数：** ~800行

## 🔗 相关资源

- [语言规范](../docs/LANGUAGE_SPEC.md)
- [入门教程](../docs/TUTORIAL.md)
- [内置函数参考](../docs/BUILTIN_REFERENCE.md)
- [VS Code插件](../vscode-extension/README.md)

## 📝 更新日志

- **2026-05-18：** 创建示例项目库，整理32个示例
- **2026-05-16：** 自举成功，新增多个高级示例
- **2026-05-05：** 添加标准库示例（JSON、网络、文件）

---

**Happy Coding with 言语言！** 🎉
