# 中文编程语言语法设计规范

> 综合言叶、文言心、言三个项目的精华，设计最符合中文语法、国人习惯的优雅中文编程语法。

---

## 〇、文档约定

本文档同时包含**语言语法规范**与**文档说明标注**，必须严格区分：

### 标记规则

| 标记方式 | 含义 | 是否参与计算 | 示例 |
|----------|------|:---:|------|
| `` `代码` `` | 语言语法元素 | ✅ 是 | `` `5加3` `` 是可执行代码 |
| `` ```代码块``` `` | 语言代码片段 | ✅ 是 | 多行可执行代码 |
| `$公式$` | 行内数学公式 | ❌ 仅文档 | $a + b$ 表示加法语义 |
| `$$公式$$` | 独立数学公式 | ❌ 仅文档 | $$\text{arity}(f) = 2$$ |
| **粗体** | 概念强调 | ❌ 仅文档 | **动词吞噬** |
| `→` | 求值结果标注 | ❌ 仅文档 | `` `5加3` → 8 `` |
| `# 注释` / `-- 注释` | 语言内注释 | ❌ 不参与计算 | `` `5加3。  -- 求和` `` |

### 判定原则

1. **反引号内的内容**：语言语法，参与编译和计算
2. **LaTeX 公式**：数学描述，仅用于文档中精确表达语义
3. **`→` 右侧**：求值结果，仅用于文档说明，不是语言语法
4. **BNF 产生式**：语法规则描述，属于文档元语言，不是语言本身

### 示例对照

````
`5加3。` → 8
````

- `` `5加3。` `` — 语言代码，参与计算
- `→` — 文档标注，表示"求值为"
- `8` — 求值结果，文档说明

$$
5 \mathbin{\text{加}} 3 \;\Rightarrow\; 8
$$

- 上述 LaTeX 公式精确表达了 `加` 的数学语义：$f(a, b) = a + b$

---

## 一、核心理念

> **中文为骨，数学为翼，无空格为表，管道为脉**

- **中文语序**：主-谓-宾，`` `5加3` `` 而非 `` `(+ 5 3)` ``
- **无空格分词**：通过预分词层自动切分，代码无需空格
- **动词吞噬**：动词向右收集参数，直到遇到阻断符
- **管道流动**：`` `，` `` 连接操作，数据从左向右流
- **双轨融合**：中文叙述逻辑，数学公式精确计算

---

## 二、三项目对比分析

| 特性 | 言叶 (YánYè) | 文言心 (WénYánXīn) | 言 (Yán) |
|------|-------------|-------------------|---------|
| 变量定义 | `` `定x=5。` `` | `` `定x为10。` `` / `` `定x=2*3+1` `` | `` `定x=10。` `` |
| 变量修改 | 无 | `` `设x为x+1。` `` | 无（重新定） |
| 函数定义 | `` `定f(x,y)=x加y。` `` | `` `fact(n)：...完。` `` | `` `定阶乘=函n...` `` |
| 匿名函数 | `` `函(x,y)x加y。` `` | 无 | `` `函x乘x x` `` |
| 条件 | `` `若5大3则印1否则印0。` `` | `` `若x>0则1否则2。` `` | `` `若5大3则"大"否则"小"。` `` |
| 循环 | 无 | `` `遍历i从1到5：...` `` | 无内置 |
| 管道 | `` `10加5，乘2。` `` | `` `10加5，乘2。` `` | `` `10加5，乘2。` `` |
| 列表 | `` `列1 2 3` `` | `` `列1 2 3` `` | `` `列1 2 3` `` |
| 高阶函数 | `` `皆乘2` `` / `` `只大3` `` / `` `归加0` `` | `` `皆乘2` `` / `` `只大3` `` / `` `归加0` `` | `` `皆乘2` `` / `` `只大3` `` / `` `归加0` `` |
| 数学表达式 | 无 | `` `2*3+1` `` 内联 | `` `$(2*3+1)` `` |
| Python嵌入 | 无 | 无 | `` `{{...}}` `` |
| 块结构 | 段落（空行分隔） | `` `：` ``开始，自然结束 | `` `：` ``开始，独立`` `。` ``结束 |
| 同像性 | 规划中 | `` `「」` ``+`` `行` `` | `` `「」` ``+`` `行` `` |
| 后端 | Python转译 | SBCL (Common Lisp) | Python转译 |
| 词法分析 | 简单单字切分 | 类型切换+贪心匹配 | 类型切换+多字贪心匹配（最完善） |

**取长补短**：
- 从**言叶**取：无空格理念、管道操作、段落式块结构
- 从**文言心**取：`` `定` ``/`` `设` ``区分、`` `遍历` ``/`` `当` ``循环、自然结束机制、同像性
- 从**言**取：`` `$()` ``数学表达式、`` `{{}}` ``Python嵌入、`` `函` ``函数定义、贪心分词器、`` `真` ``/`` `假` ``/`` `空` ``

---

## 三、预分词层设计（实现无空格的关键）

### 3.1 编译管道架构

```
源码字符串
  ↓ (1. 预分词层 Pre-tokenizer：无空格分词，贪心匹配)
Token流
  ↓ (2. 正式词法分析器 Lexer：类型标注、位置记录)
标准Token流
  ↓ (3. 语法分析器 Parser：动宾吞噬、副词修饰、管道构建)
AST
  ↓ (4. 宏展开 Macro Expand：处理「」与宏) [V2.0]
AST
  ↓ (5. 求值器/转译器 Evaluator/Transpiler：柯里化、管道注入、求值)
结果数据
```

### 3.2 预分词规则

优先级从高到低：

| 优先级 | 类型 | 规则 | 示例 |
|:---:|------|------|------|
| 1 | `META` | 结构锚点，遇到即切断 | `` `。` `` `` `，` `` `` `「` `` `` `」` `` `` `：` `` `` `=` `` |
| 2 | `STRING` | 引号包围，整体提取 | `` `"你好"` `` `` `『Hello World』` `` |
| 3 | `MATH` | `` `$(...)` `` 包围，整体提取 | `` `$(1+2*3)` `` |
| 4 | `PYTHON` | `` `{{...}}` `` 包围，整体提取 | `` `{{import os}}` `` |
| 5 | `NUM` | 连续数字+小数点 | `` `123` `` `` `3.14` `` |
| 6 | `HAN` | 连续汉字，贪心最长匹配关键字 | `` `定义` `` `→` `[定义]`, `` `皆乘` `` `→` `[皆,乘]` |
| 7 | `IDENT` | 字母/下划线开头，含数字 | `` `x` `` `` `fact` `` `` `n1` `` |
| 8 | `SPACE` | 空白符，仅作同类数据间分隔，直接丢弃 | `` `1 2 3` `` `→` NUM NUM NUM |

### 3.3 字符分类

```
META  ：。 ， 「 」 ： = ( ) 『 』
NUM   ：0-9 .
HAN   ：CJK Unified Ideographs (U+4E00-U+9FFF)
SPACE ：空格、制表符、换行
OTHER ：字母、下划线、其他符号
```

### 3.4 贪心最长匹配

当遇到连续汉字时，优先查字典匹配最长的关键字：

```
输入：定义阶乘函n若n等1则1否则n乘阶乘n减1

分词结果：
[定义] [阶乘] [函] [n] [若] [n] [等] [1] [则] [1] [否则] [n] [乘] [阶乘] [n] [减] [1]
```

如果没有多字关键字，退化为单字切分：

```
输入：皆乘2

分词结果：
[皆] [乘] [2]
```

贪心匹配的形式化定义：

$$
\text{match}(s, i, K) = \arg\max_{k \in K,\; s[i:i+|k|] = k} |k|
$$

其中 $K$ 为关键字集合，$s$ 为源码字符串，$i$ 为当前位置。即从位置 $i$ 开始，选择能匹配的最长关键字。

### 3.5 空白符处理

空白符**不是**分词边界，仅作同类数据间的分隔符：

- `` `1 2 3` `` `→` 三个独立数字 `` `1` `` `` `2` `` `` `3` ``（空格分隔同类数据）
- `` `10加5` `` `→` `[10] [加] [5]`（类型切换自动分词，无需空格）
- `` `定x=5` `` `→` `[定] [x] [=] [5]`（META切断+类型切换）

形式化描述：空白符仅在两个相邻 Token 同属 `NUM` 类时起分隔作用，否则直接丢弃。

$$
\text{space}(t_1, t_2) = \begin{cases} \text{separator} & \text{if } \text{type}(t_1) = \text{type}(t_2) = \text{NUM} \\ \text{discard} & \text{otherwise} \end{cases}
$$

### 3.6 预分词层参考实现

```python
def pre_tokenize(source: str, keywords: set) -> list:
    tokens = []
    i = 0
    n = len(source)
    max_kw_len = max(len(k) for k in keywords) if keywords else 1

    def is_han(ch):
        if not ch: return False
        return '\u4e00' <= ch <= '\u9fff'

    while i < n:
        c = source[i]

        if c in '。，：「」：=()『』':
            tokens.append(('META', c))
            i += 1
            continue

        if c == '"':
            j = i + 1
            while j < n and source[j] != '"': j += 1
            tokens.append(('STRING', source[i+1:j]))
            i = j + 1
            continue

        if c == '『':
            j = i + 1
            while j < n and source[j] != '』': j += 1
            tokens.append(('STRING', source[i+1:j]))
            i = j + 1
            continue

        if c == '$' and i+1 < n and source[i+1] == '(':
            depth, j = 1, i + 2
            while j < n and depth > 0:
                if source[j] == '(': depth += 1
                elif source[j] == ')': depth -= 1
                j += 1
            tokens.append(('MATH', source[i+2:j-1]))
            i = j
            continue

        if c == '{' and i+1 < n and source[i+1] == '{':
            depth, j = 1, i + 2
            while j < n and depth > 0:
                if source[j:j+2] == '{{': depth += 1; j += 2
                elif source[j:j+2] == '}}': depth -= 1; j += 2
                else: j += 1
            tokens.append(('PYTHON', source[i+2:j-2]))
            i = j
            continue

        if c.isdigit() or (c == '-' and i+1 < n and source[i+1].isdigit()):
            j = i
            has_dot = False
            if c == '-': j += 1
            while j < n:
                if source[j].isdigit(): j += 1
                elif source[j] == '.' and not has_dot: has_dot = True; j += 1
                else: break
            tokens.append(('NUM', source[i:j]))
            i = j
            continue

        if is_han(c):
            matched = None
            for length in range(min(max_kw_len, n-i), 0, -1):
                if source[i:i+length] in keywords:
                    matched = source[i:i+length]
                    break
            if matched:
                tokens.append(('WORD', matched))
                i += len(matched)
            else:
                j = i
                while j < n and is_han(source[j]):
                    found_kw = False
                    for length in range(min(max_kw_len, n-j), 0, -1):
                        if source[j:j+length] in keywords:
                            found_kw = True
                            break
                    if found_kw: break
                    j += 1
                tokens.append(('WORD', source[i:j]))
                i = j
            continue

        if c.isalpha() or c == '_':
            j = i
            while j < n and (source[j].isalnum() or source[j] == '_') and not is_han(source[j]): j += 1
            tokens.append(('IDENT', source[i:j]))
            i = j
            continue

        if c.isspace():
            i += 1
            continue

        if c == '-' and i+1 < n and source[i+1] == '-':
            while i < n and source[i] != '\n': i += 1
            continue

        i += 1

    return tokens
```

