# 言语言示例代码

本目录包含言语言的各种示例，从基础到高级，帮助你快速上手。

---

## 快速开始

### 运行示例

```bash
# 进入 yan 目录
cd yan

# 运行示例文件
python main.py examples/basic.yan

# 调试模式（显示解析过程）
python main.py examples/basic.yan --debug
```

### 交互模式

```bash
python main.py
```

进入交互模式后，输入代码，按空行结束：

```
言> 定x=10。

言> x加5。
  => 15
```

---

## 示例列表

### 基础入门

| 文件 | 内容 | 难度 |
|------|------|------|
| `basic.yan` | 基本运算、变量、函数 | ⭐ |
| `factorial.yan` | 递归函数（阶乘） | ⭐⭐ |
| `block.yan` | 块结构语法 | ⭐⭐ |

### 双轨制语法

| 文件 | 内容 | 难度 |
|------|------|------|
| `dual-track.yan` | 数学表达式 `$()` 和 Python 代码块 `{{}}` | ⭐⭐ |

### 经典算法

| 文件 | 内容 | 难度 |
|------|------|------|
| `hanoi.yan` | 汉诺塔问题（递归） | ⭐⭐⭐ |
| `8queens.yan` | 八皇后问题（回溯） | ⭐⭐⭐⭐ |

### Markdown 文学编程

| 文件 | 内容 | 难度 |
|------|------|------|
| `demo.ymd` | YanMD 格式演示 | ⭐⭐ |
| `math_demo.ymd` | 数学公式 + 代码 | ⭐⭐ |

---

## 示例详解

### 1. basic.yan - 基础入门

```yan
-- 注释用 -- 开头

-- 基本运算
印10加5。        -- 15
印10乘5。        -- 50

-- 变量定义
定x=10。
定y=20。
印x加y。         -- 30

-- 函数定义
定平方=函x乘x x。
印平方5。        -- 25
```

**学习要点：**
- `印` 用于输出
- `定` 用于定义变量
- `函` 用于定义函数
- `。` 是语句结束符

---

### 2. factorial.yan - 递归函数

```yan
-- 阶乘函数
定阶乘=函n若n等1则1否则n乘阶乘n减1。

印阶乘5。        -- 120
印阶乘10。       -- 3628800
```

**学习要点：**
- `若...则...否则...` 条件语句
- 函数可以递归调用自己

---

### 3. block.yan - 块结构

```yan
-- 块结构函数
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。

印距离3 7。      -- 4
印距离7 3。      -- 4
```

**学习要点：**
- `：` 开始代码块
- 块内可以定义局部变量
- 最后一个表达式的值作为返回值

---

### 4. dual-track.yan - 双轨制语法

```yan
-- 数学表达式 $()
定面积=$(3.14159 * 5 * 5)。
印面积。         -- 78.53975

-- Python 代码块 {{}}
定数据={{[x*x for x in range(1, 6)]}}。
印数据。         -- [1, 4, 9, 16, 25]
```

**学习要点：**
- `$()` 用于数学表达式
- `{{}}` 用于 Python 代码
- 各取所长：中文负责逻辑，数学/Python 负责计算

---

### 5. hanoi.yan - 汉诺塔

```yan
-- 汉诺塔实现
定汉诺塔={{
def hanoi(n, source, target, auxiliary):
    if n == 1:
        print(f"移动盘子 1: {source} -> {target}")
        return
    hanoi(n - 1, source, auxiliary, target)
    print(f"移动盘子 {n}: {source} -> {target}")
    hanoi(n - 1, auxiliary, target, source)
hanoi
}}。

汉诺塔3 "A" "C" "B"。
```

**学习要点：**
- 复杂算法可以用 Python 实现
- 言语言负责调用和参数传递

---

### 6. 8queens.yan - 八皇后

```yan
-- 八皇后问题
定安全={{
def safe(queens, row):
    for i in range(row):
        if queens[i] == queens[row]:
            return False
        if abs(queens[i] - queens[row]) == row - i:
            return False
    return True
safe
}}。

-- 求解函数
定求解={{...}}。

印求解[] 0 8。   -- 找到全部 92 个解
```

**学习要点：**
- 回溯算法
- 多个 Python 函数协作

---

### 7. demo.ymd - Markdown 文学编程

```markdown
# 数学工具库

定义常用变量：

```yan
定PI=3.14159。
```

## 几何计算

```yan
定面积=函r PI乘r乘r。
印面积5。
```
```

**运行方式：**

```bash
python yanmd_executor.py examples/demo.ymd output.md
```

**学习要点：**
- `#` 标题定义作用域
- 代码块自动执行
- 文档即程序

---

## 常见问题

### Q: 如何调试代码？

```bash
python main.py 文件.yan --debug
```

会显示：
- Token 流（词法分析结果）
- AST（语法树）
- 生成的 Python 代码

### Q: 如何运行 Markdown 文件？

```bash
python yanmd_executor.py 文件.ymd 输出.md
```

### Q: 如何使用交互模式？

```bash
python main.py
```

输入代码后，按**空行**结束。输入 `quit` 或 `退出` 退出。

### Q: 变量命名有什么限制？

- 可以用中文：`定姓名="张三"`
- 可以用英文：`定name="张三"`
- 不能用动词命名：`定加=10`（会与运算符冲突）

### Q: 如何调用 Python 库？

```yan
定数据={{import numpy as np; np.array([1, 2, 3])}}。
印数据。
```

---

## 学习路径

```
basic.yan
    ↓
factorial.yan → block.yan
    ↓
dual-track.yan
    ↓
hanoi.yan → 8queens.yan
    ↓
demo.ymd（文学编程）
```

---

## 语法速查

| 功能 | 语法 |
|------|------|
| 输出 | `印值。` |
| 变量 | `定名称=值。` |
| 函数 | `定名称=函参数... 函数体。` |
| 条件 | `若条件则结果1否则结果2。` |
| 管道 | `数据，操作1，操作2。` |
| 数学 | `$(表达式)` |
| Python | `{{代码}}` |
| 引用 | `'表达式` |

---

## 更多资源

- [语法手册](../docs/SYNTAX.md) - 完整的语法文档
- [YanMD 规范](../docs/YANMD_SPEC.md) - Markdown 文学编程格式

**编程是实践的艺术，动手写才是最好的学习方式！**
