# 言语言类型系统设计文档

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为言语言添加可选的静态类型系统，提升代码质量和开发体验

**架构：** 渐进式类型系统，支持类型推断和类型检查

**技术栈：** Python 3.8+、类型推断引擎、类型检查器

---

## 设计理念

### 1. 渐进式类型

**原则：** 类型是可选的，不强制要求

**特点：**
- 可以混合使用动态和静态类型
- 类型注解不影响运行时行为
- 逐步添加类型，无需一次性完成

**示例：**
```yan
注 动态类型（现有方式）
定 加法 = 函 a b 加 a b。

注 静态类型（新增方式）
定 加法 = 函(a: 数, b: 数): 数 加 a b。
```

### 2. 类型推断

**原则：** 尽可能自动推断类型，减少注解负担

**特点：**
- 局部类型推断
- 函数返回类型推断
- 字面量类型推断

**示例：**
```yan
注 类型推断
定 数字 = 42。          注 推断为 数
定 文本 = "hello"。     注 推断为 串
定 列表 = 列 1 2 3。    注 推断为 列<数>

注 函数返回类型推断
定 平方 = 函(x: 数) 乘 x x。  注 返回类型推断为 数
```

### 3. 中文友好

**原则：** 类型名称使用中文，符合语言风格

**特点：**
- 中文类型名称
- 中文类型操作符
- 中文错误信息

**示例：**
```yan
定 数字: 数 = 42。
定 文本: 串 = "hello"。
定 列表: 列<数> = 列 1 2 3。
定 映射: 典<串, 数> = 典 "a" 1 "b" 2。
```

---

## 类型系统设计

### 1. 基础类型

#### 1.1 原始类型

| 类型 | 中文名 | 说明 | 示例 |
|------|--------|------|------|
| `数` | 数 | 整数和浮点数 | `42`, `3.14` |
| `串` | 串 | 字符串 | `"hello"` |
| `布尔` | 布尔 | 布尔值 | `真`, `假` |
| `空` | 空 | 空值 | `空` |

#### 1.2 复合类型

| 类型 | 中文名 | 说明 | 示例 |
|------|--------|------|------|
| `列<T>` | 列表 | 列表类型 | `列<数>` |
| `典<K, V>` | 字典 | 字典类型 | `典<串, 数>` |
| `元<T...>` | 元组 | 元组类型 | `元<数, 串>` |
| `函<A...> -> R` | 函数 | 函数类型 | `函<数, 数> -> 数` |

#### 1.3 特殊类型

| 类型 | 中文名 | 说明 |
|------|--------|------|
| `任意` | 任意 | 任意类型 |
| `无` | 无 | 无返回值 |
| `未定` | 未定 | 类型未确定 |

### 2. 类型语法

#### 2.1 类型注解语法

**变量类型注解：**
```yan
定 名称: 类型 = 值。
```

**示例：**
```yan
定 年龄: 数 = 25。
定 姓名: 串 = "张三"。
定 成绩: 列<数> = 列 85 92 78。
```

**函数参数类型注解：**
```yan
定 函数名 = 函(参数1: 类型1, 参数2: 类型2): 返回类型
  函数体。
```

**示例：**
```yan
定 加法 = 函(a: 数, b: 数): 数
  加 a b。
。

定 问候 = 函(名字: 串): 串
  "你好，"连名字。
。
```

#### 2.2 泛型语法

**泛型类型：**
```yan
定 名称: 容器<元素类型> = 值。
```

**示例：**
```yan
定 数字列表: 列<数> = 列 1 2 3。
定 字符串列表: 列<串> = 列 "a" "b" "c"。
定 字典映射: 典<串, 数> = 典 "one" 1 "two" 2。
```

**泛型函数：**
```yan
定 泛型函数 = 函<T>(参数: T): T
  函数体。
。
```

**示例：**
```yan
定 恒等 = 函<T>(x: T): T
  x。
。

定 第一个 = 函<T>(列表: 列<T>): T
  首 列表。
。
```

### 3. 类型推断

#### 3.1 字面量推断

**规则：**
- 整数字面量 → `数`
- 浮点数字面量 → `数`
- 字符串字面量 → `串`
- 布尔字面量 → `布尔`
- 空值 → `空`