---

## 四、语法规范

### 4.1 语句

```
语句 ::= 表达式 '。'
```

`` `。` ``（句号）结束语句并触发求值，就像中文写作的句号。

### 4.2 运算符优先级

中文轨运算符优先级从高到低（同优先级从左到右）：

| 优先级 | 运算符 | 元数 | 结合性 | 示例 |
|:---:|--------|:---:|:---:|------|
| 1 | `` `幂` `` | 2 | 右 | `` `2幂10` `` `→` 1024 |
| 2 | `` `负` `` | 1 | 右 | `` `负5` `` `→` -5 |
| 3 | `` `乘` `` `` `除` `` `` `模` `` | 2 | 左 | `` `10除2乘3` `` `→` 15 |
| 4 | `` `加` `` `` `减` `` | 2 | 左 | `` `10减5加3` `` `→` 8 |
| 5 | `` `大` `` `` `小` `` `` `等` `` `` `不等` `` | 2 | 左 | `` `5大3等真` `` `→` 真 |
| 6 | `` `且` `` | 2 | 左 | `` `真且假` `` `→` 假 |
| 7 | `` `或` `` | 2 | 左 | `` `真或假` `` `→` 真 |
| 8 | `` `非` `` | 1 | 右 | `` `非假` `` `→` 真 |

**管道操作符** `` `，` `` 优先级最低，用于连接多个表达式。

### 4.3 变量定义与修改

取文言心的 `` `定` ``/`` `设` `` 区分，统一用 `` `=` `` 连接：

```yan
定x=10。          -- 首次定义
定姓名="张三"。    -- 中文变量名
定面积=$(3.14*r*r)。  -- 混合数学公式

设x=x加1。        -- 修改已有变量
设x=$(x*2)。      -- 数学公式修改
```

**为什么区分 `` `定` `` 和 `` `设` ``？**
- 中文"定"有"确定、首次设定"之意
- 中文"设"有"重新设置、修改"之意
- 区分后语义更清晰，避免意外覆盖

**语法规则**：

```
definition ::= '定' IDENT '=' expr '。'
assignment ::= '设' IDENT '=' expr '。'
```

语义公式：

$$
\text{定}\;x = e \;\Rightarrow\; \text{env}' = \text{env} \cup \{x \mapsto \text{eval}(e)\}
$$

$$
\text{设}\;x = e \;\Rightarrow\; \text{env}' = \text{env}[x \mapsto \text{eval}(e)] \quad (\text{要求 } x \in \text{env})
$$

### 4.4 算术运算

**中文轨**（无空格，动词吞噬）：

```yan
5加3。        → 8
10减5。       → 5
3乘4。        → 12
10除2。       → 5
10模3。       → 1
2幂10。       → 1024
```

**数学轨**（`` `$()` `` 包围，标准优先级）：

```yan
$(1+2*3)。        → 7（先乘后加）
$(2**10)。         → 1024
$(a+b*c)。         → 混合变量
```

**为什么用 `` `$()` `` 而非直接内联？**
- 边界清晰，词法分析器无需猜测 `` `+` `` 是数学加号还是其他
- 优先级明确，数学表达式内部遵循标准数学规则
- 与中文轨不冲突，两种风格各司其职

**语法规则**：

```
expr ::= han_expr | math_expr | pipeline_expr | ...
han_expr ::= term (verb term)*
math_expr ::= '$(' python_expr ')'
```

中文轨动词的数学语义：

$$
\text{加}(a, b) = a + b, \quad \text{减}(a, b) = a - b, \quad \text{乘}(a, b) = a \times b
$$

$$
\text{除}(a, b) = \frac{a}{b}, \quad \text{模}(a, b) = a \bmod b, \quad \text{幂}(a, b) = a^b
$$

### 4.5 比较与逻辑

```yan
5大3。        → 真
3小5。        → 真
5等5。        → 真
5不等3。      → 真

真且真。      → 真
假或真。      → 真
非假。        → 真
```

布尔值用 `` `真` ``/`` `假` ``，空值用 `` `空` ``——最自然的中文表达。

**内置动词表**：

| 类别 | 动词 | 元数 | 语义 |
|------|------|:---:|------|
| 算术 | `` `加` `` `` `减` `` `` `乘` `` `` `除` `` `` `模` `` `` `幂` `` | 2 | 基础算术 |
| 比较 | `` `大` `` `` `小` `` `` `等` `` `` `不等` `` | 2 | 返回 真/假 |
| 逻辑 | `` `且` `` `` `或` `` | 2 | 逻辑与/或 |
| 逻辑 | `` `非` `` | 1 | 逻辑非 |
| 取反 | `` `负` `` | 1 | 取负数 |

比较与逻辑的数学语义：

$$
\text{大}(a, b) = (a > b), \quad \text{小}(a, b) = (a < b), \quad \text{等}(a, b) = (a = b)
$$

$$
\text{且}(a, b) = a \land b, \quad \text{或}(a, b) = a \lor b, \quad \text{非}(a) = \lnot a, \quad \text{负}(a) = -a
$$

### 4.6 管道操作

`` `，` ``（中文逗号）是管道操作符，将前一步结果注入后一步：

```yan
10加5，乘2。              → 30    -- (10+5)*2
100减50，除2，加10。       → 35    -- ((100-50)/2)+10
列1 2 3，皆乘2。           → [2,4,6]
列1 2 3 4 5，只大3，归加0。 → 9     -- [4,5]→9
```

**管道注入规则**：
1. 管道前的结果作为管道后动词的**第一个参数**
2. 若动词已有部分参数（柯里化），管道值填入**空缺的左侧参数位**
3. 若动词参数已满，报错

**语法规则**：

```
pipeline ::= expr ('，' expr)*
```

管道的形式化语义：

$$
\text{pipe}(e_1, e_2, \ldots, e_n) = e_n(\ldots e_2(e_1) \ldots)
$$

更精确地，设 $v_0 = \text{eval}(e_1)$，则：

$$
v_i = \begin{cases} \text{eval}(e_{i+1}) & \text{if } i = 0 \\ \text{inject}(v_{i-1},\, e_{i+1}) & \text{if } i > 0 \end{cases}
$$

其中 $\text{inject}$ 将管道值注入缺参闭包的左侧参数位。

### 4.7 列表操作

```yan
列1 2 3。         → [1, 2, 3]
范围5。            → [1, 2, 3, 4, 5]

列1 2 3，首。      → 1       -- 取首
列1 2 3，余。      → [2,3]   -- 取余
列1 2 3，入1。     → 2       -- 索引取值（从0开始）
列1 2 3，长。      → 3       -- 取长度
列1 2 3，添4。     → [1,2,3,4]  -- 追加
列1 2，连列3 4。   → [1,2,3,4]  -- 连接
列1 2 3，含2。     → 真      -- 包含检查
```

**列表动词表**：

| 动词 | 元数 | 语义 |
|------|:---:|------|
| `` `列` `` | -1 | 构建列表（可变参数） |
| `` `范围` `` | 1 | 生成1到n的列表 |
| `` `首` `` | 1 | 取首元素 |
| `` `余` `` | 1 | 取余下列表 |
| `` `入` `` | 2 | 索引取值 |
| `` `长` `` | 1 | 取长度 |
| `` `添` `` | 2 | 追加元素 |
| `` `连` `` | 2 | 连接列表 |
| `` `含` `` | 2 | 包含检查 |

列表操作的数学语义：

$$
\text{列}(x_1, \ldots, x_n) = [x_1, \ldots, x_n], \quad \text{范围}(n) = [1, 2, \ldots, n]
$$

$$
\text{首}([x_1, \ldots, x_n]) = x_1, \quad \text{余}([x_1, x_2, \ldots, x_n]) = [x_2, \ldots, x_n]
$$

$$
\text{入}(i, L) = L[i], \quad \text{长}(L) = |L|, \quad \text{添}(x, L) = L \mathbin{+\!\!+} [x]
$$

$$
\text{含}(x, L) = x \in L
$$

### 4.8 高阶函数

副词修饰动词，对列表操作：

```yan
列1 2 3，皆乘2。       → [2,4,6]    -- 映射：每个元素乘2
列1 2 3 4 5，只大3。   → [4,5]      -- 过滤：保留大于3
列1 2 3，归加0。       → 6          -- 归约：求和，初值0
列1 2 3，归乘1。       → 6          -- 归约：求积，初值1
```

**副词与管道的协同**：`` `皆` ``/`` `只` ``/`` `归` `` 是副词，它们吞噬右侧的动词形成"副词+动词"组合，再通过管道接收列表数据。

**副词表**：

| 副词 | 元数 | 语义 | 示例 |
|------|:---:|------|------|
| `` `皆` `` | 2 | 遍历映射 | `` `皆乘2` `` |
| `` `只` `` | 2 | 过滤保留 | `` `只大3` `` |
| `` `归` `` | 2 | 归约折叠 | `` `归加0` `` |

**吞噬优先级**：

1. **副词修饰**：`` `皆` ``、`` `只` ``、`` `归` `` 等副词，优先吞噬右侧的动词节点
2. **动词吞噬**：普通动词向右吞噬数字或引用
3. **管道切断**：遇到 `` `，` ``，立刻结束当前吞噬

**推演示例**：`` `列1 2 3，皆乘2。` ``

1. 读到 `` `列` ``，创建 Call(verb=列, args=[])
2. 读到 `` `1 2 3` ``，吞噬入 args，得到 Call(列, [1, 2, 3])
3. 读到 `` `，` ``，切断！将 Call(列) 压入 Pipeline
4. 读到 `` `皆` ``，创建 Call(皆, [])
5. 读到 `` `乘` ``，创建 Call(乘, [])
6. 读到 `` `2` ``，被 `` `乘` `` 吞噬，得到 Call(乘, [2])
7. 副词修饰：`` `皆` `` 发现右侧是 Call(乘)，吞噬之，得到 Call(皆, [Call(乘, [2])])
8. 读到 `` `。` ``，将 Call(皆) 压入 Pipeline，结束

高阶函数的数学语义：

$$
\text{皆}(f, [x_1, \ldots, x_n]) = [f(x_1), \ldots, f(x_n)]
$$

$$
\text{只}(f, [x_1, \ldots, x_n]) = [x_i \mid f(x_i) = \text{真}]
$$

$$
\text{归}(f, z, [x_1, \ldots, x_n]) = f(x_n, \ldots f(x_2, f(x_1, z)) \ldots)
$$

### 4.9 条件判断

```yan
若5大3则"大"否则"小"。           → "大"
若x大0则x否则负x。               → |x|
若分数大90则"优"否则
若分数大80则"良"否则
若分数大60则"及格"否则"不及格"。  -- 链式条件
```

**语法**：`` `若 条件 则 真分支 否则 假分支` ``

这是最自然的中文条件句式，无需括号，无需冒号。

**语法规则**：

