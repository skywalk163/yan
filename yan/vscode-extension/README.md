# 言语言 VS Code 扩展

言语言的官方 VS Code 扩展，提供完整的 IDE 支持。

## 功能特性

- **语法高亮** - 完整的言语言语法高亮支持
- **自动补全** - 内置函数和用户定义函数的自动补全
- **悬停提示** - 函数文档悬停显示
- **跳转定义** - 跳转到函数/变量定义
- **查找引用** - 查找符号的所有引用
- **重命名** - 符号重命名重构
- **错误诊断** - 实时语法和语义错误检查
- **代码格式化** - 代码格式化支持
- **代码片段** - 常用代码模板
- **调试支持** - 基础调试功能

## 安装

### 方式一：从 VSIX 安装

```bash
code --install-extension yan-language-0.5.0.vsix
```

### 方式二：本地开发安装

```bash
cd vscode-extension
npm install
npm run compile
```

然后在 VS Code 中按 `F5` 启动调试。

## 配置

在 VS Code 设置中可以配置以下选项：

```json
{
  "yan.languageServer.enabled": true,
  "yan.format.enable": true,
  "yan.linter.enable": true
}
```

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+P` -> `Yan: 运行文件` | 运行当前文件 |
| `Ctrl+Shift+P` -> `Yan: 格式化` | 格式化代码 |
| `Ctrl+Shift+P` -> `Yan: 帮助` | 显示帮助文档 |

## 项目结构

```
vscode-extension/
├── package.json          # 扩展配置
├── extension.js         # 扩展入口
├── debugger.js          # 调试适配器
├── language-configuration.json
├── syntaxes/
│   ├── yan.tmLanguage.json    # 言语言语法
│   └── yanmd.tmLanguage.json  # 言文档语法
├── snippets/
│   └── yan.json         # 代码片段
└── server/
    └── main.js          # LSP 服务器入口
```

## 开发

### 依赖

- Node.js >= 16
- npm >= 8
- Python >= 3.8

### 构建

```bash
npm install
npm run compile
```

### 测试

按 `F5` 启动调试会话，在新窗口中打开一个 `.yan` 文件进行测试。

## 发布

```bash
npm install -g vsce
vsce package
vsce publish
```

## 许可证

MIT