**示例：**
```yan
定 数字 = 42。        注 推断为 数
定 小数 = 3.14。      注 推断为 数
定 文本 = "hello"。   注 推断为 串
定 标志 = 真。        注 推断为 布尔
```

#### 3.2 表达式推断

**算术运算：**
```yan
定 结果 = 加 1 2。      注 推断为 数
定 结果2 = 乘 3.14 2。  注 推断为 数
```

**比较运算：**
```yan
定 结果 = 大 5 3。      注 推断为 布尔
定 结果2 = 等 "a" "b"。 注 推断为 布尔
```

**函数调用：**
```yan
定 平方 = 函(x: 数) 乘 x x。
定 结果 = 平方 5。      注 推断为 数
```

#### 3.3 上下文推断

**列表元素类型：**
```yan
定 列表 = 列 1 2 3。    注 推断为 列<数>
定 首元素 = 首 列表。   注 推断为 数
```

**函数返回类型：**
```yan
定 加法 = 函(a: 数, b: 数)
  加 a b。              注 返回类型推断为 数
。
```

### 4. 类型检查

#### 4.1 静态检查

**检查时机：** 编译时

**检查内容：**
- 类型一致性
- 参数类型匹配
- 返回类型匹配
- 泛型约束

**示例：**
```yan
注 类型错误示例
定 数字: 数 = "hello"。  注 错误：期望 数，实际 串

定 加法 = 函(a: 数, b: 数): 数 加 a b。
加法 1 "hello"。        注 错误：参数类型不匹配
```

#### 4.2 动态检查

**检查时机：** 运行时

**检查内容：**
- 类型转换
- 空值检查
- 边界检查

**示例：**
```yan
定 除法 = 函(a: 数, b: 数): 数
  若 等 b 0
  则 报错 "除零错误"。   注 运行时检查
  否则 除 a b。
。
```

### 5. 类型兼容性

#### 5.1 子类型关系

**原始类型：**
- 无子类型关系

**复合类型：**
- `列<子类型>` 是 `列<父类型>` 的子类型（协变）
- `函<父类型> -> 子类型` 是 `函<子类型> -> 父类型` 的子类型（逆变）

**示例：**
```yan
定 数字列表: 列<数> = 列 1 2 3。
定 任意列表: 列<任意> = 数字列表。  注 兼容
```

#### 5.2 类型转换

**显式转换：**
```yan
定 数字 = 42。
定 文本 = 串 数字。    注 数 → 串

定 文本2 = "123"。
定 数字2 = 数 文本2。  注 串 → 数
```

**隐式转换：**
```yan
注 无隐式转换，保持类型安全
定 数字: 数 = 42。
定 文本: 串 = 数字。   注 错误：类型不匹配
```

---

## 实现计划

### 阶段1：类型注解支持（2周）

**目标：** 支持类型注解语法

**任务：**

#### 任务1.1：类型语法解析

- [ ] 扩展词法分析器支持类型注解
- [ ] 扩展语法分析器支持类型表达式
- [ ] 构建类型AST节点
- [ ] 测试类型语法解析

**文件：** `yan/type_parser.py`

**示例：**
```python
class TypeParser:
    def parse_type(self, tokens):
        """解析类型表达式"""
        # 数, 串, 布尔, 空
        if self.peek() in ['数', '串', '布尔', '空']:
            return PrimitiveType(self.consume())
        
        # 列<T>
        if self.peek() == '列':
            return self.parse_list_type()
        
        # 典<K, V>
        if self.peek() == '典':
            return self.parse_dict_type()
        
        # 函<A...> -> R
        if self.peek() == '函':
            return self.parse_function_type()
```

#### 任务1.2：类型表示

- [ ] 定义类型类层次结构
- [ ] 实现类型相等性判断
- [ ] 实现类型字符串表示
- [ ] 测试类型表示

**文件：** `yan/types.py`

**示例：**
```python
class Type:
    """类型基类"""
    pass

class PrimitiveType(Type):
    """原始类型"""
    def __init__(self, name):
        self.name = name
    
    def __eq__(self, other):
        return isinstance(other, PrimitiveType) and self.name == other.name
    
    def __str__(self):
        return self.name

class ListType(Type):
    """列表类型"""
    def __init__(self, element_type):
        self.element_type = element_type
    
    def __str__(self):
        return f"列<{self.element_type}>"
```