```
if_expr ::= '若' expr '则' expr ('否则' expr)?
```

条件表达式的数学语义：

$$
\text{若}\;c\;\text{则}\;e_1\;\text{否则}\;e_2 = \begin{cases} e_1 & \text{if } \text{eval}(c) = \text{真} \\ e_2 & \text{if } \text{eval}(c) = \text{假} \end{cases}
$$

### 4.10 函数定义

**单行函数**（简洁，适合简单逻辑）：

```yan
定加倍=函x乘x 2。
定平方=函x乘x x。
定加三=函a b c加a加b c。
```

**块结构函数**（清晰，适合复杂逻辑）：

```yan
定阶乘=函n：
  若n等1则1否则n乘阶乘n减1。
。

定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。

定统计=函语文 数学 英语：
  定总分=$(语文+数学+英语)。
  定均值=$(总分/3)。
  列总分 均值。
。
```

**块结构规则**：
- `` `：` ``（冒号）开始代码块
- 块内每个语句以 `` `。` `` 结束
- 最后一个表达式的值自动作为返回值
- 独立的 `` `。` `` 结束块（或自然结束）

**为什么用 `` `函` `` 而非 `` `def` ``？**
- `` `函` `` 是"函数"的首字，简洁有力
- `` `函参数 函数体` `` 的语序符合中文"先说明参数，再写操作"
- 无需括号，动词吞噬自动收集参数

**语法规则**：

```
func_def ::= '定' IDENT '=' '函' param* expr '。'
           | '定' IDENT '=' '函' param* '：' block '。'
param    ::= IDENT
block    ::= statement+
```

函数定义的数学语义：

$$
\text{定}\;f = \text{函}\;x_1 \ldots x_n\;e \;\Rightarrow\; f = \lambda x_1 \ldots x_n.\, \text{eval}(e)
$$

### 4.11 循环

取文言心的自然循环语法：

```yan
遍历i从1到10：
  印i。
。

定sum=0。
遍历i从1到100：
  设sum=$(sum+i)。
。
印sum。

当x大0时：
  印x。
  设x=$(x-1)。
。
```

**语法**：
- `` `遍历 变量 从 起始 到 结束：` `` — 遍历循环
- `` `当 条件 时：` `` — 条件循环

这是最贴近中文口语的循环表达。

**语法规则**：

```
for_loop  ::= '遍历' IDENT '从' expr '到' expr '：' block '。'
while_loop ::= '当' expr '时' '：' block '。'
```

循环的数学语义：

$$
\text{遍历}\;i\;\text{从}\;a\;\text{到}\;b\;\text{执行}\;S = \prod_{i=a}^{b} \text{exec}(S)
$$

$$
\text{当}\;c\;\text{时执行}\;S = \text{while}(\text{eval}(c), \text{exec}(S))
$$

### 4.12 同像性（代码即数据）

```yan
「1加2」         → 引用，返回AST不求值
行「1加2」。      → 3，执行引用的代码
```

`` `「」` ``（直角引号）引用代码，`` `行` `` 执行引用——这是 Lisp 同像性的中文表达。

**语法规则**：

```
quote ::= '「' expr '」'
eval  ::= '行' quote
```

同像性的数学语义：

$$
\text{「}e\text{」} = \text{AST}(e) \quad (\text{不求值，返回语法树})
$$

$$
\text{行}(\text{AST}(e)) = \text{eval}(e) \quad (\text{对语法树求值})
$$

### 4.13 注释

```yan
-- 这是注释
注：这也是注释
印x。  -- 行尾注释
```

注释不参与计算，在预分词层直接丢弃。

### 4.14 字符串

```yan
"你好世界"       -- 双引号字符串
『Hello World』  -- 直角引号字符串（可包含空格）
```

支持转义字符：`` `\"` `` `` `\\` `` `` `\n` `` `` `\t` ``

---

## 五、AST 节点定义

```python
class Node: pass

class Num(Node):       value: int | float
class Str(Node):       value: str
class Bool(Node):      value: bool
class Nil(Node):       pass
class Word(Node):      name: str
class MathExpr(Node):  expr: str
class PythonCode(Node): code: str

class Call(Node):      verb: Node; args: list[Node]; is_partial: bool = False
class Pipeline(Node):  steps: list[Node]
class Quote(Node):     expr: Node

class Define(Node):    name: str; value: Node
class Assign(Node):    name: str; value: Node
class Lambda(Node):    params: list[str]; body: Node
class Block(Node):     statements: list[Node]
class If(Node):        cond: Node; then_branch: Node; else_branch: Node | None
class ForLoop(Node):   var: str; start: Node; end: Node; body: Node
class WhileLoop(Node): cond: Node; body: Node
class Program(Node):   statements: list[Node]
```

AST 节点与数学语义的对应：

$$
\text{Call}(f, [e_1, \ldots, e_n]) \;\Rightarrow\; f(\text{eval}(e_1), \ldots, \text{eval}(e_n))
$$

$$
\text{Pipeline}([e_1, \ldots, e_n]) \;\Rightarrow\; \text{pipe}(\text{eval}(e_1), \ldots, \text{eval}(e_n))
$$

$$
\text{Quote}(e) \;\Rightarrow\; \text{AST}(e) \quad (\text{不求值})
$$

---

## 六、语义层设计

### 6.1 元数声明

环境字典存储函数实现及其期望参数总数：

```python
Env = {
    "加": (2, lambda a, b: a + b),
    "减": (2, lambda a, b: a - b),
    "乘": (2, lambda a, b: a * b),
    "除": (2, lambda a, b: a / b),
    "模": (2, lambda a, b: a % b),
    "幂": (2, lambda a, b: a ** b),
    "大": (2, lambda a, b: a > b),
    "小": (2, lambda a, b: a < b),
    "等": (2, lambda a, b: a == b),
    "不等": (2, lambda a, b: a != b),
    "且": (2, lambda a, b: a and b),
    "或": (2, lambda a, b: a or b),
    "非": (1, lambda a: not a),
    "负": (1, lambda a: -a),
    "列": (-1, lambda *args: list(args)),
    "范围": (1, lambda n: list(range(1, n+1))),
    "首": (1, lambda lst: lst[0]),
    "余": (1, lambda lst: lst[1:]),
    "入": (2, lambda i, lst: lst[i]),
    "长": (1, lambda lst: len(lst)),
    "添": (2, lambda x, lst: lst + [x]),
    "连": (2, lambda a, b: a + b),
    "含": (2, lambda x, lst: x in lst),
    "皆": (2, map_func),
    "只": (2, filter_func),
    "归": (2, reduce_func),
    "印": (1, lambda x: print(x)),
    "行": (1, eval_func),
}
```

元数的数学定义：

$$
\text{arity}(f) = n \quad \text{表示函数 } f \text{ 接受 } n \text{ 个参数}
$$

$$
\text{arity}(f) = -1 \quad \text{表示函数 } f \text{ 接受可变参数}
$$

### 6.2 柯里化规则

当动词吞噬的参数数量 $\text{len(args)}$ < 元数 $\text{arity}$ 时：
- **右侧参数先占位**：将已有的 $\text{args}$ 绑定到函数的右侧参数位
- **返回闭包**：生成一个 $\lambda \text{left\_arg}: f(\text{left\_arg}, \ldots \text{args})$，标记剩余元数为 $\text{arity} - \text{len(args)}$

示例：`` `乘2` `` `→` 闭包 $\lambda x. x \times 2$（缺1个参数）

柯里化的形式化定义：

$$
\text{curry}(f, [a_{k+1}, \ldots, a_n]) = \lambda a_1 \ldots a_k.\, f(a_1, \ldots, a_k, a_{k+1}, \ldots, a_n)
$$

其中 $n = \text{arity}(f)$，已提供 $n - k$ 个右侧参数。

### 6.3 管道注入规则

当执行 $\text{Pipeline}(\text{steps})$ 时，维护隐式的 $\text{pipeline\_value}$：

1. 若 $v = \emptyset$，正常求值当前 Call，结果赋给 $v$
2. 若 $v \neq \emptyset$，将其注入当前 Call：
   - 闭包（缺参）：$v$ 作为左操作数传入
   - 可变参数动词：$v$ 追加到参数列表
   - 参数已满：报错（管道溢出）

管道注入的形式化定义：

$$
\text{inject}(v, f) = \begin{cases}
f(v) & \text{if } f \text{ 是闭包，缺1个参数} \\
f(\ldots, v) & \text{if } f \text{ 是可变参数动词} \\
\text{Error} & \text{if } f \text{ 参数已满}
\end{cases}
$$

---

## 七、语法分析器实现（递归下降解析）

### 7.1 解析器结构

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def consume(self):
        token = self.current()
        self.pos += 1
        return token
    
    def expect(self, type_, value=None):
        token = self.consume()
        if token[0] != type_ or (value and token[1] != value):
            raise SyntaxError(f"Expected {type_} {value}, got {token}")
        return token
```

### 7.2 表达式解析（动词吞噬核心）

```python
def parse_expr(self):
    """解析表达式，处理动词吞噬和运算符优先级"""
    return self.parse_pipeline()

def parse_pipeline(self):
    """解析管道表达式"""
    steps = [self.parse_if()]
    while self.current() and self.current()[1] == '，':
        self.consume()
        steps.append(self.parse_if())
    if len(steps) == 1:
        return steps[0]
    return Pipeline(steps)

def parse_if(self):
    """解析条件表达式"""
    if self.current() and self.current()[1] == '若':
        self.consume()
        cond = self.parse_logic_or()
        self.expect('WORD', '则')
        then_branch = self.parse_if()
        else_branch = None
        if self.current() and self.current()[1] == '否则':
            self.consume()
            else_branch = self.parse_if()
        return If(cond, then_branch, else_branch)
    return self.parse_logic_or()

def parse_logic_or(self):
    """解析逻辑或表达式"""
    left = self.parse_logic_and()
    while self.current() and self.current()[1] == '或':
        op = self.consume()
        right = self.parse_logic_and()
        left = Call(Word(op[1]), [left, right])
    return left

def parse_logic_and(self):
    """解析逻辑与表达式"""
    left = self.parse_comparison()
    while self.current() and self.current()[1] == '且':
        op = self.consume()
        right = self.parse_comparison()
        left = Call(Word(op[1]), [left, right])
    return left

def parse_comparison(self):
    """解析比较表达式"""
    left = self.parse_arithmetic()
    while self.current() and self.current()[1] in ['大', '小', '等', '不等']:
        op = self.consume()
        right = self.parse_arithmetic()
        left = Call(Word(op[1]), [left, right])
    return left

def parse_arithmetic(self):
    """解析算术表达式"""
    left = self.parse_unary()
    while self.current() and self.current()[1] in ['加', '减']:
        op = self.consume()
        right = self.parse_unary()
        left = Call(Word(op[1]), [left, right])
    return left

def parse_unary(self):
    """解析一元表达式（负、非）"""
    if self.current() and self.current()[1] in ['负', '非']:
        op = self.consume()
        operand = self.parse_power()
        return Call(Word(op[1]), [operand])
    return self.parse_power()

