# 言语言 VS Code 插件

文言为表，函数为里。

## 特性

- ✅ 语法高亮
- ✅ 自动补全
- ✅ 错误诊断
- ✅ 悬停提示
- ✅ 代码格式化

## 安装

### 从 VS Code 市场安装

1. 打开 VS Code
2. 按 `Ctrl+Shift+X` 打开扩展面板
3. 搜索 "Yan Language"
4. 点击安装

### 从源码安装

```bash
cd yan/vscode-extension
npm install
npm run compile
```

## 使用

### 创建言语言文件

1. 创建新文件，扩展名为 `.yan`
2. 编写言语言代码：

```yan
定 平方 = 函 x 乘 x x。
印 平方 5。
```

### 编译和运行

- 按 `Ctrl+Shift+P` 打开命令面板
- 输入 "言语言：编译当前文件"
- 或右键选择 "言语言：运行当前文件"

## 配置

在 `settings.json` 中配置：

```json
{
  "yan.compilerPath": "path/to/yan/compiler",
  "yan.enableDiagnostics": true,
  "yan.enableCompletion": true
}
```

## 示例

### 基础运算

```yan
加 1 2。
乘 3 4。
列 1 2 3 皆 乘 2。
```

### 函数定义

```yan
定 阶乘 = 函 n
  若 等于 n 0
    返回 1。
  否则
    返回 乘 n 阶乘 减 n 1。
  。
。

印 阶乘 5。
```

### 列表操作

```yan
定 数据 = 列 1 2 3 4 5。
定 平方数据 = 皆 平方 数据。
定 偶数数据 = 只 函 x 等于 模 x 2 0 数据。
印 平方数据。
印 偶数数据。
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**更新日期**：2026-05-18