#### 任务1.3：类型存储

- [ ] 实现类型环境
- [ ] 存储变量类型
- [ ] 存储函数类型
- [ ] 测试类型存储

**文件：** `yan/type_env.py`

**示例：**
```python
class TypeEnv:
    """类型环境"""
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
    
    def bind(self, name, type):
        """绑定变量类型"""
        self.bindings[name] = type
    
    def lookup(self, name):
        """查找变量类型"""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
```

### 阶段2：类型推断（1周）

**目标：** 实现自动类型推断

**任务：**

#### 任务2.1：类型推断引擎

- [ ] 实现类型推断算法
- [ ] 处理字面量推断
- [ ] 处理表达式推断
- [ ] 测试类型推断

**文件：** `yan/type_inference.py`

**示例：**
```python
class TypeInference:
    """类型推断引擎"""
    def infer(self, ast, env):
        """推断表达式类型"""
        if ast.type == 'number':
            return PrimitiveType('数')
        
        if ast.type == 'string':
            return PrimitiveType('串')
        
        if ast.type == 'variable':
            return env.lookup(ast.name)
        
        if ast.type == 'call':
            func_type = self.infer(ast.func, env)
            arg_types = [self.infer(arg, env) for arg in ast.args]
            return self.apply_function(func_type, arg_types)
```

#### 任务2.2：约束求解

- [ ] 生成类型约束
- [ ] 求解约束系统
- [ ] 处理泛型变量
- [ ] 测试约束求解

**文件：** `yan/constraint_solver.py`

**示例：**
```python
class ConstraintSolver:
    """约束求解器"""
    def solve(self, constraints):
        """求解类型约束"""
        substitution = {}
        
        for constraint in constraints:
            left, right = constraint
            
            # 统一两个类型
            self.unify(left, right, substitution)
        
        return substitution
    
    def unify(self, t1, t2, subst):
        """统一两个类型"""
        # 如果t1是类型变量
        if isinstance(t1, TypeVar):
            return self.unify_var(t1, t2, subst)
        
        # 如果t2是类型变量
        if isinstance(t2, TypeVar):
            return self.unify_var(t2, t1, subst)
        
        # 如果都是原始类型
        if isinstance(t1, PrimitiveType) and isinstance(t2, PrimitiveType):
            if t1 == t2:
                return subst
            raise TypeError(f"无法统一 {t1} 和 {t2}")
```

### 阶段3：类型检查（1周）

**目标：** 实现静态类型检查

**任务：**

#### 任务3.1：类型检查器

- [ ] 实现类型检查算法
- [ ] 检查类型一致性
- [ ] 检查参数类型
- [ ] 测试类型检查

**文件：** `yan/type_checker.py`

**示例：**
```python
class TypeChecker:
    """类型检查器"""
    def check(self, ast, env):
        """检查类型"""
        if ast.type == 'variable':
            var_type = env.lookup(ast.name)
            if var_type is None:
                raise TypeError(f"未定义的变量: {ast.name}")
            return var_type
        
        if ast.type == 'call':
            func_type = self.check(ast.func, env)
            arg_types = [self.check(arg, env) for arg in ast.args]
            
            # 检查函数类型
            if not isinstance(func_type, FunctionType):
                raise TypeError(f"{ast.func} 不是函数")
            
            # 检查参数类型
            if len(arg_types) != len(func_type.param_types):
                raise TypeError(f"参数数量不匹配")
            
            for i, (expected, actual) in enumerate(zip(func_type.param_types, arg_types)):
                if expected != actual:
                    raise TypeError(f"参数{i}类型不匹配: 期望{expected}, 实际{actual}")
            
            return func_type.return_type
```

#### 任务3.2：错误报告

- [ ] 实现类型错误报告
- [ ] 提供错误位置
- [ ] 提供修复建议
- [ ] 测试错误报告

**文件：** `yan/type_errors.py`

**示例：**
```python
class TypeError:
    """类型错误"""
    def __init__(self, message, location, expected=None, actual=None):
        self.message = message
        self.location = location
        self.expected = expected
        self.actual = actual
    
    def format(self):
        """格式化错误信息"""
        result = f"类型错误: {self.message}\n"
        result += f"位置: 第{self.location.line}行, 第{self.location.column}列\n"
        
        if self.expected and self.actual:
            result += f"期望类型: {self.expected}\n"
            result += f"实际类型: {self.actual}\n"
        
        return result
```