def parse_power(self):
    """解析幂运算（右结合）"""
    base = self.parse_primary()
    if self.current() and self.current()[1] == '幂':
        op = self.consume()
        exp = self.parse_unary()
        return Call(Word(op[1]), [base, exp])
    return base

def parse_primary(self):
    """解析基本表达式"""
    token = self.current()
    if not token:
        raise SyntaxError("Unexpected end of input")
    
    if token[0] == 'NUM':
        self.consume()
        return Num(float(token[1]) if '.' in token[1] else int(token[1]))
    
    if token[0] == 'STRING':
        self.consume()
        return Str(token[1])
    
    if token[1] == '真':
        self.consume()
        return Bool(True)
    
    if token[1] == '假':
        self.consume()
        return Bool(False)
    
    if token[1] == '空':
        self.consume()
        return Nil()
    
    if token[0] == 'MATH':
        self.consume()
        return MathExpr(token[1])
    
    if token[0] == 'PYTHON':
        self.consume()
        return PythonCode(token[1])
    
    if token[0] == 'IDENT':
        self.consume()
        return Word(token[1])
    
    if token[1] == '函':
        return self.parse_lambda()
    
    if token[1] == '「':
        return self.parse_quote()
    
    if token[1] == '列':
        return self.parse_list()
    
    if token[1] == '遍历':
        return self.parse_for_loop()
    
    if token[1] == '当':
        return self.parse_while_loop()
    
    if token[1] == '定':
        return self.parse_definition()
    
    if token[1] == '设':
        return self.parse_assignment()
    
    if token[0] == 'WORD':
        verb = Word(token[1])
        self.consume()
        return self.parse_call(verb)
    
    raise SyntaxError(f"Unexpected token: {token}")

def parse_call(self, verb):
    """解析动词调用（动词吞噬）"""
    args = []
    arity = get_arity(verb.name)
    
    while self.current():
        token = self.current()
        
        if token[1] in ['。', '，', '则', '否则', '：']:
            break
        
        if token[0] == 'WORD' and is_adverb(token[1]):
            adverb = Word(token[1])
            self.consume()
            inner_call = self.parse_call(verb)
            return Call(adverb, [inner_call])
        
        if token[0] == 'WORD' and is_verb(token[1]):
            break
        
        arg = self.parse_expr()
        args.append(arg)
        
        if arity > 0 and len(args) >= arity:
            break
    
    call = Call(verb, args)
    if arity > 0 and len(args) < arity:
        call.is_partial = True
    return call

def parse_list(self):
    """解析列表构建"""
    self.consume()
    args = []
    while self.current() and self.current()[1] not in ['。', '，']:
        args.append(self.parse_primary())
    return Call(Word('列'), args)

def parse_lambda(self):
    """解析函数定义"""
    self.consume()
    params = []
    
    while self.current():
        token = self.current()
        if token[0] == 'IDENT':
            params.append(token[1])
            self.consume()
        elif token[1] == '：':
            self.consume()
            body = self.parse_block()
            return Lambda(params, body)
        elif token[1] == '。':
            body = self.parse_expr()
            self.consume()
            return Lambda(params, body)
        else:
            body = self.parse_expr()
            return Lambda(params, body)
    
    raise SyntaxError("Unexpected end of lambda")

def parse_block(self):
    """解析代码块"""
    statements = []
    while self.current() and self.current()[1] != '。':
        statements.append(self.parse_expr())
        if self.current() and self.current()[1] == '。':
            self.consume()
    if self.current() and self.current()[1] == '。':
        self.consume()
    return Block(statements)
```

---

## 八、错误处理规范

### 8.1 错误分类

| 错误类型 | 触发场景 | 示例 |
|----------|----------|------|
| **词法错误** | 无法识别的字符序列 | `` `定x=@` ``（`@` 非法） |
| **语法错误** | 不符合语法规则 | `` `若5大3则` ``（缺少否则分支） |
| **语义错误** | 变量未定义、参数数量不匹配 | `` `设y=10。` ``（y未定义） |
| **运行时错误** | 除零、索引越界、类型错误 | `` `10除0。` `` |

### 8.2 错误消息格式

所有错误消息遵循统一格式：

```
[错误类型] [位置]: [中文描述]
    源码: [源代码行]
          [错误位置标记]
```

**示例**：

```
[语义错误] 第3行第5列: 变量「y」未定义
    源码: 设y=10。
          ^
```

### 8.3 错误恢复策略

1. **词法错误**：跳过当前字符，继续分词，记录错误
2. **语法错误**：回退到最近的语句结束符（`` `。` ``），继续解析
3. **语义错误**：抛出异常，终止执行（变量未定义等无法恢复）
4. **运行时错误**：抛出异常，提供完整调用栈

### 8.4 错误类型定义

```python
class YanError(Exception):
    pass

class LexerError(YanError):
    def __init__(self, pos, msg):
        self.pos = pos
        self.msg = msg
    
    def __str__(self):
        return f"[词法错误] 位置{self.pos}: {self.msg}"

class ParserError(YanError):
    def __init__(self, pos, msg, source_line=""):
        self.pos = pos
        self.msg = msg
        self.source_line = source_line
    
    def __str__(self):
        marker = " " * self.pos + "^"
        return f"[语法错误] 位置{self.pos}: {self.msg}\n    源码: {self.source_line}\n          {marker}"

class SemanticError(YanError):
    def __init__(self, pos, msg):
        self.pos = pos
        self.msg = msg
    
    def __str__(self):
        return f"[语义错误] 位置{self.pos}: {self.msg}"

class RuntimeError(YanError):
    def __init__(self, msg, stack=None):
        self.msg = msg
        self.stack = stack or []
    
    def __str__(self):
        result = f"[运行时错误]: {self.msg}"
        if self.stack:
            result += "\n调用栈:"
            for frame in self.stack:
                result += f"\n  {frame}"
        return result
```

---

## 九、标准库设计

### 9.1 数学库

| 函数 | 元数 | 语义 | 示例 |
|------|:---:|------|------|
| `` `正弦` `` | 1 | 正弦函数 | `` `正弦$(3.14/2)` `` `→` 1 |
| `` `余弦` `` | 1 | 余弦函数 | `` `余弦0` `` `→` 1 |
| `` `正切` `` | 1 | 正切函数 | `` `正切0` `` `→` 0 |
| `` `反正弦` `` | 1 | 反正弦函数 | `` `反正弦1` `` `→` π/2 |
| `` `指数` `` | 1 | 自然指数 | `` `指数1` `` `→` e |
| `` `对数` `` | 1 | 自然对数 | `` `对数$(2.718)` `` `→` 1 |
| `` `对数10` `` | 1 | 常用对数 | `` `对数10 100` `` `→` 2 |
| `` `开方` `` | 1 | 平方根 | `` `开方16` `` `→` 4 |
| `` `绝对值` `` | 1 | 绝对值 | `` `绝对值负5` `` `→` 5 |
| `` `取整` `` | 1 | 向下取整 | `` `取整3.9` `` `→` 3 |
| `` `四舍五入` `` | 1 | 四舍五入 | `` `四舍五入3.5` `` `→` 4 |
| `` `随机` `` | 0 | 0-1随机数 | `` `随机` `` `→` 0.42 |
| `` `随机整数` `` | 2 | 指定范围随机整数 | `` `随机整数1到10` `` `→` 7 |

### 9.2 字符串库

| 函数 | 元数 | 语义 | 示例 |
|------|:---:|------|------|
| `` `长度` `` | 1 | 字符串长度 | `` `长度"你好"` `` `→` 2 |
| `` `连接` `` | 2 | 字符串拼接 | `` `连接"你好""世界"` `` `→` "你好世界" |
| `` `分割` `` | 2 | 字符串分割 | `` `分割"a,b,c"","` `` `→` ["a","b","c"] |
| `` `替换` `` | 3 | 字符串替换 | `` `替换"ababa""a""x"` `` `→` "xbxbx" |
| `` `截取` `` | 3 | 字符串切片 | `` `截取"Hello"0到3` `` `→` "Hel" |
| `` `小写` `` | 1 | 转小写 | `` `小写"HELLO"` `` `→` "hello" |
| `` `大写` `` | 1 | 转大写 | `` `大写"hello"` `` `→` "HELLO" |
| `` `查找` `` | 2 | 查找子串位置 | `` `查找"abcde""cd"` `` `→` 2 |
| `` `包含` `` | 2 | 包含检查 | `` `包含"abc""b"` `` `→` 真 |
| `` `格式化` `` | -1 | 字符串格式化 | `` `格式化"{}加{}等于{}"1 2 3` `` `→` "1加2等于3" |

### 9.3 文件IO

| 函数 | 元数 | 语义 | 示例 |
|------|:---:|------|------|
| `` `读文件` `` | 1 | 读取文件内容 | `` `读文件"data.txt"` `` |
| `` `写文件` `` | 2 | 写入文件 | `` `写文件"output.txt""内容"` `` |
| `` `追加文件` `` | 2 | 追加内容 | `` `追加文件"log.txt""日志"` `` |
| `` `路径` `` | 1 | 获取文件路径 | `` `路径"file.txt"` `` |
| `` `文件名` `` | 1 | 获取文件名 | `` `文件名"/a/b.txt"` `` `→` "b.txt" |
| `` `扩展名` `` | 1 | 获取扩展名 | `` `扩展名"file.txt"` `` `→` ".txt" |
| `` `是否存在` `` | 1 | 文件是否存在 | `` `是否存在"file.txt"` `` `→` 真 |
| `` `创建目录` `` | 1 | 创建目录 | `` `创建目录"data"` `` |
| `` `列出目录` `` | 1 | 列出目录内容 | `` `列出目录"."` `` |
| `` `删除文件` `` | 1 | 删除文件 | `` `删除文件"tmp.txt"` `` |

### 9.4 时间库

| 函数 | 元数 | 语义 | 示例 |
|------|:---:|------|------|
| `` `当前时间` `` | 0 | 获取当前时间戳 | `` `当前时间` `` |
| `` `日期` `` | 0 | 获取当前日期 | `` `日期` `` `→` "2026-05-04" |
| `` `时间` `` | 0 | 获取当前时间 | `` `时间` `` `→` "14:30:00" |
| `` `格式化时间` `` | 2 | 时间戳转字符串 | `` `格式化时间当前时间"%Y-%m-%d"` `` |
| `` `解析时间` `` | 2 | 字符串转时间戳 | `` `解析时间"2026-05-04""%Y-%m-%d"` `` |
| `` `睡眠` `` | 1 | 暂停指定秒数 | `` `睡眠1` ``（暂停1秒） |

---

## 十、模块系统

### 10.1 导入语法

```yan
入文件"utils.言"。        -- 导入整个文件
入文件"math.言"为m。      -- 导入并指定别名
入函数"求和"自"utils.言"。  -- 导入特定函数
入全部自"std.言"。        -- 导入所有符号
```

### 10.2 导出语法

```yan
出函数"求和"。            -- 导出单个函数
出函数"求和""求积"。      -- 导出多个函数
出全部。                 -- 导出所有顶级定义
```

### 10.3 命名空间

模块导入后，符号名称遵循以下规则：

1. **完整导入**：`入文件"utils.言"` → 使用 `utils.求和`
2. **别名导入**：`入文件"utils.言"为u` → 使用 `u.求和`
3. **单独导入**：`入函数"求和"自"utils.言"` → 直接使用 `求和`
4. **全部导入**：`入全部自"std.言"` → 直接使用所有符号

### 10.4 模块路径解析

```yan
入文件"./lib/utils.言"。   -- 相对路径
入文件"/usr/lib/yan/std.言"。  -- 绝对路径
入文件"math"。            -- 标准库路径
```

---

## 十一、测试用例

### 11.1 基础运算测试

| 输入 | 预期输出 | 测试目的 |
|------|:---:|----------|
| `` `5加3。` `` | 8 | 基本加法 |
| `` `10减5加3。` `` | 8 | 运算符优先级（从左到右） |
| `` `2幂10。` `` | 1024 | 幂运算（最高优先级） |
| `` `负5加10。` `` | 5 | 一元负号 |
| `` `5大3。` `` | 真 | 比较运算 |
| `` `真且假。` `` | 假 | 逻辑与 |
| `` `非假。` `` | 真 | 逻辑非 |

### 11.2 管道操作测试

| 输入 | 预期输出 | 测试目的 |
|------|:---:|----------|
| `` `10加5，乘2。` `` | 30 | 基本管道 |
| `` `100减50，除2，加10。` `` | 35 | 多步管道 |
| `` `列1 2 3，皆乘2。` `` | [2,4,6] | 管道+高阶函数 |
| `` `列1 2 3 4 5，只大3，归加0。` `` | 9 | 连续管道 |

### 11.3 函数定义测试

| 输入 | 预期输出 | 测试目的 |
|------|:---:|----------|
| `` `定平方=函x乘x x。平方5。` `` | 25 | 单行函数 |
| `` `定阶乘=函n：若n等1则1否则n乘阶乘n减1。。阶乘5。` `` | 120 | 递归函数 |
| `` `定加三=函a b c加a加b c。加三1 2 3。` `` | 6 | 多参数函数 |

### 11.4 变量测试

| 输入 | 预期输出 | 测试目的 |
|------|:---:|----------|
| `` `定x=10。定y=x加5。y。` `` | 15 | 变量定义与引用 |
| `` `定x=5。设x=x加1。x。` `` | 6 | 变量修改 |
| `` `设y=10。` `` | 错误 | 未定义变量赋值 |

### 11.5 边界情况测试

| 输入 | 预期输出 | 测试目的 |
|------|:---:|----------|
| `` `10除0。` `` | 错误 | 除零错误 |
| `` `列1 2 3，入5。` `` | 错误 | 索引越界 |
| `` `$(1/0)` `` | 错误 | 数学表达式错误 |
| `` `若5大3则` `` | 错误 | 语法不完整 |

---

## 十二、性能考量

### 12.1 分词器优化

- **关键字字典结构**：使用 Trie 树或 Aho-Corasick 算法加速关键字匹配
- **缓存机制**：缓存分词结果，避免重复分词

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class KeywordTrie:
    def __init__(self, keywords):
        self.root = TrieNode()
        for kw in keywords:
            self.insert(kw)
    
    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
    
    def longest_match(self, text, start):
        node = self.root
        longest = ""
        current = ""
        i = start
        while i < len(text) and text[i] in node.children:
            node = node.children[text[i]]
            current += text[i]
            if node.is_end:
                longest = current
            i += 1
        return longest if longest else None
```

