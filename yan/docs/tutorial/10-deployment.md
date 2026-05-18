# 第10章：部署与发布

在本章中，我们将学习如何部署和发布言语言项目。

## 10.1 项目结构

一个标准的言语言项目应该遵循以下结构：

```
my-project/
├── package.json        # 项目配置文件
├── 主.yan              # 入口文件
├── lib/                # 自定义库
│   └── utils.yan
├── tests/              # 测试文件
│   └── test_main.yan
├── docs/               # 文档
│   └── README.md
└── examples/           # 示例代码
    └── demo.yan
```

### 10.1.1 package.json 格式

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "description": "项目描述",
  "author": "作者",
  "dependencies": {},
  "entry": "主.yan"
}
```

## 10.2 运行项目

### 10.2.1 开发模式

```bash
# 运行单个文件
python main.py 主.yan

# 启用调试模式
python main.py 主.yan --debug

# 运行测试
python main.py 包 测试
```

### 10.2.2 编译模式

```bash
# 编译为Python代码
python main.py --compile 主.yan --output main.py

# 运行编译后的代码
python main.py
```

## 10.3 打包发布

### 10.3.1 使用包管理器

```bash
# 初始化项目
yan 包 初始化 my-project

# 安装依赖
yan 包 安装 math-utils

# 发布包
yan 包 发布
```

### 10.3.2 手动打包

```bash
# 创建发布包
zip -r my-project.zip my-project/

# 解压使用
unzip my-project.zip
cd my-project
python main.py 主.yan
```

## 10.4 部署到服务器

### 10.4.1 环境要求

- Python 3.8+
- 必要的依赖包

### 10.4.2 部署步骤

```bash
# 登录服务器
ssh user@server

# 创建项目目录
mkdir -p /opt/my-project
cd /opt/my-project

# 上传项目文件
scp -r local-project/* user@server:/opt/my-project/

# 安装依赖
pip install -r requirements.txt

# 运行服务
nohup python main.py 主.yan > output.log 2>&1 &
```

## 10.5 创建可执行程序

### 10.5.1 使用 PyInstaller

```bash
# 安装 PyInstaller
pip install pyinstaller

# 创建可执行文件
pyinstaller --onefile --name myapp main.py

# 运行生成的程序
./dist/myapp 主.yan
```

### 10.5.2 创建 Windows 安装包

```bash
# 使用 Inno Setup 创建安装程序
# 创建 installer.iss 文件
# 运行 Inno Setup 编译
```

## 10.6 CI/CD 配置

### 10.6.1 GitHub Actions

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest
    
    - name: Run tests
      run: |
        cd yan
        python -m pytest tests/
```

### 10.6.2 GitLab CI

```yaml
stages:
  - test

test:
  stage: test
  image: python:3.x
  script:
    - cd yan
    - pip install pytest
    - python -m pytest tests/
```

## 10.7 版本管理

### 10.7.1 版本号规范

```
v0.1.0  - 初始版本
v0.1.1  - Bug修复
v0.2.0  - 新增功能
v1.0.0  - 稳定版本
v1.0.1  - 稳定版本的Bug修复
v2.0.0  - 重大更新，不兼容旧版本
```

### 10.7.2 更新版本号

```bash
# 更新 package.json 中的版本号
sed -i 's/"version": "0.1.0"/"version": "0.1.1"/' package.json
```

## 10.8 发布说明模板

```markdown
# v0.1.0 发布说明

## 新增功能

- 新增 JSON 模块支持
- 新增网络请求功能
- 新增数据库操作模块

## Bug 修复

- 修复词法分析器错误
- 修复解析器异常处理

## 改进

- 优化代码生成性能
- 改进错误提示信息

## 文档

- 添加入门教程
- 添加 API 参考文档

## 安装

```bash
yan 包 安装 my-package
```

## 使用

```yan
引 我的模块。
印 我的模块.功能()。
```
```

## 练习

1. 创建一个完整的项目结构
2. 编写 CI/CD 配置文件
3. 创建一个可执行程序
4. 编写发布说明

恭喜！你已经完成了言语言的全部学习内容！
