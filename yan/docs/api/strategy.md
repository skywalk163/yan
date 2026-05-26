# 优化策略 模块 API 文档

---

## 类: `OptimizationStrategy`

**行号**: 13

### 描述

> 优化策略接口

### 方法

#### `optimize(node)`

**行号**: 17

> 执行优化，返回优化后的节点

#### `name()`

**行号**: 22

> 优化策略名称

#### `requires()`

**行号**: 27

> 此优化依赖的其他优化策略

#### `get_stats()`

**行号**: 31

> 获取此优化策略的统计信息

## 类: `OptimizationLevel`

**行号**: 36

### 描述

> 优化级别枚举

### 方法

#### `get_description(level)`

**行号**: 45

> 获取优化级别的描述

#### `get_enabled_optimizations(level)`

**行号**: 57

> 根据优化级别获取启用的优化策略

## 函数: `optimize(self, node)`

**行号**: 17

### 描述

> 执行优化，返回优化后的节点

## 函数: `name(self)`

**行号**: 22

### 描述

> 优化策略名称

## 函数: `requires(self)`

**行号**: 27

### 描述

> 此优化依赖的其他优化策略

## 函数: `get_stats(self)`

**行号**: 31

### 描述

> 获取此优化策略的统计信息

## 函数: `get_description(cls, level)`

**行号**: 45

### 描述

> 获取优化级别的描述

## 函数: `get_enabled_optimizations(cls, level)`

**行号**: 57

### 描述

> 根据优化级别获取启用的优化策略