### 12.2 AST 优化

- **常量折叠**：编译时计算常量表达式
- **死代码消除**：移除不可达代码
- **内联展开**：将小函数内联到调用点

```python
def optimize_ast(node):
    if isinstance(node, Call):
        node.args = [optimize_ast(arg) for arg in node.args]
        
        if isinstance(node.verb, Word) and node.verb.name in ['加', '减', '乘', '除']:
            if all(isinstance(arg, (Num, Bool)) for arg in node.args):
                values = [arg.value for arg in node.args]
                if node.verb.name == '加':
                    return Num(sum(values))
                elif node.verb.name == '乘':
                    result = 1
                    for v in values:
                        result *= v
                    return Num(result)
    return node
```

### 12.3 求值优化

- **惰性求值**：管道操作按需求值
- **缓存策略**：缓存函数调用结果（记忆化）
- **编译缓存**：缓存编译后的 AST，避免重复编译

---

## 十三、设计哲学

| 原则 | 体现 |
|------|------|
| 中文语序 | `` `5加3` `` 主谓宾，`` `若…则…否则…` `` 自然条件句 |
| 无空格 | 预分词层自动切分，`` `10加5乘2` `` 等价于 `` `10 加 5 乘 2` `` |
| 动词吞噬 | 动词向右收集参数，直到遇到阻断符（句号/逗号/另一个动词） |
| 管道流动 | `` `，` `` 连接操作，数据从左向右流，像水管一样 |
| 双轨融合 | 中文轨：`` `5加3` ``，数学轨：`` `$(5+3)` ``，各取所长 |
| 定/设区分 | `` `定` ``首次定义，`` `设` ``修改已有，语义清晰 |
| 自然块结束 | `` `：` ``开始块，自然结束或独立`` `。` ``结束 |
| 同像性 | `` `「」` ``引用+`` `行` ``求值，代码即数据 |
| 极简标点 | 仅用 `` `。` `` `` `，` `` `` `：` `` `` `=` `` `` `「」` `` 六种中文标点 |

---

## 十四、完整形式文法（EBNF）

### 14.1 文法定义

本节定义语言的完整上下文无关文法，使用扩展巴科斯范式（EBNF）表示：

```ebnf
(* 程序结构 *)
program      ::= statement*
statement    ::= definition
               | assignment
               | loop
               | import_stmt
               | export_stmt
               | expr '。'

(* 变量定义与赋值 *)
definition   ::= '定' IDENT '=' expr '。'
assignment   ::= '设' IDENT '=' expr '。'

(* 表达式 *)
expr         ::= pipeline_expr
               | if_expr
               | lambda_expr
               | quote_expr

(* 管道表达式 *)
pipeline_expr::= logic_or_expr
               | logic_or_expr '，' pipeline_expr

(* 条件表达式 *)
if_expr      ::= '若' logic_or_expr '则' expr
               ('否则' expr)?

(* 逻辑运算 *)
logic_or_expr::= logic_and_expr
               | logic_and_expr '或' logic_or_expr

logic_and_expr::= comparison_expr
               | comparison_expr '且' logic_and_expr

(* 比较运算 *)
comparison_expr::= arithmetic_expr
                 | arithmetic_expr compare_op arithmetic_expr

compare_op    ::= '大' | '小' | '等' | '不等'

(* 算术运算 *)
arithmetic_expr::= unary_expr
                 | unary_expr ('加' | '减') arithmetic_expr

unary_expr   ::= power_expr
               | ('负' | '非') unary_expr

power_expr   ::= call_expr ('幂' unary_expr)?

(* 函数调用 *)
call_expr    ::= primary_expr
               | call_expr argument+

argument     ::= primary_expr
               | adverb call_expr

(* 基本表达式 *)
primary_expr ::= NUMBER
               | STRING
               | IDENT
               | list_expr
               | lambda_expr
               | quote_expr
               | block_expr
               | '真'
               | '假'
               | '空'
               | math_expr
               | python_expr

(* 列表 *)
list_expr    ::= '列' element*
element      ::= expr

(* 函数定义 *)
lambda_expr  ::= '函' param* ('：' block | expr)
param        ::= IDENT
block        ::= statement+ '。'

(* 引用 *)
quote_expr   ::= '「' expr '」'

(* 数学表达式 *)
math_expr    ::= '$(' any_python_expr ')'

(* Python 代码块 *)
python_expr  ::= '{{' python_code '}}'

(* 循环 *)
loop         ::= for_loop | while_loop

for_loop     ::= '遍历' IDENT '从' expr '到' expr '：' block
while_loop   ::= '当' expr '时' '：' block

(* 模块系统 *)
import_stmt  ::= '入' import_spec (',' import_spec)* '。'
import_spec ::= '文件' STRING
              | '函数' STRING '自' STRING
              | '全部' '自' STRING
              | import_spec '为' IDENT

export_stmt  ::= '出' export_spec (',' export_spec)* '。'
export_spec ::= '函数' STRING (',' STRING)*
              | '全部'

(* 字面值 *)
NUMBER       ::= [0-9]+ ('.' [0-9]+)?
STRING       ::= '"' ([^"\\] | escape)* '"'
              | '『' ([^』\\] | escape)* '』'
IDENT        ::= [a-zA-Z_] [a-zA-Z0-9_]*
              | CJK_CHAR+
escape       ::= '\\' ['"\\nrt]
```

### 14.2 First/Follow 集合

对于递归下降解析器，每个非终结符的 First 集合：

| 非终结符 | First |
|----------|-------|
| `program` | `` `定` `` `` `设` `` `` `遍历` `` `` `当` `` `` `入` `` `` `出` `` `` `真` `` `` `假` `` `` `空` `` `` `「` `` `` `列` `` `` `函` `` `` `$` `` `` `{{` `` NUMBER, STRING, IDENT |
| `statement` | `` `定` `` `` `设` `` `` `遍历` `` `` `当` `` `` `入` `` `` `出` `` 同上 |
| `expr` | `` `若` `` `` `真` `` `` `假` `` `` `空` `` `` `「` `` `` `列` `` `` `函` `` `` `$` `` `` `{{` `` NUMBER, STRING, IDENT |
| `unary_expr` | `` `负` `` `` `非` `` 同上（减去 `幂`） |
| `primary_expr` | `` `真` `` `` `假` `` `` `空` `` `` `「` `` `` `列` `` `` `函` `` `` `$` `` `` `{{` `` NUMBER, STRING, IDENT |

### 14.3 歧义性与消歧规则

语言的语法存在以下潜在歧义，需要通过上下文消除：

1. **管道与逗号表达式**：`expr , expr` 既可解释为管道操作，也可解释为函数调用的可变参数
   - **消歧规则**：若 `` `，` `` 左侧是列表字面量或函数调用结果，则为管道；否则需要显式括号

2. **负号与减号**：`负5` vs `5减3`
   - **消歧规则**：一元 `负` 仅在表达式开头或括号后出现；二元 `减` 需要左右操作数

3. **函数调用与变量名**：`印x` 可能是函数调用，也可能是变量名后跟另一个变量
   - **消歧规则**：查环境字典，若 `印` 是函数则解释为调用；否则报错

---

## 十五、类型系统

### 15.1 类型层次

语言采用**动态类型系统**，所有值都属于以下类型层次：

```
类型层次
├── 数 (Number)
│   ├── 整数 (Int)
│   └── 浮点数 (Float)
├── 串 (String)
├── 表 (List)
├── 函 (Function)
├── 真 (Boolean)
├── 空 (Nil)
└─ 任意 (Any) — 顶层类型，所有类型都是 Any 的子类型
```

### 15.2 类型检查规则

