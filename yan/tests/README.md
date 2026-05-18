# 言语言测试框架文档

言语言提供完整的测试框架支持，包括单元测试、集成测试和测试运行工具。

## 📦 测试框架组件

### 1. yan_test.py - 测试框架核心

测试框架核心模块，提供测试套件、测试用例和测试运行功能。

**功能特性：**
- ✅ 测试套件管理
- ✅ 测试用例装饰器
- ✅ setup/teardown 支持
- ✅ 测试跳过机制
- ✅ 详细/安静输出模式
- ✅ 快速失败模式
- ✅ 测试报告生成

### 2. yan_assertions.py - 断言函数库

提供 40+ 断言函数，覆盖各种测试场景。

**断言类别：**
- 基础断言：等、不等、为真、为假、为空、非空
- 比较断言：大于、小于、大于等于、小于等于
- 容器断言：包含、不包含、长度
- 类型断言：类型检查
- 字符串断言：开始、结束、匹配
- 异常断言：抛出、不抛出
- 浮点数断言：几乎等
- 列表断言：无重复、有序、子集、超集
- 字典断言：键存在、字典等

### 3. run_tests.py - 测试运行器

命令行测试运行工具，支持内存监控。

**功能特性：**
- ✅ 自动发现测试文件
- ✅ 内存占用监控（默认 20GB 限制）
- ✅ 测试进度显示
- ✅ 详细测试报告
- ✅ 失败快速定位

## 🔧 使用方法

### 基本测试示例

```python
from yan_test import *
from yan_assertions import *

@suite("数学运算测试")
class MathTests:

    def setup(self):
        """测试前准备"""
        pass

    def teardown(self):
        """测试后清理"""
        pass

    @test("加法测试")
    def test_add(self):
        """测试加法运算"""
        等(1 + 2, 3)
        等(0 + 0, 0)

    @test("除法测试")
    def test_divide(self):
        """测试除法运算"""
        等(10 / 2, 5)
        等(9 / 3, 3)
```

### 运行测试

```bash
# 运行所有测试
python tests/run_tests.py

# 指定内存限制
python tests/run_tests.py -m 10G

# 详细输出
python tests/run_tests.py -v

# 快速失败模式
python tests/run_tests.py -f
```

### 单元测试示例

#### Math 模块测试

```python
from stdlib.math import *

@suite("Math 模块测试")
class MathTests:

    @test("绝对值测试")
    def test_abs(self):
        等(绝对(-5), 5)
        等(绝对(3.14), 3.14)

    @test("阶乘测试")
    def test_factorial(self):
        等(阶乘(5), 120)
        等(阶乘(0), 1)
```

#### String 模块测试

```python
from stdlib.string import *

@suite("String 模块测试")
class StringTests:

    @test("大写测试")
    def test_upper(self):
        等(大写("hello"), "HELLO")

    @test("字符串长度测试")
    def test_length(self):
        等(长度("hello"), 5)
```

#### Collections 模块测试

```python
from stdlib.collections import *

@suite("Collections 模块测试")
class CollectionsTests:

    @test("列表去重测试")
    def test_distinct(self):
        等(去重(列(1, 2, 2, 3)), [1, 2, 3])

    @test("列表反转测试")
    def test_reverse(self):
        等(反转(列(1, 2, 3)), [3, 2, 1])
```

## 📊 测试覆盖

### Math 模块
- ✅ 常量测试（π, e）
- ✅ 基础数学运算（绝对值、上下取整、四舍五入）
- ✅ 幂运算和开方
- ✅ 阶乘和素数判断
- ✅ 斐波那契数列
- ✅ 最大公约数和最小公倍数
- ✅ 统计函数（求和、平均值、最大值、最小值）

### String 模块
- ✅ 基础操作（长度、拼接、重复）
- ✅ 大小写转换（大写、小写、首字母大写）
- ✅ 查找替换（查找、替换、包含）
- ✅ 分割连接（分割、连接）
- ✅ 格式处理（去空白、对齐、补零）
- ✅ 类型判断（是数字、是字母、是空白）
- ✅ 高级功能（反转、统计）

