# 模块系统 模块 API 文档

---

## 类: `Module`

**行号**: 25

### 描述

> 言语言模块

### 方法

#### `__post_init__()`

**行号**: 41

> 初始化后计算源码哈希

#### `_compute_hash()`

**行号**: 45

> 计算源码哈希值，用于检测变化

#### `export(name, value)`

**行号**: 49

> 导出一个名称

#### `has_export(name)`

**行号**: 53

> 检查是否导出了某个名称

#### `add_hot_reload_callback(callback)`

**行号**: 57

> 添加热更新回调函数

#### `trigger_hot_reload()`

**行号**: 61

> 触发热更新回调

#### `check_for_changes()`

**行号**: 69

> 检查模块源文件是否发生变化

## 类: `ImportStatement`

**行号**: 80

### 描述

> 导入语句

## 类: `ModuleError`

**行号**: 91

### 描述

> 模块系统错误

### 方法

#### `__init__(message, module_name)`

**行号**: 93


## 类: `CircularDependencyError`

**行号**: 98

### 描述

> 循环依赖错误

### 方法

#### `__init__(cycle)`

**行号**: 100


## 类: `ModuleSystem`

**行号**: 107

### 描述

> 言语言模块系统 - 增强版

### 方法

#### `__init__(search_paths, max_cache_size, detect_cycles, enable_hot_reload)`

**行号**: 110


#### `_init_search_paths()`

**行号**: 134

> 初始化搜索路径

#### `resolve_module(module_path, current_file)`

**行号**: 149

> 解析模块路径
> 支持：
> - 相对路径："./utils", "../common"
> - 标准库："collections", "math"
> - 绝对路径

#### `_check_extension(path)`

**行号**: 180

> 检查文件扩展名

#### `_update_lru(key)`

**行号**: 198

> 更新LRU缓存顺序

#### `load_module(module_path, current_file, version_spec)`

**行号**: 210

> 加载一个模块
> 如果已在缓存中则直接返回
> 
> :param module_path: 模块路径
> :param current_file: 当前文件路径（用于相对路径解析）
> :param version_spec: 版本约束（如 ">= 1.0.0"）

#### `_handle_circular_dependency(abs_path, resolved_path)`

**行号**: 302

> 处理循环依赖 - 使用延迟加载
> 返回一个占位模块，实际内容在后续补全

#### `_extract_version(module_path)`

**行号**: 324

> 从模块所在目录的 package.json 中提取版本信息

#### `_check_version(current_version, version_spec)`

**行号**: 341

> 检查版本是否满足约束
> 
> :param current_version: 当前版本
> :param version_spec: 版本约束（如 ">= 1.0.0", "< 2.0.0", "== 1.2.3"）
> :return: 是否满足约束

#### `_parse_imports(source)`

**行号**: 386

> 解析源码中的导入语句
> 支持：
> - 导入 "module"
> - 导入 "module" 为 alias
> - 导入 "module" 取 name1, name2
> - 导入 "module" 取 name1, name2 为 a, b

#### `_parse_exports(source)`

**行号**: 429

> 解析源码中的导出语句
> 支持：
> - 出 name
> - 出 name1, name2
> - 出 函 ...
> - 出 定 ...

#### `get_module(name)`

**行号**: 467

> 从缓存中获取模块

#### `clear_cache()`

**行号**: 474

> 清空模块缓存

#### `build_dependency_graph()`

**行号**: 479

> 构建依赖图
> 返回: {模块名: [依赖模块名列表]}

#### `find_dependencies(module_name, include_indirect)`

**行号**: 497

> 查找模块的依赖
> :param module_name: 模块名称
> :param include_indirect: 是否包含间接依赖
> :return: 依赖模块名称列表

#### `is_standard_library(module_name)`

**行号**: 534

> 检查模块是否是标准库模块

#### `list_standard_library_modules()`

**行号**: 554

> 列出所有标准库模块

#### `_start_hot_reload_monitor()`

**行号**: 579

> 启动热更新监控线程

#### `_check_for_changes()`

**行号**: 592

> 检查所有模块是否发生变化

#### `reload_module(module_path)`

**行号**: 599

> 重新加载指定模块
> 
> :param module_path: 模块路径（可以是绝对路径字符串或模块名称）

#### `enable_hot_reload_for_module(module_name)`

**行号**: 653

> 为指定模块启用热更新
> 
> :param module_name: 模块名称

#### `disable_hot_reload_for_module(module_name)`

**行号**: 665

> 为指定模块禁用热更新
> 
> :param module_name: 模块名称

#### `shutdown_hot_reload()`

**行号**: 677

> 停止热更新监控

#### `resolve_dependencies(module_name, version_spec)`

**行号**: 687

> 解析模块的所有依赖及其版本
> 
> :param module_name: 模块名称
> :param version_spec: 版本约束
> :return: {依赖模块名: 版本号}

#### `validate_dependencies()`

**行号**: 713

> 验证所有已加载模块的依赖是否满足版本约束
> 
> :return: 不满足约束的依赖列表

## 类: `ModuleParser`

**行号**: 739

### 描述

> 模块语句解析器（扩展）

### 方法

#### `is_import_stmt(pos)`

**行号**: 743

> 检查是否是导入语句

#### `is_export_stmt(pos)`

**行号**: 754

> 检查是否是导出语句

## 类: `ImportNode`

**行号**: 770

### 描述

> 导入语句节点

### 方法

#### `__str__()`