| 操作 | 类型要求 | 结果类型 |
|------|----------|----------|
| `` `加` `` | 数 × 数 | 数 |
| `` `加` `` | 串 × 串 | 串 |
| `` `减乘除模幂` `` | 数 × 数 | 数 |
| `` `大 小 等 不等` `` | 数 × 数 | 真 |
| `` `且 或` `` | 真 × 真 | 真 |
| `` `非` `` | 真 | 真 |
| `` `负` `` | 数 | 数 |
| `` `列` `` | 任意* | 表 |
| `` `长` `` | 表 | 数 |
| `` `入` `` | 数 × 表 | 任意 |
| `` `首 余` `` | 表 | 任意 |

类型错误示例：

```yan
定x="hello"。
定y=x加1。  -- 错误：串不能加数
```

### 15.3 类型标注语法

语言支持可选的类型标注（用于文档和静态检查）：

```yan
定 f :: (数, 数) -> 数
定 f=函a b加a b。

定 列表 :: 表
定 列表=列1 2 3。
```

类型标注不参与运行时检查，仅作为文档和 IDE 提示。

### 15.4 类型错误消息

```
[类型错误] 第3行: 操作「加」类型不匹配
    期望: 数 × 数
    实际: 串 × 数
    源码: 定y=x加1。
               ^
```

---

## 十六、测试框架

### 16.1 测试语法

```yan
测试"加法测试":
  断言 5加3 等于 8。
  断言 0加0 等于 0。
  断言 负5加10 等于 5。
。

测试"阶乘测试":
  断言 阶乘5 等于 120。
  断言 阶乘0 等于 1。
  断言 阶乘1 等于 1。
。

测试"列表测试":
  断言 列1 2 3，长 等于 3。
  断言 列1 2 3，首 等于 1。
  断言 列1 2 3，余 等于 列2 3。
。

测试"管道测试":
  断言 10加5，乘2 等于 30。
  断言 列1 2 3，皆乘2 等于 列2 4 6。
.
```

### 16.2 断言语法

```yan
断言 <expr> 等于 <expected>。
断言 <expr> 不等于 <expected>。
断言 <expr> 大于 <expected>。
断言 <expr> 小于 <expected>。
断言 <expr> 为真。
断言 <expr> 为假。
断言 <expr> 为空。
```

### 16.3 测试执行

```yan
运行测试。  -- 运行所有测试

定结果=测试"阶乘测试"。  -- 运行指定测试
印结果。
```

### 16.4 测试输出格式

```
运行测试: 加法测试
  ✅ 5加3等于8
  ✅ 0加0等于0
  ✅ 负5加10等于5
通过 (3/3)

运行测试: 阶乘测试
  ✅ 阶乘5等于120
  ✅ 阶乘0等于1
  ❌ 阶乘1等于2 (预期: 1)
失败 (2/3)

总计: 5通过, 1失败
```

---

## 十七、国际化与本地化

### 17.1 错误消息本地化

错误消息支持多语言显示：

```yan
设语言为"中文"。  -- 或 "English"
```

### 17.2 错误消息模板

```python
ErrorMessages = {
    "中文": {
        "未定义变量": "变量「{name}」未定义，请先使用「定{name}=...」定义",
        "除零错误": "除数不能为零",
        "类型不匹配": "操作「{op}」类型不匹配，期望「{expected}」，实际「{actual}」",
        "索引越界": "索引「{index}」超出范围，列表长度为「{length}」",
        "语法错误": "语法错误：{reason}",
        "文件不存在": "文件「{filename}」不存在",
    },
    "English": {
        "未定义变量": "Undefined variable: {name}",
        "除零错误": "Division by zero",
        "类型不匹配": "Type mismatch for operator「{op}」: expected「{expected}」, got「{actual}」",
        "索引越界": "Index {index} out of bounds, list length is {length}",
        "语法错误": "Syntax error: {reason}",
        "文件不存在": "File not found: {filename}",
    }
}
```

### 17.3 运行时提示本地化

数字、日期等本地化显示：

```yan
印 格式化数字 1234567。  -- 中文: 1,234,567
印 格式化日期 当前时间。  -- 中文: 2026年5月4日
```

---

## 十八、序列化与数据格式

### 18.1 JSON 支持

```yan
定数据={
  "name": "张三",
  "age": 25,
  "scores": [90, 85, 92]
}。

定文本=转JSON数据。
印文本。

定解析后=解析JSON('{"x":1,"y":2}').
印 解析后["x"]。
```

### 18.2 数据字面量

支持简洁的对象/字典字面量：

```yan
定人{
  名字: "李四",
  年龄: 30,
  职业: "工程师"
}。

印 人["名字"]。
```

---

## 十九、运行时系统

### 19.1 内存布局

```
┌─────────────────────────────────────────┐
│ 栈帧 (Stack)                            │
├─────────────────────────────────────────┤
│ main                                     │
│  ├─ x: 10 (整数)                        │
│  ├─ f: <函数 阶乘>                      │
│  └─ 临时: 120                           │
├─────────────────────────────────────────┤
│ 堆 (Heap)                               │
├─────────────────────────────────────────┤
│ [1, 2, 3]      ── 表对象                │
│ "hello"        ── 字符串对象            │
│ <函数 阶乘>    ── 函数闭包              │
└─────────────────────────────────────────┘
```

### 19.2 垃圾回收策略

语言采用**引用计数 + 标记清除**混合策略：

- **引用计数**：即时回收无引用的小对象（字符串、小列表）
- **标记清除**：定期执行，回收循环引用对象

```yan
定 x=列1 2 3。  -- 创建列表，引用计数=1
定 y=x。         -- 引用计数=2
设x=空。         -- 引用计数=1，仍不回收
设y=空。         -- 引用计数=0，即时回收
```

### 19.3 调用约定

- 参数通过栈传递
- 返回值通过寄存器/栈传递
- 调用者清理栈（cdecl风格）

### 19.4 尾调用优化

`` `函` `` 支持尾调用优化，尾递归不会导致栈溢出：

```yan
定阶乘=函n acc:
  若n等0则acc否则阶乘n减1acc乘n。
。

定 result=阶乘10000 1。  -- 不会栈溢出
```

---

## 二十、开发里程碑

### MVP (v0.1)
- 预分词层（类型切换 + 贪心匹配）
- 词法分析器
- 语法分析器（动宾吞噬 + 管道构建）
- 求值器（算术 + 管道）
- 能跑通：`` `10加5，乘2。` ``

### v0.2
- 列表 `` `列` `` 与高阶函数 `` `皆` `` `` `只` `` `` `归` ``
- 柯里化
- 能跑通：`` `列1 2 3，皆乘2。` ``

### v0.3
- 条件判断 `` `若` `` `` `则` `` `` `否则` ``
- 变量定义 `` `定` `` `` `设` ``
- 函数定义 `` `函` ``
- 能跑通：`` `定阶乘=函n若n等1则1否则n乘阶乘n减1。` ``

### v0.4
- 块结构 `` `：` `` `` `。` ``
- 循环 `` `遍历` `` `` `当` ``
- 能跑通：块结构递归函数

### v0.5
- 双轨制 `` `$()` `` `` `{{}}` ``
- 同像性 `` `「」` `` `` `行` ``
- 完整标准库

### v0.6
- REPL 交互式环境
- 错误信息中文化
- 调试模式

---

## 二十一、完整示例程序

### 21.1 阶乘计算器

```yan
定阶乘=函n：
  若n等0则1否则n乘阶乘n减1。
。

定主程序=函：
  定n=5。
  定结果=阶乘n。
  印 格式化"5的阶乘是{}"结果。
。

主程序。
```

### 21.2 数据处理管道

```yan
定数据=列1 2 3 4 5 6 7 8 9 10。

定处理结果=数据，
  皆乘2，
  只大10，
  归加0。

印处理结果。  -- 输出：54（12+14+16+18+20）
```

### 21.3 斐波那契数列

```yan
定斐波那契=函n：
  若n小2则n否则斐波那契n减1加斐波那契n减2。
。

定数列=范围10，皆斐波那契。
印数列。  -- 输出：[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### 21.4 文件处理

```yan
定内容=读文件"input.txt"。
定行=分割内容"\n"。
定非空行=行，只非空。
定行数=非空行，长。

印 格式化"文件有{}行"行数。
```

---

## 二十二、标准库扩展

### 22.1 集合操作

| 函数 | 元数 | 语义 | 示例 |
|------|:---:|------|------|
| `` `并集` `` | 2 | 集合合并 | `` `并集列1 2 3列2 3 4` `` `→` [1,2,3,4] |
| `` `交集` `` | 2 | 集合交集 | `` `交集列1 2 3列2 3 4` `` `→` [2,3] |
| `` `差集` `` | 2 | 集合差集 | `` `差集列1 2 3列2 3 4` `` `→` [1] |
| `` `唯一` `` | 1 | 去重 | `` `唯一列1 2 2 3` `` `→` [1,2,3] |
| `` `排序` `` | 1 | 排序 | `` `排序列3 1 2` `` `→` [1,2,3] |

### 22.2 数学统计

| 函数 | 元数 | 语义 | 示例 |
|------|:---:|------|------|
| `` `求和` `` | 1 | 列表求和 | `` `求和列1 2 3` `` `→` 6 |
| `` `求积` `` | 1 | 列表求积 | `` `求积列1 2 3` `` `→` 6 |
| `` `均值` `` | 1 | 平均值 | `` `均值列1 2 3` `` `→` 2 |
| `` `中位数` `` | 1 | 中位数 | `` `中位数列1 2 3` `` `→` 2 |
| `` `标准差` `` | 1 | 标准差 | `` `标准差列1 2 3` `` `→` 0.816 |

### 22.3 日期时间扩展

| 函数 | 元数 | 语义 | 示例 |
|------|:---:|------|------|
| `` `今日` `` | 0 | 今天日期 | `` `今日` `` `→` "2026-05-05" |
| `` `此刻` `` | 0 | 当前时间 | `` `此刻` `` `→` "15:30:00" |
| `` `星期` `` | 1 | 获取星期几 | `` `星期今日` `` `→` "星期一" |
| `` `加天数` `` | 2 | 日期加天数 | `` `加天数今日7` `` `→` "2026-05-12" |

---

## 二十三、实现指南

### 23.1 项目结构

```
yan/
├── lexer.py        # 预分词层 + 词法分析器
├── parser.py       # 语法分析器（递归下降）
├── ast.py          # AST节点定义
├── evaluator.py    # 求值器
├── stdlib.py       # 标准库
├── repl.py         # REPL环境
├── tests/          # 测试用例
└── examples/       # 示例程序
```

### 23.2 核心实现要点

#### 23.2.1 求值器核心循环

```python
def evaluate(node, env):
    if isinstance(node, Num):
        return node.value
    elif isinstance(node, Str):
        return node.value
    elif isinstance(node, Bool):
        return node.value
    elif isinstance(node, Word):
        return env.get(node.name)
    elif isinstance(node, Call):
        func = evaluate(node.verb, env)
        args = [evaluate(arg, env) for arg in node.args]
        if callable(func):
            return func(*args)
        else:
            raise RuntimeError(f"{func} 不是函数")
    elif isinstance(node, Pipeline):
        result = None
        for step in node.steps:
            if result is None:
                result = evaluate(step, env)
            else:
                step_result = evaluate(step, env)
                if callable(step_result):
                    result = step_result(result)
                else:
                    result = step_result
        return result
    # ... 其他节点类型
