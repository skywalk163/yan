# 言语言 WebAssembly 编译指南

## 概述

言语言支持直接编译为 WebAssembly 字节码，可以在浏览器、Node.js、wasmtime 等任何支持 WebAssembly 的环境中运行。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 编译示例

```python
from codegen_wasm import compile_yan_to_wasm

# 编译言语言代码
code = '定义x=10。定义y=20。印加x y。'
wasm = compile_yan_to_wasm(code, 'output.wasm')

print(f"WASM 文件大小: {len(wasm)} 字节")
```

## 支持的特性

| 特性 | 说明 |
|------|------|
| 整数运算 | 加、减、乘、除、取模 |
| 浮点数运算 | 浮点加、浮点减、浮点乘、浮点除 |
| 比较运算 | 小于、大于、等于、不等于 |
| 条件语句 | 如果...则...否则... |
| 循环语句 | 当满足...则...、遍历循环 |
| 函数定义 | 函数参数 体 |
| 打印输出 | 印字符串、整数、浮点数 |
| 字符串 | 字符串字面量 |

## 示例：汉诺塔

```yan
-- 汉诺塔问题
定义移动=函数n 源 目标 辅助
  如果等于n 1则
    印"移动圆盘从"源"到"目标"。"。
  否则
    移动减n 1源辅助目标。
    移动1源目标辅助。
    移动减n 1辅助目标源。
  。
。

移动3"A""C""B"。
```

### 编译命令

```bash
python compile_example.py
```

## 运行 WASM

### 在 Node.js 中运行

```javascript
const fs = require('fs');
const { instantiate } = require('wasi');

const wasmBytes = fs.readFileSync('output.wasm');

const wasi = new WASI();
const importObject = {
    env: {
        print: (ptr) => { /* 打印字符串 */ },
        print_num: (num) => { console.log(num); },
        print_float: (num) => { console.log(num); }
    },
    wasi_snapshot_preview1: wasi.wasiImport
};

WebAssembly.instantiate(wasmBytes, importObject)
    .then(({ instance }) => {
        instance.exports.main();
    });
```

## 性能特点

- **轻量级**: 生成的 WASM 文件体积小
- **高性能**: 直接编译为机器码执行
- **跨平台**: 可在任何支持 WASM 的环境运行

## 限制

当前版本的 WASM 代码生成器有以下限制：

1. 不支持动态内存分配
2. 不支持复杂数据结构
3. 不支持文件系统访问（除 WASI）

## 未来计划

- [ ] 添加 WASI 完整支持
- [ ] 支持动态数组和字符串操作
- [ ] 添加垃圾回收支持
- [ ] 优化生成代码的大小和性能