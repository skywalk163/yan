# 词法分析器 模块 API 文档

---

## 类: `Lexer`

**行号**: 74

### 描述

> 词法分析器：无空格分词 + 多字贪心匹配

### 方法

#### `__init__(keywords, user_words)`

**行号**: 111


#### `_create_han_check()`

**行号**: 152

> 创建优化的汉字检查函数

#### `_create_ident_char_check()`

**行号**: 162

> 创建优化的标识符字符检查函数

#### `_scan_user_defs(source)`

**行号**: 171

> 轻量扫描：收集所有用户定义的函数名/变量名
> 
> 寻找 '定 X =' 或 '定 X = 函' 模式的标识符 X

#### `_is_han(ch)`

**行号**: 212

> 判断是否为汉字

#### `_is_ident_char(ch)`

**行号**: 219

> 判断是否为标识符字符（汉字或字母或下划线或数字）

#### `_try_match_surname(source, i)`

**行号**: 225

> 尝试匹配姓氏（支持复姓）

#### `_is_same_type(ch1, ch2)`

**行号**: 237

> 判断两个字符是否属于同一类型（用于分词）

#### `_is_chinese()`

**行号**: 253

> 检查字符是否是中文

#### `_create_error(message, line, col)`

**行号**: 257

> 创建增强版词法分析错误

#### `tokenize(source)`

**行号**: 263

> 将源码转为 Token 流（支持缩进语法和续行）

#### `_count_indent(line)`

**行号**: 398

> 计算行的缩进级别

#### `_tokenize_line(line, line_num, start_col, tokens, user_defined_names)`

**行号**: 410

> 处理单行的 token 化

#### `_match_keyword(line, pos, length)`

**行号**: 727

> 快速匹配关键字，返回匹配长度，未匹配返回0
> 
> 使用预计算的按长度分组的关键字集合进行高效查找

#### `_collect_chinese_identifier(line, start, length)`

**行号**: 742

> 收集连续的汉字标识符
> 
> 收集所有连续的汉字（可能包含数字后缀），然后检查是否匹配关键字
> 如果完整标识符匹配关键字，优先返回完整标识符
> 否则返回完整标识符作为一个整体（用户自定义变量名）

#### `_tokenize_raw(source, user_defined_names)`

**行号**: 761

> 生成基础 tokens（包含换行符和原始缩进信息）

#### `_process_indent(raw_tokens)`

**行号**: 1318

> 处理缩进，将原始缩进信息转换为 INDENT/DEDENT tokens
> 
> 规则：
> 1. 缩进增加 → 生成 INDENT
> 2. 缩进减少 → 生成相应数量的 DEDENT
> 3. 缩进不变 → 不生成任何 token

## 函数: `_create_han_check(self)`

**行号**: 152

### 描述

> 创建优化的汉字检查函数

## 函数: `_create_ident_char_check(self)`

**行号**: 162

### 描述

> 创建优化的标识符字符检查函数

## 函数: `_scan_user_defs(self, source)`

**行号**: 171

### 描述

> 轻量扫描：收集所有用户定义的函数名/变量名
> 
> 寻找 '定 X =' 或 '定 X = 函' 模式的标识符 X

## 函数: `_is_han(self, ch)`

**行号**: 212

### 描述

> 判断是否为汉字

## 函数: `_is_ident_char(self, ch)`

**行号**: 219

### 描述

> 判断是否为标识符字符（汉字或字母或下划线或数字）

## 函数: `_try_match_surname(self, source, i)`

**行号**: 225

### 描述

> 尝试匹配姓氏（支持复姓）

## 函数: `_is_same_type(self, ch1, ch2)`

**行号**: 237

### 描述

> 判断两个字符是否属于同一类型（用于分词）

## 函数: `_is_chinese(ch)`

**行号**: 253

### 描述

> 检查字符是否是中文

## 函数: `_create_error(self, message, line, col)`

**行号**: 257

### 描述

> 创建增强版词法分析错误

## 函数: `tokenize(self, source)`

**行号**: 263

### 描述

> 将源码转为 Token 流（支持缩进语法和续行）

## 函数: `_count_indent(self, line)`

**行号**: 398

### 描述

> 计算行的缩进级别

## 函数: `_tokenize_line(self, line, line_num, start_col, tokens, user_defined_names)`

**行号**: 410

### 描述

> 处理单行的 token 化

## 函数: `_match_keyword(self, line, pos, length)`

**行号**: 727

### 描述

> 快速匹配关键字，返回匹配长度，未匹配返回0
> 
> 使用预计算的按长度分组的关键字集合进行高效查找

## 函数: `_collect_chinese_identifier(self, line, start, length)`

**行号**: 742

### 描述

> 收集连续的汉字标识符
> 
> 收集所有连续的汉字（可能包含数字后缀），然后检查是否匹配关键字
> 如果完整标识符匹配关键字，优先返回完整标识符
> 否则返回完整标识符作为一个整体（用户自定义变量名）

## 函数: `_tokenize_raw(self, source, user_defined_names)`

**行号**: 761

### 描述

> 生成基础 tokens（包含换行符和原始缩进信息）

## 函数: `_process_indent(self, raw_tokens)`

**行号**: 1318

### 描述

> 处理缩进，将原始缩进信息转换为 INDENT/DEDENT tokens
> 
> 规则：
> 1. 缩进增加 → 生成 INDENT
> 2. 缩进减少 → 生成相应数量的 DEDENT
> 3. 缩进不变 → 不生成任何 token