```

#### 23.2.2 柯里化实现

```python
def curry(func, args, arity):
    if len(args) >= arity:
        return func(*args)
    else:
        def partial(*more_args):
            all_args = list(more_args) + list(args)
            if len(all_args) >= arity:
                return func(*all_args)
            else:
                return curry(func, all_args, arity)
        return partial
```

### 23.3 测试驱动开发

建议采用测试驱动开发，按以下顺序实现：

1. **词法测试**：验证分词正确性
2. **语法测试**：验证AST构建正确
3. **求值测试**：验证基本运算
4. **集成测试**：验证完整程序

---

---

## 二十五、字节码与虚拟机设计

### 25.1 字节码指令集

| 指令 | 操作码 | 操作数 | 语义 |
|------|:---:|:---:|------|
| `PUSH_NUM` | 0x01 | n | 将数字n压栈 |
| `PUSH_STR` | 0x02 | idx | 将字符串表中idx位置的字符串压栈 |
| `PUSH_VAR` | 0x03 | idx | 将变量表中idx位置的变量压栈 |
| `PUSH_FUNC` | 0x04 | idx | 将函数表中idx位置的函数压栈 |
| `POP` | 0x05 | 0 | 弹出栈顶元素 |
| `DUP` | 0x06 | 0 | 复制栈顶元素 |
| `SWAP` | 0x07 | 0 | 交换栈顶两个元素 |
| `ADD` | 0x10 | 0 | 弹出两个数相加，结果压栈 |
| `SUB` | 0x11 | 0 | 弹出两个数相减，结果压栈 |
| `MUL` | 0x12 | 0 | 弹出两个数相乘，结果压栈 |
| `DIV` | 0x13 | 0 | 弹出两个数相除，结果压栈 |
| `CALL` | 0x20 | nargs | 调用函数，弹出nargs个参数 |
| `JUMP` | 0x30 | offset | 无条件跳转到offset |
| `JUMP_IF_FALSE` | 0x31 | offset | 若栈顶为假则跳转 |
| `RET` | 0x40 | 0 | 返回栈顶值 |

### 25.2 AST到字节码的编译

```python
def compile(node):
    if isinstance(node, Num):
        return [0x01, node.value]
    elif isinstance(node, Str):
        string_table.append(node.value)
        return [0x02, len(string_table)-1]
    elif isinstance(node, Call):
        code = []
        for arg in node.args:
            code += compile(arg)
        code += compile(node.verb)
        code += [0x20, len(node.args)]
        return code
    # ... 其他节点类型
```

### 25.3 虚拟机运行时

```python
class VirtualMachine:
    def __init__(self, bytecode, string_table, func_table):
        self.stack = []
        self.bytecode = bytecode
        self.string_table = string_table
        self.func_table = func_table
        self.pc = 0
    
    def run(self):
        while self.pc < len(self.bytecode):
            opcode = self.bytecode[self.pc]
            if opcode == 0x01:  # PUSH_NUM
                self.stack.append(self.bytecode[self.pc+1])
                self.pc += 2
            elif opcode == 0x10:  # ADD
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
                self.pc += 1
            elif opcode == 0x20:  # CALL
                nargs = self.bytecode[self.pc+1]
                args = [self.stack.pop() for _ in range(nargs)][::-1]
                func = self.stack.pop()
                result = func(*args)
                self.stack.append(result)
                self.pc += 2
            # ... 其他指令
```

---

## 二十六、FFI互操作规范

### 26.1 数据类型转换

| 言类型 | Python类型 | C类型 |
|--------|-----------|-------|
| 数 | int/float | int/double |
| 串 | str | char* |
| 表 | list | PyObject* |
| 函 | callable | PyObject* |
| 真 | bool | int |
| 空 | None | NULL |

### 26.2 Python嵌入语法

```yan
定结果={{
    import numpy as np
    arr = np.array([1, 2, 3])
    return arr.sum()
}}。

印结果。  -- 输出：6
```

### 26.3 回调机制

```yan
定回调=函x：
  印"收到："x。
。

{{
    def process(callback):
        callback("hello from Python")
    process(callback)
}}。
```

---

## 二十七、包管理器与依赖管理

### 27.1 包结构

```
mypackage/
├── yan.toml          # 包元数据
├── src/
│   └── main.yan      # 主模块
├── tests/            # 测试目录
└── README.md         # 说明文档
```

### 27.2 包元数据格式

```toml
[package]
name = "mypackage"
version = "1.0.0"
description = "一个示例包"
author = "作者"
license = "MIT"

[dependencies]
core = ">=1.0.0"
math = "1.2.3"
```

### 27.3 模块导入语法

```yan
入文件"utils.yan"。
入函数"阶乘"自"math"。
入全部自"data"为d。
```

---

## 二十八、IDE扩展与LSP支持

### 28.1 语言服务器协议(LSP)实现

| LSP功能 | 支持 | 说明 |
|---------|:---:|------|
| 代码补全 | ✅ | 基于上下文的智能补全 |
| 语法高亮 | ✅ | 关键字、函数、变量着色 |
| 跳转到定义 | ✅ | 变量/函数定义定位 |
| 悬停提示 | ✅ | 显示类型和文档 |
| 错误诊断 | ✅ | 实时语法检查 |

### 28.2 语法高亮配色

| 元素 | 建议颜色 |
|------|----------|
| 关键字 | #994500 |
| 函数名 | #0086b3 |
| 变量名 | #333333 |
| 字符串 | #183691 |
| 数字 | #008080 |
| 注释 | #6a9955 |

### 28.3 调试器集成

```yan
断点在阶乘。
运行。
→ 断点: 阶乘(5)
单步。
→ 阶乘(4)
看变量n。
→ n = 4
```

---

## 二十九、并发模型

### 29.1 协程支持

```yan
定任务=协():
  等网络取"http://example.com"。
  印结果。
。

定主程序=函：
  启动任务。
  印"任务已启动"。
。
```

### 29.2 并行操作

```yan
定结果=列1 2 3，皆并行乘2。  -- 并行处理
印结果。  -- 输出：[2, 4, 6]
```

### 29.3 通道通信

```yan
定通道=通道()。

协():
  发送通道"hello"。
。

协():
  定消息=接收通道。
  印消息。
。
```

---

## 三十、开发者体验

### 30.1 渐进式错误提示

```
错误：变量「x」未定义

[基础提示]：请先使用「定x=...」定义变量
[进阶提示]：检查是否拼写错误，或确认变量作用域
[示例]：定x=10。印x。
```

### 30.2 代码格式化工具

```yan
格式文件"main.yan"。  -- 自动格式化
```

### 30.3 静态检查器

```yan
检查文件"main.yan"。  -- 检查潜在问题
```

---

## 三十一、统一字符处理标准

### 31.1 字符分类定义

```python
META    = '。'，'，'，'：'，'「'，'」'，'『'，'』'，'（'，'）'，'【'，'】'，'《'，'》'，'——'，'……'

NUM     = '0'-'9'，'.'，'𝟙'，'𝟚'，'𝟛'  # 半角和全角数字

HAN     = CJK统一表意文字 (U+4E00-U+9FFF)
        + CJK符号和标点 (U+3000-U+303F)
        + CJK兼容表意文字 (U+F900-U+FAFF)

LATIN   = 'a'-'z'，'A'-'Z'，'_'

SPACE   = '　'（全角空格），' '（半角空格），'\t'，'\n'，'\r'
```

### 31.2 Unicode完全支持

```yan
定中文变量=123。  -- 中文变量名
定变量名="中文"。  -- 中文字符串
印"你好世界"。    -- 中文输出
```

### 31.3 全角半角混用处理

```yan
定x＝10。          -- 全角等号，等价于 x=10
如果x>5那么：      -- 全角符号均可
  印"大于5"。
否则：
  印"小于等于5"。
。
```

---

## 三十二、动词副词语义表

### 32.1 词类体系

| 词类 | 标记 | 示例 | 作用 |
|------|------|------|------|
| **核心动词** | `v` | `` `加` `` `` `减` `` `` `乘` `` `` `除` `` `` `等` `` `` `印` `` | 基本操作 |
| **内置副词** | `adv` | `` `皆` `` `` `只` `` `` `归` `` | 高阶操作修饰符 |
| **流控制词** | `control` | `` `若` `` `` `则` `` `` `否则` `` `` `遍历` `` `` `当` `` | 流程控制 |
| **构建词** | `construct` | `` `列` `` `` `「` `` `` `函` `` `` `定` `` `` `设` `` | 数据/代码构建 |
| **类型词** | `type` | `` `数` `` `` `串` `` `` `表` `` `` `函` `` `` `真` `` `` `假` `` `` `空` `` | 类型表示 |

### 32.2 核心动词表

| 动词 | 元数 | 语义 | 类型签名 |
|------|:---:|------|----------|
| `` `加` `` | 2 | 加法 | `` `数 × 数 → 数` `` |
| `` `减` `` | 2 | 减法 | `` `数 × 数 → 数` `` |
| `` `乘` `` | 2 | 乘法 | `` `数 × 数 → 数` `` |
| `` `除` `` | 2 | 除法 | `` `数 × 数 → 数` `` |
| `` `幂` `` | 2 | 幂运算 | `` `数 × 数 → 数` `` |
| `` `模` `` | 2 | 取模 | `` `数 × 数 → 数` `` |
| `` `负` `` | 1 | 负号 | `` `数 → 数` `` |
| `` `大` `` | 2 | 大于 | `` `数 × 数 → 真` `` |
| `` `小` `` | 2 | 小于 | `` `数 × 数 → 真` `` |
| `` `等` `` | 2 | 等于 | `` `任意 × 任意 → 真` `` |
| `` `不等` `` | 2 | 不等 | `` `任意 × 任意 → 真` `` |
| `` `且` `` | 2 | 逻辑与 | `` `真 × 真 → 真` `` |
| `` `或` `` | 2 | 逻辑或 | `` `真 × 真 → 真` `` |
| `` `非` `` | 1 | 逻辑非 | `` `真 → 真` `` |
| `` `印` `` | 1 | 打印 | `` `任意 → 空` `` |
| `` `长` `` | 1 | 长度 | `` `表 → 数` `` |
| `` `首` `` | 1 | 列表首元素 | `` `表 → 任意` `` |
| `` `余` `` | 1 | 列表剩余 | `` `表 → 表` `` |

### 32.3 内置副词表

| 副词 | 修饰 | 语义 | 示例 |
|------|------|------|------|
| `` `皆` `` | 一元函数 | 映射：每个元素应用函数 | `` `列1 2 3，皆乘2` `` `→` [2,4,6] |
| `` `只` `` | 一元函数谓词 | 过滤：保留满足条件的元素 | `` `列1 2 3，只大1` `` `→` [2,3] |
| `` `归` `` | 二元函数 | 归约：折叠为单一值 | `` `列1 2 3，归加0` `` `→` 6 |
| `` `并` `` | 列表 | 拼接两个列表 | `` `列1 2 并 列3 4` `` `→` [1,2,3,4] |

---

## 三十三、AST序列化与调试

### 33.1 AST序列化

```python
class ASTEncoder(json.JSONEncoder):
    """AST序列化为JSON以便调试"""
    def default(self, obj):
        if isinstance(obj, Node):
            result = {'__type__': obj.__class__.__name__}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    if isinstance(value, Node):
                        result[key] = self.default(value)
                    elif isinstance(value, list):
                        result[key] = [self.default(item) for item in value]
                    else:
                        result[key] = value
            return result
        return super().default(obj)