**行号**: 776


## 类: `ExportNode`

**行号**: 786

### 描述

> 导出语句节点

### 方法

#### `__str__()`

**行号**: 791


## 函数: `__post_init__(self)`

**行号**: 41

### 描述

> 初始化后计算源码哈希

## 函数: `_compute_hash(self)`

**行号**: 45

### 描述

> 计算源码哈希值，用于检测变化

## 函数: `export(self, name, value)`

**行号**: 49

### 描述

> 导出一个名称

## 函数: `has_export(self, name)`

**行号**: 53

### 描述

> 检查是否导出了某个名称

## 函数: `add_hot_reload_callback(self, callback)`

**行号**: 57

### 描述

> 添加热更新回调函数

## 函数: `trigger_hot_reload(self)`

**行号**: 61

### 描述

> 触发热更新回调

## 函数: `check_for_changes(self)`

**行号**: 69

### 描述

> 检查模块源文件是否发生变化

## 函数: `_init_search_paths(self)`

**行号**: 134

### 描述

> 初始化搜索路径

## 函数: `resolve_module(self, module_path, current_file)`

**行号**: 149

### 描述

> 解析模块路径
> 支持：
> - 相对路径："./utils", "../common"
> - 标准库："collections", "math"
> - 绝对路径

## 函数: `_check_extension(self, path)`

**行号**: 180

### 描述

> 检查文件扩展名

## 函数: `_update_lru(self, key)`

**行号**: 198

### 描述

> 更新LRU缓存顺序

## 函数: `load_module(self, module_path, current_file, version_spec)`

**行号**: 210

### 描述

> 加载一个模块
> 如果已在缓存中则直接返回
> 
> :param module_path: 模块路径
> :param current_file: 当前文件路径（用于相对路径解析）
> :param version_spec: 版本约束（如 ">= 1.0.0"）

## 函数: `_handle_circular_dependency(self, abs_path, resolved_path)`

**行号**: 302

### 描述

> 处理循环依赖 - 使用延迟加载
> 返回一个占位模块，实际内容在后续补全

## 函数: `_extract_version(self, module_path)`

**行号**: 324

### 描述

> 从模块所在目录的 package.json 中提取版本信息

## 函数: `_check_version(self, current_version, version_spec)`

**行号**: 341

### 描述

> 检查版本是否满足约束
> 
> :param current_version: 当前版本
> :param version_spec: 版本约束（如 ">= 1.0.0", "< 2.0.0", "== 1.2.3"）
> :return: 是否满足约束

## 函数: `_parse_imports(self, source)`

**行号**: 386

### 描述

> 解析源码中的导入语句
> 支持：
> - 导入 "module"
> - 导入 "module" 为 alias
> - 导入 "module" 取 name1, name2
> - 导入 "module" 取 name1, name2 为 a, b

## 函数: `_parse_exports(self, source)`

**行号**: 429

### 描述

> 解析源码中的导出语句
> 支持：
> - 出 name
> - 出 name1, name2
> - 出 函 ...
> - 出 定 ...

## 函数: `get_module(self, name)`

**行号**: 467

### 描述

> 从缓存中获取模块

## 函数: `clear_cache(self)`

**行号**: 474

### 描述

> 清空模块缓存

## 函数: `build_dependency_graph(self)`

**行号**: 479

### 描述

> 构建依赖图
> 返回: {模块名: [依赖模块名列表]}

## 函数: `find_dependencies(self, module_name, include_indirect)`

**行号**: 497

### 描述

> 查找模块的依赖
> :param module_name: 模块名称
> :param include_indirect: 是否包含间接依赖
> :return: 依赖模块名称列表

## 函数: `is_standard_library(self, module_name)`

**行号**: 534

### 描述

> 检查模块是否是标准库模块

## 函数: `list_standard_library_modules(self)`

**行号**: 554

### 描述

> 列出所有标准库模块

## 函数: `_start_hot_reload_monitor(self)`

**行号**: 579

### 描述

> 启动热更新监控线程

## 函数: `_check_for_changes(self)`

**行号**: 592

### 描述

> 检查所有模块是否发生变化

## 函数: `reload_module(self, module_path)`

**行号**: 599

### 描述

> 重新加载指定模块
> 
> :param module_path: 模块路径（可以是绝对路径字符串或模块名称）

## 函数: `enable_hot_reload_for_module(self, module_name)`

**行号**: 653

### 描述

> 为指定模块启用热更新
> 
> :param module_name: 模块名称

## 函数: `disable_hot_reload_for_module(self, module_name)`

**行号**: 665

### 描述

> 为指定模块禁用热更新
> 
> :param module_name: 模块名称

## 函数: `shutdown_hot_reload(self)`

**行号**: 677

### 描述

> 停止热更新监控

## 函数: `resolve_dependencies(self, module_name, version_spec)`

**行号**: 687

### 描述

> 解析模块的所有依赖及其版本
> 
> :param module_name: 模块名称
> :param version_spec: 版本约束
> :return: {依赖模块名: 版本号}

## 函数: `validate_dependencies(self)`

**行号**: 713

### 描述

> 验证所有已加载模块的依赖是否满足版本约束
> 
> :return: 不满足约束的依赖列表

## 函数: `is_import_stmt(tokens, pos)`

**行号**: 743

### 描述

> 检查是否是导入语句

## 函数: `is_export_stmt(tokens, pos)`

**行号**: 754

### 描述

> 检查是否是导出语句
