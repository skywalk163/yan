# 运行时系统 模块 API 文档

---

## 函数: `_eval(expr_str)`

**行号**: 61

### 描述

> 求值算术表达式字符串，支持加减乘除和括号

## 函数: `_range(n)`

**行号**: 166

### 描述

> 生成从0到n-1的列表

## 函数: `_set_nth(lst, n, value)`

**行号**: 178

### 描述

> 设置列表中指定索引的值

## 函数: `_concat()`

**行号**: 188

### 描述

> 连接多个参数，支持任意数量的参数

## 函数: `_map(func_or_lst, lst_or_func)`

**行号**: 220

### 描述

> 映射：支持柯里化
> 
> 用法：
> - _map(func, lst) -> list(map(func, lst))
> - _map(lst)(func) -> list(map(func, lst))  # 管道形式

## 函数: `_filter(pred, lst)`

**行号**: 246

### 描述

> 过滤：支持柯里化

## 函数: `_reduce(func_or_init, init_or_lst, lst)`

**行号**: 253

### 描述

> 归约：支持柯里化
> 
> 用法：
> - _reduce(func, init, lst) -> reduce(func, lst, init)
> - _reduce(func, init)(lst) -> reduce(func, lst, init)

## 函数: `curry(func, arity)`

**行号**: 281

### 描述

> 将函数转为可柯里化形式

## 函数: `_dict()`

**行号**: 292

### 描述

> 创建字典：典 'key1' val1 'key2' val2 或 典 key1 val1 key2 val2

## 函数: `_get(d, key)`

**行号**: 307

### 描述

> 获取字典中指定键的值

## 函数: `_read_char()`

**行号**: 329

### 描述

> 读取单个字符

## 类: `YanAssertionError`

**行号**: 621

### 描述

> 言语言断言错误

## 函数: `tokenize(s)`

**行号**: 66

### 描述

> 将表达式字符串分解为token

## 函数: `parse(tokens)`

**行号**: 89

### 描述

> 递归下降解析器
