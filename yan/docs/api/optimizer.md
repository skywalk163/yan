# 优化器 模块 API 文档

---

## 类: `OptimizerConfig`

**行号**: 19

### 描述

> 优化器配置

### 方法

#### `__init__(constant_folding, dead_code_elimination, expression_simplification, tail_recursion_optimization, optimization_level, verbose, enable_diagnostics)`

**行号**: 21


## 类: `ASTOptimizer`

**行号**: 44

### 描述

> AST 优化器

### 方法

#### `__init__(config)`

**行号**: 47


#### `_create_optimizations()`

**行号**: 61

> 根据配置创建优化策略列表

#### `optimize(node)`

**行号**: 82

> 执行所有启用的优化

#### `_print_optimization_summary(original, optimized)`

**行号**: 110

> 打印优化摘要

#### `get_total_time()`

**行号**: 117

> 获取优化总耗时

#### `get_optimization_stats()`

**行号**: 123

> 获取优化统计信息

#### `get_diagnostics()`

**行号**: 150

> 获取详细诊断信息

#### `add_optimization(optimization)`

**行号**: 154

> 添加自定义优化策略

#### `remove_optimization(optimization_type)`

**行号**: 158

> 移除指定类型的优化策略

#### `clear_optimizations()`

**行号**: 165

> 清除所有优化策略

#### `reset_stats()`

**行号**: 169

> 重置统计信息

## 函数: `_create_optimizations(self)`

**行号**: 61

### 描述

> 根据配置创建优化策略列表

## 函数: `optimize(self, node)`

**行号**: 82

### 描述

> 执行所有启用的优化

## 函数: `_print_optimization_summary(self, original, optimized)`

**行号**: 110

### 描述

> 打印优化摘要

## 函数: `get_total_time(self)`

**行号**: 117

### 描述

> 获取优化总耗时

## 函数: `get_optimization_stats(self)`

**行号**: 123

### 描述

> 获取优化统计信息

## 函数: `get_diagnostics(self)`

**行号**: 150

### 描述

> 获取详细诊断信息

## 函数: `add_optimization(self, optimization)`

**行号**: 154

### 描述

> 添加自定义优化策略

## 函数: `remove_optimization(self, optimization_type)`

**行号**: 158

### 描述

> 移除指定类型的优化策略

## 函数: `clear_optimizations(self)`

**行号**: 165

### 描述

> 清除所有优化策略

## 函数: `reset_stats(self)`

**行号**: 169

### 描述

> 重置统计信息
