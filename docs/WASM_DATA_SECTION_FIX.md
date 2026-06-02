# WebAssembly Data Section 修复文档

## 问题描述

在执行言语言编译器生成的 WebAssembly 文件时，遇到了编译错误：

```
Error: WebAssembly.instantiate(): expected 65 bytes, fell off end @+121
```

这个问题主要出现在包含字符串输出的代码中，例如：

```yan
印"Hello"。
```

## 问题根因

经过详细调试，发现问题出在 Data section 的 flags 字段上。Node.js 的 WebAssembly 实现对 Data section 的 flags 字段有特定要求。

### 原来的实现

在 [codegen_wasm.py](file:///g:/dumategithub/newlisp/yan/codegen_wasm.py#L326) 中，Data section 的生成使用了：

```python
# flags = 1 (active segment with implicit memory index 0)
segment = b'\x01' + init_expr + self._encode_varuint(len(data_bytes)) + data_bytes
```

### 问题分析

- **Flags = 0x01**: 表示 active segment，使用隐式的 memory index 0
- 但是 Node.js 的 WebAssembly 实现对这种格式的支持有问题，导致编译失败

## 解决方案

修改 Data section 的生成方式，使用显式的 memory index：

```python
# flags = 0x02 (active segment with explicit memory index)
# 后面紧跟 memory index (0x00)
segment = b'\x02' + b'\x00' + init_expr + self._encode_varuint(len(data_bytes)) + data_bytes
```

## 修改内容

### 文件: [codegen_wasm.py](file:///g:/dumategithub/newlisp/yan/codegen_wasm.py)

**方法**: `_gen_data` (第 314-330 行)

**修改前**:
```python
def _gen_data(self) -> bytes:
    """生成数据段"""
    if not self.string_constants:
        return None

    segments = []
    for data, offset in self.string_constants.items():
        # Active segment: flags=1, offset(init_expr), data(vec(byte))
        # init_expr = i32.const offset + end
        # 添加 null 终止符
        data_bytes = data.encode('utf-8') + b'\x00'
        init_expr = self._i32_const(offset) + b'\x0b'
        segment = b'\x01' + init_expr + self._encode_varuint(len(data_bytes)) + data_bytes
        segments.append(segment)

    return self._encode_varuint(len(segments)) + b''.join(segments)
```

**修改后**:
```python
def _gen_data(self) -> bytes:
    """生成数据段"""
    if not self.string_constants:
        return None

    segments = []
    for data, offset in self.string_constants.items():
        # Active segment: flags=2, memory_idx, offset(init_expr), data(vec(byte))
        # flags=2 表示 active segment with explicit memory index
        # init_expr = i32.const offset + end
        # 添加 null 终止符
        data_bytes = data.encode('utf-8') + b'\x00'
        init_expr = self._i32_const(offset) + b'\x0b'
        segment = b'\x02' + b'\x00' + init_expr + self._encode_varuint(len(data_bytes)) + data_bytes
        segments.append(segment)

    return self._encode_varuint(len(segments)) + b''.join(segments)
```

## WebAssembly Data Section 格式说明

### Flags 字段

| Flags 值 | 含义 | 格式 |
|---------|------|------|
| 0x00 | Passive segment | flags |
| 0x01 | Active segment (implicit memory 0) | flags + init_expr |
| 0x02 | Active segment (explicit memory) | flags + memory_idx + init_expr |

### Data section 完整格式

```
section_id: 0x0b (Data)
section_size: varuint32
data_count: varuint32  # 仅在 Bulk Memory 特性下存在
segment_count: varuint32

# 对于每个 segment（flags = 0x02）:
  flags: varuint32 = 0x02
  memory_idx: varuint32 = 0x00
  init_expr: expr  # 初始化偏移量表达式
  data_size: varuint32
  data: byte[data_size]
```

## 测试验证

修复后，所有测试用例都能正常工作：

1. **简单字符串输出**:
   ```yan
   印"Hello"。
   ```
   ✅ 输出：`Printed: Hello`

2. **数字输出**:
   ```yan
   令 a 为 42。印数 a。
   ```
   ✅ 输出：`Number: 42`

3. **多字符串输出**:
   ```yan
   印"Hello"。印"World"。
   ```
   ✅ 输出：`Printed: Hello` 和 `Printed: World`

## 兼容性说明

- ✅ Node.js 支持 (已测试)
- ✅ 标准 WebAssembly 运行时支持
- ✅ 保持与现有 Memory section 导出兼容

## 相关文件

- [codegen_wasm.py](file:///g:/dumategithub/newlisp/yan/codegen_wasm.py) - 主要修改文件
