# Python 代码生成器 模块 API 文档

---

## 类: `PythonCodeGen`

**行号**: 29

### 描述

> Python 代码生成器

### 方法

#### `__init__()`

**行号**: 32


#### `generate(node)`

**行号**: 36

> 生成 Python 代码

#### `_gen_program(node)`

**行号**: 91

> 生成程序

#### `_gen_list(node)`

**行号**: 100

> 生成列表

#### `_gen_call(node, pipeline_arg)`

**行号**: 105

> 生成函数调用

#### `_gen_pipeline(node)`

**行号**: 175

> 生成管道

#### `_gen_quote(node)`

**行号**: 274

> 生成引用（返回 AST 的 Python 表示）

#### `_ast_to_dict(node)`

**行号**: 279

> 将 AST 节点转为字典

#### `_gen_define(node)`

**行号**: 320

> 生成定义语句

#### `_gen_tail_recursive_function(name, node)`

**行号**: 359

> 生成尾递归优化的函数（转换为循环）

#### `_convert_tail_recursion_to_loop(node, func_name, params)`

**行号**: 371

> 将尾递归转换为循环体

#### `_gen_def_function(name, node)`

**行号**: 404

> Generate a def function for Lambda with Block body

#### `_gen_def_function_from_code(name, params, body_code)`

**行号**: 433

> Generate a def function from generated body code

#### `_gen_lambda(node)`

**行号**: 447

> 生成匿名函数

#### `_gen_block(node)`

**行号**: 480

> 生成代码块

#### `_gen_if(node)`

**行号**: 490

> 生成条件表达式

#### `_gen_foreach(node)`

**行号**: 574

> 生成遍历循环

#### `_gen_while(node)`

**行号**: 598

> 生成当循环

#### `_gen_import(node)`

**行号**: 621

> 生成导入语句的 Python 代码

#### `_gen_export(node)`

**行号**: 631

> 生成导出语句的 Python 代码

#### `_gen_import_node(node)`

**行号**: 637

> 生成 ImportNode 节点的 Python 代码生成

#### `_gen_export_node(node)`

**行号**: 664

> 生成 ExportNode 节点的 Python 代码生成

#### `_gen_struct_def(node)`

**行号**: 681

> 生成结构体定义的 Python 代码

#### `_gen_struct_init(node)`

**行号**: 696

> 生成结构体实例化的 Python 代码

## 类: `OptimizedPythonCodeGen`

**行号**: 704

### 描述

> 带优化的 Python 代码生成器

### 方法

#### `__init__(config)`

**行号**: 707


#### `generate(node)`

**行号**: 717

> 生成优化后的 Python 代码

#### `get_optimization_stats()`

**行号**: 725

> 获取优化统计信息

## 函数: `generate(self, node)`

**行号**: 36

### 描述

> 生成 Python 代码

## 函数: `_gen_program(self, node)`

**行号**: 91

### 描述

> 生成程序

## 函数: `_gen_list(self, node)`

**行号**: 100

### 描述

> 生成列表

## 函数: `_gen_call(self, node, pipeline_arg)`

**行号**: 105

### 描述

> 生成函数调用

## 函数: `_gen_pipeline(self, node)`

**行号**: 175

### 描述

> 生成管道

## 函数: `_gen_quote(self, node)`

**行号**: 274

### 描述

> 生成引用（返回 AST 的 Python 表示）

## 函数: `_ast_to_dict(self, node)`

**行号**: 279

### 描述

> 将 AST 节点转为字典

## 函数: `_gen_define(self, node)`

**行号**: 320

### 描述

> 生成定义语句

## 函数: `_gen_tail_recursive_function(self, name, node)`

**行号**: 359

### 描述

> 生成尾递归优化的函数（转换为循环）

## 函数: `_convert_tail_recursion_to_loop(self, node, func_name, params)`

**行号**: 371

### 描述

> 将尾递归转换为循环体

## 函数: `_gen_def_function(self, name, node)`

**行号**: 404

### 描述

> Generate a def function for Lambda with Block body

## 函数: `_gen_def_function_from_code(self, name, params, body_code)`

**行号**: 433

### 描述

> Generate a def function from generated body code

## 函数: `_gen_lambda(self, node)`

**行号**: 447

### 描述

> 生成匿名函数

## 函数: `_gen_block(self, node)`

**行号**: 480

### 描述

> 生成代码块

## 函数: `_gen_if(self, node)`

**行号**: 490

### 描述

> 生成条件表达式

## 函数: `_gen_foreach(self, node)`

**行号**: 574

### 描述

> 生成遍历循环

## 函数: `_gen_while(self, node)`

**行号**: 598

### 描述

> 生成当循环

## 函数: `_gen_import(self, node)`

**行号**: 621

### 描述

> 生成导入语句的 Python 代码

## 函数: `_gen_export(self, node)`

**行号**: 631

### 描述

> 生成导出语句的 Python 代码

## 函数: `_gen_import_node(self, node)`

**行号**: 637

### 描述

> 生成 ImportNode 节点的 Python 代码生成

## 函数: `_gen_export_node(self, node)`

**行号**: 664

### 描述

> 生成 ExportNode 节点的 Python 代码生成

## 函数: `_gen_struct_def(self, node)`

**行号**: 681

### 描述

> 生成结构体定义的 Python 代码

## 函数: `_gen_struct_init(self, node)`

**行号**: 696

### 描述

> 生成结构体实例化的 Python 代码

## 函数: `generate(self, node)`

**行号**: 717

### 描述

> 生成优化后的 Python 代码

## 函数: `get_optimization_stats(self)`

**行号**: 725

### 描述

> 获取优化统计信息
