# JavaScript 代码生成器 模块 API 文档

---

## 类: `JavaScriptCodeGen`

**行号**: 13

### 描述

> JavaScript 代码生成器

### 方法

#### `__init__()`

**行号**: 16


#### `generate(node)`

**行号**: 22

> 生成 JavaScript 代码

#### `_gen_program(node)`

**行号**: 73

> 生成完整的 JavaScript 程序

#### `_gen_helpers()`

**行号**: 88

> 生成 JavaScript 辅助函数

#### `_gen_list(node)`

**行号**: 220

> 生成列表

#### `_gen_call(node, pipeline_arg)`

**行号**: 225

> 生成函数调用

#### `_gen_pipeline(node)`

**行号**: 281

> 生成管道表达式

#### `_gen_quote(node)`

**行号**: 305

> 生成引用表达式

#### `_gen_define(node)`

**行号**: 311

> 生成变量定义

#### `_gen_lambda(node)`

**行号**: 322

> 生成匿名函数

#### `_gen_block(node)`

**行号**: 333

> 生成代码块

#### `_gen_if(node)`

**行号**: 342

> 生成条件语句

#### `_gen_foreach(node)`

**行号**: 367

> 生成遍历循环

#### `_gen_while(node)`

**行号**: 378

> 生成当循环

#### `_gen_import(node)`

**行号**: 388

> 生成导入语句

#### `_gen_export(node)`

**行号**: 393

> 生成导出语句

#### `_gen_struct_def(node)`

**行号**: 398

> 生成结构体定义

#### `_gen_struct_init(node)`

**行号**: 407

> 生成结构体初始化

## 函数: `generate(self, node)`

**行号**: 22

### 描述

> 生成 JavaScript 代码

## 函数: `_gen_program(self, node)`

**行号**: 73

### 描述

> 生成完整的 JavaScript 程序

## 函数: `_gen_helpers(self)`

**行号**: 88

### 描述

> 生成 JavaScript 辅助函数

## 函数: `_gen_list(self, node)`

**行号**: 220

### 描述

> 生成列表

## 函数: `_gen_call(self, node, pipeline_arg)`

**行号**: 225

### 描述

> 生成函数调用

## 函数: `_gen_pipeline(self, node)`

**行号**: 281

### 描述

> 生成管道表达式

## 函数: `_gen_quote(self, node)`

**行号**: 305

### 描述

> 生成引用表达式

## 函数: `_gen_define(self, node)`

**行号**: 311

### 描述

> 生成变量定义

## 函数: `_gen_lambda(self, node)`

**行号**: 322

### 描述

> 生成匿名函数

## 函数: `_gen_block(self, node)`

**行号**: 333

### 描述

> 生成代码块

## 函数: `_gen_if(self, node)`

**行号**: 342

### 描述

> 生成条件语句

## 函数: `_gen_foreach(self, node)`

**行号**: 367

### 描述

> 生成遍历循环

## 函数: `_gen_while(self, node)`

**行号**: 378

### 描述

> 生成当循环

## 函数: `_gen_import(self, node)`

**行号**: 388

### 描述

> 生成导入语句

## 函数: `_gen_export(self, node)`

**行号**: 393

### 描述

> 生成导出语句

## 函数: `_gen_struct_def(self, node)`

**行号**: 398

### 描述

> 生成结构体定义

## 函数: `_gen_struct_init(self, node)`

**行号**: 407

### 描述

> 生成结构体初始化
