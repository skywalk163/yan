# 言语言 VS Code 插件

文言为表，函数为里。

## 特性

- ✅ 语法高亮
- ✅ 自动补全（包括关键字、动词、标准库函数）
- ✅ 错误诊断
- ✅ 悬停提示
- ✅ 代码格式化
- ✅ 调试支持
- ✅ 编译和运行命令
- ✅ 代码片段支持

## 安装

### 从源码安装

```bash
cd yan/vscode-extension
npm install
npm run compile
```

然后在 VS Code 中：
1. 按 `F5` 打开扩展开发主机
2. 在新窗口中即可使用插件

## 使用

### 创建言语言文件

1. 创建新文件，扩展名为 `.yan`
2. 编写言语言代码（支持缩进语法）：

```yan
-- 使用缩进语法（推荐）
定 平方 = 函 x
  乘 x x

印 平方 5
```

### 编译和运行

- 按 `Ctrl+Shift+P` 打开命令面板
- 输入 "言语言：编译当前文件" 或 "言语言：运行当前文件"
- 或右键选择相应命令

### 代码格式化

- 按 `Ctrl+Shift+P` 打开命令面板
- 选择 "格式化文档" 或使用快捷键
- 或执行命令 "言语言：格式化当前文件"

### 调试支持

1. 配置启动配置：
   - 打开运行和调试面板 (`Ctrl+Shift+D`)
   - 点击 "创建 launch.json 文件"
   - 选择 "言语言"

2. 在代码中设置断点（点击行号左侧）

3. 按 F5 开始调试

调试特性：
- 断点支持
- 变量查看
- 单步执行
- 调用堆栈

## 配置

在 `settings.json` 中配置：

```json
{
  "yan.pythonPath": "python",
  "yan.compilerPath": "",
  "yan.format.indentSize": 2,
  "yan.format.maxLineLength": 80
}
```

## 标准库模块

### 基础模块
- 数学运算：加、减、乘、除、模、幂等
- 比较运算：大、小、等、不等
- 列表操作：列、首、余、长、添、连、反、排、最大、最小、求和、计数
- 高阶函数：皆、只、归

### 标准库导入

言语言标准库提供丰富的功能模块：

```yan
引 stdlib/math
引 stdlib/collections
引 stdlib/functional
引 stdlib/algorithms
```

## 语法示例

### 基础运算

```yan
加 1 2
乘 3 4
列 1 2 3 皆 乘 2
```

### 函数定义（混合模式）

```yan
定 阶乘 = 函 n
  若 等 n 0
    返回 1
  否则
    返回 乘 n 阶乘 减 n 1

印 阶乘 5
```

### 条件语句

```yan
若 大 x 0
  印 "正数"
否则
  印 "非正数"
```

### 循环遍历

```yan
遍历 x 于 列 1 2 3 4 5
  印 加 x 1
```

### 列表操作

```yan
定 数据 = 列 1 2 3 4 5
定 平方数据 = 皆 平方 数据
定 偶数数据 = 只 函 x 等 模 x 2 0 数据
印 平方数据
印 偶数数据
```

## 命令列表

- `yan.compile` - 编译当前文件
- `yan.run` - 运行当前文件
- `yan.format` - 格式化当前文件
- `yan.toggleOutline` - 切换大纲视图

## 开发工具

言语言提供以下工具：

### 代码格式化工具 (yan_fmt.py)

```bash
# 格式化文件并输出
python yan_fmt.py input.yan

# 原地修改
python yan_fmt.py --inplace input.yan

# 自定义缩进
python yan_fmt.py --indent-size 4 input.yan
```

### 调试适配器 (yan_debug.py 和 debug_server.py)

```bash
# 启动调试服务器
python debug_server.py 4711
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**更新日期**：2026-05-18