### 阶段4：工具集成（1周）

**目标：** 集成到编译器和IDE

**任务：**

#### 任务4.1：编译器集成

- [ ] 集成类型检查到编译流程
- [ ] 支持类型注解的代码生成
- [ ] 添加类型检查选项
- [ ] 测试编译器集成

**文件：** `yan/compiler_with_types.py`

#### 任务4.2：IDE集成

- [ ] VS Code插件类型提示
- [ ] 类型自动补全
- [ ] 类型错误标记
- [ ] 测试IDE集成

**文件：** `yan/vscode-extension/typeProvider.ts`

---

## 类型系统示例

### 示例1：简单类型注解

```yan
注 变量类型注解
定 年龄: 数 = 25。
定 姓名: 串 = "张三"。
定 成绩: 列<数> = 列 85 92 78。

注 函数类型注解
定 平方 = 函(x: 数): 数
  乘 x x。
。

定 问候 = 函(名字: 串): 串
  "你好，"连名字。
。
```

### 示例2：泛型函数

```yan
注 泛型恒等函数
定 恒等 = 函<T>(x: T): T
  x。
。

定 数字 = 恒等 42。      注 类型推断为 数
定 文本 = 恒等 "hello"。 注 类型推断为 串

注 泛型列表函数
定 第一个 = 函<T>(列表: 列<T>): T
  首 列表。
。

定 首数字 = 第一个 列 1 2 3。  注 类型推断为 数
```

### 示例3：类型推断

```yan
注 类型推断示例
定 数字 = 42。              注 推断为 数
定 文本 = "hello"。         注 推断为 串
定 列表 = 列 1 2 3。        注 推断为 列<数>

注 函数返回类型推断
定 加法 = 函(a: 数, b: 数)
  加 a b。                  注 返回类型推断为 数
。

注 表达式类型推断
定 结果 = 乘 加 1 2 3。     注 推断为 数
```

### 示例4：类型错误检测

```yan
注 类型错误示例
定 数字: 数 = "hello"。     注 错误：期望 数，实际 串

定 加法 = 函(a: 数, b: 数): 数 加 a b。
加法 1 "hello"。            注 错误：参数类型不匹配

定 列表: 列<数> = 列 1 "a" 3。  注 错误：列表元素类型不一致
```

---

## 验收标准

### 功能验收

- [ ] 支持所有基础类型
- [ ] 支持类型注解语法
- [ ] 支持类型推断
- [ ] 支持类型检查
- [ ] 支持泛型

### 性能验收

- [ ] 类型检查时间 < 100ms（小型文件）
- [ ] 类型推断准确率 > 95%
- [ ] 不影响编译速度

### 质量验收

- [ ] 测试覆盖率 > 80%
- [ ] 所有测试通过
- [ ] 文档完整

---

## 成功指标

**短期（1个月）：**
- 类型系统成熟度：0% → 40%
- 类型推断准确率：> 90%
- 用户采用率：> 20%

**中期（3个月）：**
- 类型系统成熟度：40% → 70%
- 类型推断准确率：> 95%
- 用户采用率：> 50%

---

## 风险与缓解

### 风险1：类型推断不准确

**风险：** 类型推断可能推断错误

**缓解：**
- 提供类型注解覆盖
- 允许显式类型
- 收集用户反馈

### 风险2：性能影响

**风险：** 类型检查可能影响编译速度

**缓解：**
- 增量类型检查
- 缓存类型信息
- 可选的类型检查

### 风险3：学习曲线

**风险：** 类型系统可能增加学习难度

**缓解：**
- 类型是可选的
- 提供详细文档
- 提供示例代码

---

## 后续工作

1. **高级类型特性**（2周）
   - 联合类型
   - 交叉类型
   - 类型守卫

2. **类型推导增强**（1周）
   - 全局类型推断
   - 类型泛化
   - 类型特化

3. **类型工具**（1周）
   - 类型可视化
   - 类型文档生成
   - 类型覆盖率报告

---

**最后更新：** 2026-05-18  
**预计完成：** 2026-06-15  
**负责人：** AI代理