### Collections 模块
- ✅ 列表操作（去重、反转、切片、排序）
- ✅ 范围生成
- ✅ 查找过滤（查找、查找所有、存在、所有）
- ✅ 展平分组
- ✅ 集合操作（交集、并集、差集）
- ✅ 字典操作（取键、取值、过滤、映射）

### Time 模块
- ✅ 时间戳获取
- ✅ 日期时间提取（年、月、日、星期几）
- ✅ 闰年判断
- ✅ 月份天数
- ✅ 睡眠函数
- ✅ 格式转换（角度↔弧度）
- ✅ 名称转换（中文月份、星期）

## 🛠️ 命令行工具

### 基本用法

```bash
# 运行所有测试
python run_tests.py

# 指定内存限制（默认 20GB）
python run_tests.py -m 10G
python run_tests.py -m 1T

# 详细输出
python run_tests.py -v

# 安静模式
python run_tests.py -q

# 快速失败（遇到第一个失败就停止）
python run_tests.py -f
```

### 测试文件结构

```
tests/
├── run_tests.py          # 测试运行器
├── test_math.py          # Math 模块测试
├── test_string.py        # String 模块测试
├── test_collections.py   # Collections 模块测试
├── test_time.py          # Time 模块测试
└── README.md             # 本文档
```

## 📈 内存管理

测试运行器内置内存监控功能：

- ✅ 实时监控进程内存占用
- ✅ 包含所有子进程的内存占用
- ✅ 可配置的内存限制（默认 20GB）
- ✅ 超限时自动触发垃圾回收
- ✅ 警告提示

### 内存限制配置

```bash
# 20GB（默认）
python run_tests.py -m 20G

# 10GB
python run_tests.py -m 10G

# 1TB
python run_tests.py -m 1T
```

## 🎯 最佳实践

### 1. 测试组织

```python
@suite("功能模块测试")
class FeatureTests:

    def setup(self):
        """共享的测试前准备"""
        self.data = load_test_data()

    def teardown(self):
        """共享的测试后清理"""
        cleanup(self.data)

    @test("具体测试1")
    def test_case_1(self):
        ...

    @test("具体测试2")
    def test_case_2(self):
        ...
```

### 2. 断言使用

```python
# 使用中文断言函数
等(actual, expected)        # 断言相等
包含(container, element)    # 断言包含
为真(condition)            # 断言为真
抛出(func, Exception)      # 断言抛出异常
```

### 3. 跳过测试

```python
@skip("暂未实现")
@test("未完成的测试")
def test_unfinished(self):
    ...

@test("条件测试")
def test_conditional(self):
    skipIf(some_condition, "条件不满足")
    ...
```

## 📝 测试报告

运行测试后，会生成详细的测试报告：

```
==================================================
言语言标准库测试报告
==================================================

运行测试: tests/test_math.py
--------------------------------------------------------------------------------
✓ 圆周率常量测试
✓ 自然常数测试
✓ 绝对值测试
✓ 向下取整测试
✓ 向上取整测试
...

==================================================
测试摘要
==================================================
  总计测试: 150
  通过: 145
  失败: 3
  错误: 2
  跳过: 0
  总时间: 12.34秒

  最大内存占用: 1.23GB
  内存限制: 20.00GB
==================================================
```

## 🤝 贡献测试

欢迎为言语言贡献更多测试！

1. 在 `tests/` 目录下创建测试文件
2. 遵循现有的测试约定
3. 使用中文断言函数
4. 包含详细的测试说明
5. 运行测试确保通过

## 📚 更多资源

- [语言规范](../docs/LANGUAGE_SPEC.md)
- [标准库文档](../stdlib/README.md)
- [自举成功报告](../selfhost/BOOTSTRAP_SUCCESS_REPORT.md)
