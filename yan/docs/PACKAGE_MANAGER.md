# 言语言包管理器使用指南

## 概述

`yan 包` 是言语言的官方包管理器，用于管理 Yan 项目的依赖包、初始化项目、发布包等操作。

## 安装

包管理器已随言语言一起安装，无需额外安装。

## 基本命令

### 1. 安装包

```bash
# 安装最新版本
yan 包 安装 <包名>

# 安装指定版本
yan 包 安装 <包名> <版本>
```

**示例:**
```bash
yan 包 安装 hello-world
yan 包 安装 math-utils 1.0.0
```

### 2. 卸载包

```bash
yan 包 卸载 <包名>
```

**示例:**
```bash
yan 包 卸载 hello-world
```

### 3. 列出已安装的包

```bash
yan 包 列表
```

**示例输出:**
```
已安装的包:
  - hello-world (版本: 1.0.0)
  - math-utils (版本: 0.1.0)
```

### 4. 搜索包

```bash
yan 包 搜索 <关键词>
```

**示例:**
```bash
yan 包 搜索 math
```

### 5. 初始化项目

```bash
# 在当前目录初始化
yan 包 初始化

# 指定项目名称
yan 包 初始化 <项目名>
```

**示例:**
```bash
yan 包 初始化 my-project
```

这将创建以下文件结构:
```
my-project/
├── package.json    # 项目配置文件
├── 主.yan          # 入口文件
└── tests/          # 测试目录
    └── 基本测试.yan
```

### 6. 显示帮助

```bash
yan 包 帮助
```

## 项目配置 (package.json)

每个 Yan 项目都应该有一个 `package.json` 文件，用于描述项目信息和依赖。

**示例:**
```json
{
  "name": "my-project",
  "version": "0.1.0",
  "description": "我的第一个 Yan 项目",
  "author": "张三",
  "dependencies": {
    "math-utils": "1.0.0"
  },
  "entry": "主.yan"
}
```

**字段说明:**
- `name`: 项目名称（必填）
- `version`: 版本号（必填）
- `description`: 项目描述
- `author`: 作者信息
- `dependencies`: 依赖包列表
- `entry`: 入口文件（默认: 主.yan）

## 模块系统

### 导入模块

```yan
# 导入整个模块
引 数学。

# 导入并重命名
引 网络 为 网。

# 导入特定函数
引 工具 之 平方 立方。
```

### 导出定义

```yan
# 导出多个定义
定 平方 = 函 x 乘 x x。
定 立方 = 函 x 乘 x x x。

出 平方 立方。

# 默认导出
出 默认 主函数。
```

## 包结构

### 单文件包

```
math-utils.yan
```

### 多文件包

```
math-utils/
├── package.json    # 包配置
├── 主.yan          # 入口文件
├── src/            # 源码目录
│   ├── 算术.yan
│   └── 几何.yan
└── tests/          # 测试目录
    └── 测试.yan
```

## 包存储位置

包安装在用户主目录的 `.yan/packages` 目录下：

```
~/.yan/
├── packages/       # 已安装的包
└── config.json     # 配置文件
```

## 环境变量

### YANPATH

用于指定额外的包搜索路径：

```bash
export YANPATH=/path/to/my/packages:/another/path
```

## 高级功能

### 开发模式

在开发模式下，包管理器会从本地目录加载包，方便调试：

```bash
# 链接本地包
yan 包 链接 /path/to/local/package
```

### 发布包

```bash
# 发布到仓库
yan 包 发布
```

**注意:** 发布功能需要配置仓库认证信息。

## 命令速查表

| 命令 | 说明 | 示例 |
|------|------|------|
| `yan 包 安装` | 安装包 | `yan 包 安装 math-utils` |
| `yan 包 卸载` | 卸载包 | `yan 包 卸载 math-utils` |
| `yan 包 列表` | 列出包 | `yan 包 列表` |
| `yan 包 搜索` | 搜索包 | `yan 包 搜索 web` |
| `yan 包 初始化` | 初始化项目 | `yan 包 初始化 my-app` |
| `yan 包 帮助` | 显示帮助 | `yan 包 帮助` |

## 常见问题

### Q: 包安装失败怎么办？

A: 请检查以下事项：
1. 网络连接是否正常
2. 包名是否正确
3. 版本号是否存在

### Q: 如何更新包？

A: 使用 `安装` 命令重新安装即可：
```bash
yan 包 安装 <包名>
```

### Q: 如何查看包的详细信息？

A: 使用 `列表` 命令可以查看已安装包的版本信息。

### Q: 可以安装本地包吗？

A: 可以，使用 `链接` 命令：
```bash
yan 包 链接 /path/to/local/package
```

## 版本历史

- **v0.1**: 初始版本，支持基本的安装、卸载、搜索功能
- **v0.2**: 添加项目初始化和包发布功能
- **v0.3**: 添加开发模式和链接功能

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
