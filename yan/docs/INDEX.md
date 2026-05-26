# 言语言文档导航

言语言完整文档索引。

## 📚 文档分类

### 入门指南

| 文档 | 说明 |
|------|------|
| [README](../README.md) | 项目主页面 |
| [TUTORIAL](./tutorial/) | 入门教程 |
| [使用指南](./tutorial/01-intro.md) | 语言基础介绍 |

### 语言参考

| 文档 | 说明 |
|------|------|
| [LANGUAGE_SPEC](./LANGUAGE_SPEC.md) | 语言规范 |
| [SYNTAX](./SYNTAX.md) | 语法参考 |
| [内置扩展](./BUILTIN_REFERENCE.md) | 内置函数和扩展 |

### 开发者文档

| 文档 | 说明 |
|------|------|
| [架构文档](./ARCHITECTURE.md) | 编译器架构详解 |
| [API 参考](./API_REFERENCE.md) | 完整 API 参考手册 |
| [工具链](./TOOLCHAIN.md) | LSP、调试器、包管理器 |
| [错误处理](./ERROR_HANDLING_IMPROVEMENT.md) | 错误处理机制 |

### 模块文档

| 文档 | 说明 |
|------|------|
| [模块系统](./MODULE_SYSTEM.md) | 模块导入和热更新 |
| [包管理器](./PACKAGE_MANAGER.md) | 包管理功能 |
| [优化器](./PERFORMANCE_OPTIMIZATION_PLAN.md) | 编译器优化 |
| [标准库](../stdlib/README.md) | 标准库参考 |

### 测试文档

| 文档 | 说明 |
|------|------|
| [测试报告](./TEST_REPORT.md) | 测试覆盖率和结果 |
| [测试框架](./TEST_FRAMEWORK.md) | 测试框架使用指南 |

### 高级主题

| 文档 | 说明 |
|------|------|
| [自举报告](../selfhost/BOOTSTRAP_SUCCESS_REPORT.md) | 自举工作总结 |
| [Bootstrap 现实检查](./BOOTSTRAP_REALITY_CHECK.md) | 自举可行性分析 |
| [工具链](./TOOLCHAIN.md) | 开发工具完整指南 |

---

## 🚀 快速链接

### 新手上路

1. 阅读 [入门教程](./tutorial/01-intro.md)
2. 运行第一个程序
3. 学习语言基础语法

### API 快速查找

需要查找特定 API？请参考：

- [编译器 API](./API_REFERENCE.md#yancompiler)
- [优化器 API](./API_REFERENCE.md#优化器)
- [调试器 API](./API_REFERENCE.md#yandebuggerenhanced)
- [模块系统 API](./API_REFERENCE.md#modulesystem)

### 开发者资源

- [架构概览](./ARCHITECTURE.md#整体架构)
- [核心模块说明](./ARCHITECTURE.md#核心模块)
- [扩展机制](./ARCHITECTURE.md#扩展机制)

---

## 📖 文档贡献指南

### 文档结构

```
docs/
├── ARCHITECTURE.md      # 架构文档
├── API_REFERENCE.md     # API 参考
├── LANGUAGE_SPEC.md     # 语言规范
├── TUTORIAL.md          # 教程目录
└── TEST_REPORT.md       # 测试报告
```

### 文档规范

- 使用中文编写
- 遵循 [中文排版规范](https://github.com/sparanoid/chinese-copywriting-guidelines)
- 代码示例需可运行
- 术语保持一致

### 更新文档

1. Fork 项目仓库
2. 编辑相应文档
3. 提交 Pull Request
4. 等待代码审查

---

## 🔗 相关链接

- [GitHub 仓库](https://github.com/yan-lang/yan)
- [问题反馈](https://github.com/yan-lang/yan/issues)
- [讨论区](https://github.com/yan-lang/yan/discussions)
- [版本历史](../CHANGELOG.md)

---

## 📝 最近更新

### 2026-05-26
- 新增 [架构文档](./ARCHITECTURE.md)
- 新增 [API 参考](./API_REFERENCE.md)
- 更新 [测试报告](./TEST_REPORT.md)
- 完善调试器文档

### 2026-05-25
- 新增性能优化文档
- 完善模块系统文档
- 更新错误处理指南

### 2026-05-24
- 新增调试器功能
- 完善标准库文档
- 更新教程内容