```

### 33.2 错误位置追踪

```python
class SourceLocation:
    """源代码位置追踪"""
    def __init__(self, filename, start_line, start_col, end_line=None, end_col=None):
        self.filename = filename
        self.start_line = start_line
        self.start_col = start_col
        self.end_line = end_line if end_line else start_line
        self.end_col = end_col if end_col else start_col
    
    def __str__(self):
        return f"{self.filename}:{self.start_line}:{self.start_col}-{self.end_line}:{self.end_col}"

class Node:
    def __init__(self, location: SourceLocation):
        self.location = location
```

### 33.3 错误输出格式

```
[类型错误] 源码.yan:5:10-5:15
    操作「加」类型不匹配
    期望: 数 × 数
    实际: 串 × 数
    源码:     定y=x加1。
                       ^^^^^
```

---

## 三十四、编程范例模式库

### 34.1 MapReduce模式

```yan
定总和=列1到10，皆乘2，只大10，归加0。
印总和。
```

### 34.2 数据处理管道

```yan
数据来源。
清洗。
转换。
分析。
可视化。
```

### 34.3 资源自动管理

```yan
用文件「数据.txt」为输入：
  内容=读取输入。
  写文件「结果.txt」以内容。
。
```

### 34.4 错误处理模式

```yan
试：
  结果=风险操作。
捕获「文件不存在」则：
  印"文件不存在，使用默认值"。
  结果=默认值。
终：
  释放资源。
。
```

---

## 三十五、代码样式规范

### 35.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | 名词短语 | `` `学生分数` `` `` `总金额` `` |
| 函数 | 动词短语 | `` `计算平均值` `` `` `过滤无效项` `` |
| 常量 | 全大写用`_` | `` `最大宽度` `` `` `默认超时` `` |
| 模块 | 简短名词 | `` `数学` `` `` `文件` `` `` `网络` `` |

### 35.2 格式规则

```yan
-- 管道操作每行一个
定结果=数据，
  映射，
  过滤，
  归约。

-- 缩进使用2个空格

-- 复杂函数使用空行分段
定复杂函数=函参数：
  -- 步骤1
  中间结果=步骤1处理参数。

  -- 步骤2
  最终结果=步骤2处理中间结果。

  返回最终结果。
。
```

---

## 三十六、快速入门小抄

### 36.1 基本运算

| 代码 | 结果 |
|------|------|
| `` `5加3` `` | 8 |
| `` `真且假` `` | 假 |
| `` `负5` `` | -5 |
| `` `10除3` `` | 3.333 |

### 36.2 变量与函数

| 代码 | 说明 |
|------|------|
| `` `定x=10` `` | 定义变量 |
| `` `设x=15` `` | 修改变量 |
| `` `定f=函x x加1` `` | 定义函数 |

### 36.3 流程控制

| 代码 | 说明 |
|------|------|
| `` `若条件则A否则B` `` | 条件判断 |
| `` `遍历i从1到10: ...` `` | 循环 |
| `` `当条件时: ...` `` | 当循环 |

### 36.4 数据处理

| 代码 | 说明 |
|------|------|
| `` `列1 2 3，皆乘2` `` | 映射 |
| `` `列1 2 3，只大1` `` | 过滤 |
| `` `列1 2 3，归加0` `` | 归约 |

### 36.5 特殊语法

| 代码 | 说明 |
|------|------|
| `` `$`(1+2*3) `` | 数学表达式 |
| `` `{{python代码}}` `` | Python嵌入 |
| `` `「表达式」` `` | 引用不求值 |
| `` `行「表达式」` `` | 执行引用 |

---

## 三十七、常见陷阱与解决方法

### 37.1 无空格歧义

**问题**：`` `10加 5` `` (带空格) vs `` `10加5` `` (无空格)

**解决**：预分词自动处理，编程时完全忽略空格

### 37.2 柯里化参数顺序

**问题**：`函a b 加a b` 柯里化后是 `λa. λb. a+b`

**解释**：动词吞噬是从左到右收集参数，参数顺序需要理解

### 37.3 列表操作返回新列表

**特性**：所有列表操作都返回新列表，原列表不变

**对比**：`设列表=列添加4列表`，不是原地修改

### 37.4 定与设的严格区别

**规则**：`定`只能定义新变量，`设`只能修改已定义变量

**设计哲学**：防止意外覆盖，明确代码意图

---

## 三十八、版本管理语义

### 38.1 版本格式

版本格式：`主.次.修订`

| 级别 | 说明 | 兼容性 |
|------|------|--------|
| **主版本** (v**X**.0.0) | 不兼容的重大变更 | 不兼容 |
| **次版本** (v0.**X**.0) | 向前兼容的功能添加 | 兼容 |
| **修订版本** (v0.0.**X**) | bug修复，无新功能 | 完全兼容 |

### 38.2 发布计划

| 版本 | 里程碑 |
|------|--------|
| v0.1.0 | MVP发布（基本运算、管道、变量） |
| v0.2.0 | 添加列表、高阶函数 |
| v0.3.0 | 添加条件语句、函数定义 |
| v0.4.0 | 循环、标准库 |
| v0.5.0 | 双轨制、同像性 |
| v0.6.0 | REPL、调试器 |

---

## 三十九、真实场景示例

### 39.1 网络爬虫

```yan
定爬取页面=函网址：
  响应=请求网址。
  内容=响应体。
  标题=提取标题内容。
  返回标题。
。

定主程序=函：
  网址列表=列
    "https://example.com",
    "https://example.org",
    "https://example.net"
  。
  
  结果=网址列表，皆爬取页面。
  印结果。
。

主程序。
```

### 39.2 数据处理管道

```yan
定数据处理=函：
  原始数据=读取文件"data.csv"。
  行=分割原始数据"\n"。
  表头=行首，分割","。
  数据行=行余。
  
  处理后=数据行，
    皆分割",",
    皆转数字，
    只非空，
    归合并表。
  
  写入文件"output.json"以转JSON处理后。
。

数据处理。
```

### 39.3 Web服务

```yan
定处理请求=函请求：
  路径=请求路径。
  若路径等"/hello"则：
    返回响应200内容"你好世界"。
  否则：
    返回响应404内容"未找到"。
  。
。

启动服务器8080处理请求。
```

### 39.4 小游戏：猜数字

```yan
定猜数字游戏=函：
  秘密数字=随机整数1到100。
  尝试次数=0。
  
  当真时：
    输入=获取用户输入"猜一个1-100的数字："。
    猜测=转数字输入。
    设尝试次数=尝试次数加1。
    
    若猜测等秘密数字则：
      印 格式化"恭喜！你用了{}次猜对了"尝试次数。
      跳出循环。
    否则若猜测小秘密数字则：
      印"太小了！"。
    否则：
      印"太大了！"。
    。
  。
。

猜数字游戏。
```

---

## 四十、性能分析与调试工具

### 40.1 性能分析

```yan
导入「基准测试」。

定测试性能=函：
  开始=时间戳。
  
  结果=重复1000次：
    计算复杂操作。
  。
  
  结束=时间戳。
  持续时间=结束减开始。
  
  印 格式化"耗时：{}毫秒"持续时间乘1000。
。

测试性能。
```

### 40.2 内存调试

```yan
激活内存跟踪。

运行程序。

显示内存统计：
  对象类型：串，数量：15，占用：480字节
  对象类型：表，数量：3，占用：120字节
  对象类型：闭包，数量：7，占用：280字节
。

禁用内存跟踪。
```

### 40.3 代码覆盖率

```yan
运行测试覆盖。

报告覆盖率：
  文件：main.yan，覆盖：85%
  文件：utils.yan，覆盖：92%
。
```

---

## 四十一、互操作示例

### 41.1 Python调用言

```python
import yan

calc = yan.load("""
定计算=函x y：
  结果=x加y乘2。
  返回结果。
。
""")

result = calc(3, 4)  # 11
print(result)
```

### 41.2 言调用Python

```yan
定数据分析=函数据：
  使用Python库为pandas：
    数据框=表到数据框数据。
    分析结果=计算统计量数据框。
    返回分析结果。
  。
。

定数据=列
  行「姓名」「年龄」「分数」，
  行「张三」25 90，
  行「李四」30 85，
  行「王五」28 95，
。

定结果=数据分析数据。
印结果。
```

### 41.3 数据类型转换

| 言类型 | Python类型 | 转换示例 |
|--------|-----------|----------|
| 数 | int/float | `` `5` `` → `5` |
| 串 | str | `` `"hello"` `` → `"hello"` |
| 表 | list | `` `列1 2 3` `` → `[1, 2, 3]` |
| 函 | callable | `` `函x x加1` `` → `<function>` |

---

## 四十二、迁移指南

### 42.1 从Python迁移

```python
# Python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)
```

```yan
# 言
定阶乘=函n：
  若n等0则1否则n乘阶乘n减1。
。
```

### 42.2 从JavaScript迁移

```javascript
// JavaScript
const sum = arr.reduce((acc, x) => acc + x, 0);
```

```yan
// 言
定总和=列，归加0。
```

### 42.3 语法对比表

| 特性 | Python | JavaScript | 言 |
|------|--------|-----------|----|
| 变量定义 | `x = 10` | `let x = 10` | `` `定x=10` `` |
| 条件判断 | `if x: ...` | `if (x) { ... }` | `` `若x则...` `` |
| 函数定义 | `def f(): ...` | `function f() {}` | `` `定f=函...` `` |
| 列表操作 | `map(f, lst)` | `arr.map(f)` | `` `列表，皆f` `` |

---

## 四十三、修订历史

- v1.0 (2026-05-03): 综合言叶、文言心、言三个项目，制定统一语法规范
- v1.1 (2026-05-03): 添加文档约定章节，区分语言语法与文档标注；添加LaTeX公式支持
- v1.2 (2026-05-04): 添加运算符优先级、语法分析器实现、错误处理规范、标准库设计、模块系统、测试用例、性能考量
- v1.3 (2026-05-04): 添加完整EBNF形式文法、类型系统、测试框架、国际化本地化、序列化数据格式、运行时系统
- v1.4 (2026-05-05): 添加完整示例程序、标准库扩展、实现指南
- v1.5 (2026-05-05): 添加字节码虚拟机、FFI互操作、包管理器、LSP支持、并发模型、开发者体验
- v1.6 (2026-05-05): 添加统一字符标准、动词副词语义表、AST序列化调试、编程模式库、代码样式规范、快速入门小抄、常见陷阱、版本管理语义
- v1.7 (2026-05-05): 添加真实场景示例、性能分析工具、内存调试、互操作示例、迁移指南