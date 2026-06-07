# 言语言工具链

言语言提供完整的开发工具链，包括 LSP 语言服务器、调试器和包管理器。

## 🔧 工具列表

1. **yan_lsp.py** - LSP 语言服务器，提供智能编码支持
2. **yan_debugger.py** - 调试器，用于调试言语言程序
3. **yan_pkg.py** - 包管理器，用于管理言语言包

---

## 📘 LSP 语言服务器

言语言的 LSP (Language Server Protocol) 服务器，为编辑器提供完整的语言支持。

### 功能特性

- ✅ 语法高亮（语义着色）
- ✅ 代码自动补全（内置函数 + 用户定义）
- ✅ 悬停提示（函数文档）
- ✅ 错误诊断（实时语法检查）
- ✅ 文档符号（变量/函数定义）
- ✅ 查找引用
- ✅ 重命名重构
- ✅ 代码格式化（规划中）

### 使用方式

#### VSCode 扩展

安装言语言 VSCode 扩展后会自动启用 LSP 功能。

#### 手动启动

```bash
python yan_lsp.py
```

### 配置

在项目根目录创建 `.yan.json` 配置文件：

```json
{
  "name": "my-project",
  "version": "0.1.0",
  "entry": "主.yan",
  "test": "tests/",
  "lsp": {
    "enable": true,
    "diagnostics": {
      "enable": true,
      "severity": "warning"
    }
  }
}
```

---

## 🐛 调试器 (yan_debugger.py)

完整的调试器，支持断点、单步执行等功能。

### 功能特性

- ✅ 断点管理（条件断点、命中计数）
- ✅ 单步执行（Step in / Step out / Next）
- ✅ 变量查看与修改
- ✅ 调用堆栈
- ✅ 表达式计算
- ✅ 调试控制台
- ✅ 符合 DAP (Debug Adapter Protocol) 协议

### 使用方式

#### 命令行调试

```bash
# 启动调试
python yan_debugger.py --file 主.yan
```

#### VSCode 调试

在 `.vscode/launch.json` 中添加配置：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Yan: 调试文件",
      "type": "yan",
      "request": "launch",
      "program": "${file}",
      "stopOnEntry": true
    }
  ]
}
```

### 调试命令

调试器支持以下命令（在调试控制台中）：

- `step` / `s` - 单步进入
- `next` / `n` - 单步跳过
- `stepout` / `so` - 单步跳出
- `continue` / `c` - 继续执行
- `pause` / `p` - 暂停执行
- `variables` / `vars` - 查看变量
- `eval <expr>` - 计算表达式
- `break <line>` - 设置断点
- `list` / `l` - 列出当前代码
- `help` - 显示帮助

---

## 📦 包管理器 (yan_pkg.py)

包管理器用于安装、管理言语言的第三方包。

### 功能特性

- ✅ 包搜索与安装
- ✅ 包版本管理
- ✅ 依赖解析
- ✅ 项目初始化
- ✅ 包发布
- ✅ 包卸载与更新

### 安装方式

```bash
# 包管理器已包含在言语言发行版中
yan 包 help  # 显示帮助
```

### 常用命令

#### 初始化项目

```bash
yan 包 初始化 [项目名]
# 或
yan 包 init
```

这会创建：
- `package.json` - 包配置文件
- `主.yan` - 入口文件
- `tests/` - 测试目录
- `.yan.json` - 语言配置

#### 安装包

```bash
yan 包 安装 <包名> [版本]
# 或
yan 包 i <包名>

# 示例
yan 包 安装 网络请求
yan 包 安装 math-utils ^2.0.0
```

#### 列出已安装的包

```bash
yan 包 列表
# 或
yan 包 ls
```

#### 更新包

```bash
yan 包 更新 [包名]

# 更新所有包
yan 包 更新

# 更新特定包
yan 包 更新 网络请求
```

#### 卸载包

```bash
yan 包 卸载 <包名>
# 或
yan 包 uninstall <包名>
```

#### 搜索包

```bash
yan 包 搜索 <关键词>
# 或
yan 包 s <关键词>

# 示例
yan 包 搜索 json
```

#### 查看包信息

```bash
yan 包 信息 <包名>
```

#### 发布包

```bash
yan 包 发布
```

需要先在 https://yanpkg.org 注册账号并获取 API key。

### package.json 格式

```json
{
  "name": "my-package",
  "version": "0.1.0",
  "description": "我的包描述",
  "author": "作者名",
  "dependencies": {
    "网络请求": "^1.0.0",
    "json-tools": "~1.2.0"
  },
  "entry": "主.yan",
  "repository": "https://github.com/...",
  "license": "MIT"
}
```

### 版本规范

- `^1.0.0` - 兼容 1.0.0 到 2.0.0 以下的版本
- `~1.0.0` - 兼容 1.0.0 到 1.1.0 以下的版本
- `1.0.0` - 精确版本

---

## 🛠️ 完整工作流程示例

### 1. 创建新项目

```bash
# 初始化项目
yan 包 init my-project
cd my-project
```

### 2. 编写代码

创建文件 `主.yan`：

```yan
-- my-project 主文件

定 hello 函 name:
    印 "你好, " 连 name 连 "!"

定 加 函 a b:
    a 加 b

定 main 函:
    hello "世界"
    定 result 加 2 3
    印 result

main()。

出 hello 加 main。
```

### 3. 使用 LSP

在 VSCode 中打开项目，获得：
- 语法高亮
- 代码补全
- 实时诊断

### 4. 调试程序

设置断点，启动调试器。

### 5. 安装依赖包

```bash
yan 包 install 网络请求
```

### 6. 运行程序

```bash
yan 运行 主.yan
```

### 7. 发布包（可选）

```bash
yan 包 发布
```

---

## 📚 更多资源

- [语言规范](../docs/LANGUAGE_SPEC.md)
- [入门教程](../docs/TUTORIAL.md)
- [标准库文档](../stdlib/README.md)
- [自举历史](../selfhost/BOOTSTRAP_SUCCESS_REPORT.md)

## 🤝 贡献

欢迎贡献言语言的工具链！

- [GitHub 仓库](https://github.com/yan-lang/yan)
- [问题反馈](https://github.com/yan-lang/yan/issues)
- [讨论区](https://github.com/yan-lang/yan/discussions)
