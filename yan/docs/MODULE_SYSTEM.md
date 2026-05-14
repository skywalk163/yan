# 言语言模块系统设计

**版本：** 0.3.0  
**最后更新：** 2026-05-10

---

## 1. 设计目标

- **简洁性：** 语法简洁，符合文言风格
- **模块化：** 支持代码组织和复用
- **命名空间：** 避免命名冲突
- **标准库扩展：** 支持第三方库

---

## 2. 语法设计

### 2.1 导入模块

**语法：** `引 模块名`

**示例：**
```
引 数学
引 网络
引 文件

正弦1.0。        → 使用数学库的正弦函数
读文件"test.txt"。 → 使用文件库的读文件函数
```

### 2.2 导入并重命名

**语法：** `引 模块名 为 别名`

**示例：**
```
引 数学 为 算
算正弦1.0。
```

### 2.3 导入特定函数

**语法：** `引 模块名 之 函数名`

**示例：**
```
引 数学 之 正弦
正弦1.0。  → 直接使用正弦函数
```

### 2.4 导入多个函数

**语法：** `引 模块名 之 函数名 函数名...`

**示例：**
```
引 数学 之 正弦 余弦 正切
正弦1.0。
余弦1.0。
```

### 2.5 导出

**语法：** `出 名称`

**示例：**
```
定平方 = 函x 乘x x。
定立方 = 函x 幂x 3。

出 平方
出 立方
```

### 2.6 导出多个

**语法：** `出 名称 名称...`

**示例：**
```
出 平方 立方
```

### 2.7 默认导出

**语法：** `出 默认 值`

**示例：**
```
定主 = 函x 印x。
出 默认 主
```

---

## 3. 模块文件结构

### 3.1 文件命名

- 模块文件：`模块名.yan`
- 包目录：`模块名/`
  - `主.yan` 或 `__init__.yan`（包入口）

### 3.2 示例模块

**文件：`数学.yan`**
```
注 数学工具模块

定圆周率 = 3.14159265359
定自然常数 = 2.71828182846

定平方 = 函x 乘x x。
定立方 = 函x 幂x 3。
定开方 = 函x 幂x 0.5。

出 圆周率 自然常数
出 平方 立方 开方
```

**文件：`工具/字符串.yan`**
```
注 字符串工具模块

定反转 = 函s 
  $(s[::-1])。

定大写 = 函s
  $(s.upper())。

出 反转 大写
```

---

## 4. 模块搜索路径

### 4.1 搜索顺序

1. 当前目录
2. `YANPATH` 环境变量指定的目录
3. 标准库目录（`~/.yan/lib/`）
4. 第三方库目录（`~/.yan/packages/`）

### 4.2 配置

**环境变量：**
```bash
export YANPATH="/path/to/libs:/another/path"
```

**配置文件：** `~/.yan/config.yaml`
```yaml
paths:
  - ./lib
  - ~/.yan/lib
  - ~/.yan/packages
```

---

## 5. 模块加载器实现

### 5.1 核心类

```python
class ModuleLoader:
    """模块加载器"""
    
    def __init__(self, search_paths: List[str] = None):
        self.search_paths = search_paths or self._default_paths()
        self.loaded_modules: Dict[str, Module] = {}
    
    def load(self, module_name: str) -> Module:
        """加载模块"""
        # 检查缓存
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        # 查找模块文件
        module_path = self._find_module(module_name)
        if not module_path:
            raise ImportError(f"模块 '{module_name}' 未找到")
        
        # 解析模块
        module = self._parse_module(module_path)
        
        # 缓存
        self.loaded_modules[module_name] = module
        
        return module
    
    def _find_module(self, name: str) -> Optional[str]:
        """查找模块文件"""
        for path in self.search_paths:
            # 单文件模块
            file_path = os.path.join(path, f"{name}.yan")
            if os.path.exists(file_path):
                return file_path
            
            # 包模块
            init_path = os.path.join(path, name, "主.yan")
            if os.path.exists(init_path):
                return init_path
            
            init_path = os.path.join(path, name, "__init__.yan")
            if os.path.exists(init_path):
                return init_path
        
        return None
    
    def _parse_module(self, path: str) -> Module:
        """解析模块"""
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 解析源码
        lexer = Lexer()
        tokens = lexer.tokenize(source, path)
        
        parser = Parser(source=source, filename=path)
        ast = parser.parse(tokens)
        
        # 提取导出
        exports = self._extract_exports(ast)
        
        return Module(name, path, exports)
```

### 5.2 模块对象

```python
@dataclass
class Module:
    """模块对象"""
    name: str
    path: str
    exports: Dict[str, Any]
    namespace: Dict[str, Any] = None
    
    def get(self, name: str) -> Any:
        """获取导出的值"""
        if name not in self.exports:
            raise AttributeError(f"模块 '{self.name}' 没有导出 '{name}'")
        return self.exports[name]
```

---

## 6. 语法扩展

### 6.1 新增 AST 节点

```python
@dataclass
class Import(Node):
    """导入语句"""
    module: str           # 模块名
    names: List[str]      # 导入的名称（空列表表示导入全部）
    alias: Optional[str]  # 别名

@dataclass
class Export(Node):
    """导出语句"""
    names: List[str]      # 导出的名称
    default: bool         # 是否为默认导出
```

### 6.2 EBNF 扩展

```ebnf
Statement   ::= ...
            |   Import
            |   Export

Import      ::= '引' ModuleName ('为' Name)?
            |   '引' ModuleName '之' Name+

Export      ::= '出' Name+
            |   '出' '默认' Expression

ModuleName  ::= WORD ('.' WORD)*
```

---

## 7. 标准库模块

### 7.1 内置模块

| 模块名 | 说明 |
|--------|------|
| 数学 | 数学函数 |
| 字符串 | 字符串操作 |
| 列表 | 列表操作 |
| 文件 | 文件操作 |
| 网络 | 网络请求 |
| 时间 | 时间处理 |
| 系统 | 系统调用 |
| JSON | JSON 解析 |
| 正则 | 正则表达式 |

### 7.2 模块示例

**`数学.yan`**
```
注 标准数学库

出 圆周率 自然常数
出 正弦 余弦 正切
出 开方 幂 绝对
出 取整 进位 四舍五入
出 随机 随机整数
```

**`网络.yan`**
```
注 网络请求库

定获取 = 函url
  {{import requests; requests.get(url).text}}。

定发布 = 函url 数据
  {{import requests; requests.post(url, data=data).text}}。

出 获取 发布
```

---

## 8. 包管理器

### 8.1 包配置文件

**`包配置.yaml`**
```yaml
名称: 我的工具包
版本: "1.0.0"
描述: 言语言工具包
作者: 张三
依赖:
  - 数学: "^1.0"
  - 网络: "^0.5"

文件:
  - 源码: "src/"
  - 文档: "docs/"
  - 示例: "examples/"
```

### 8.2 包管理命令

```bash
# 安装包
言包 安装 包名

# 卸载包
言包 卸载 包名

# 更新包
言包 更新 包名

# 发布包
言包 发布

# 搜索包
言包 搜索 关键词
```

---

## 9. 实现计划

### 9.1 第一阶段：基础模块系统

- [ ] 实现 `引` 和 `出` 语法解析
- [ ] 实现模块加载器
- [ ] 实现模块缓存
- [ ] 支持单文件模块

### 9.2 第二阶段：标准库模块化

- [ ] 将现有标准库拆分为模块
- [ ] 创建标准模块文件
- [ ] 更新文档

### 9.3 第三阶段：包管理器

- [ ] 设计包配置格式
- [ ] 实现包安装/卸载
- [ ] 实现依赖解析
- [ ] 创建包仓库

---

## 10. 示例

### 10.1 创建模块

**文件：`工具.yan`**
```
注 工具函数模块

定问候 = 函名
  连"你好，" 名"！"。

定平方 = 函x
  乘x x。

定立方 = 函x
  幂x 3。

出 问候 平方 立方
```

### 10.2 使用模块

**文件：`主.yan`**
```
引 工具

工具问候"张三"。  → 你好，张三！
工具平方5。       → 25
工具立方3。       → 27
```

### 10.3 导入特定函数

```
引 工具 之 平方 立方

平方5。  → 25
立方3。  → 27
```

### 10.4 使用别名

```
引 工具 为 具

具平方5。  → 25
```

---

## 11. 注意事项

### 11.1 循环导入

**问题：** 模块 A 导入 B，B 又导入 A。

**解决方案：**
1. 检测循环导入，抛出错误
2. 延迟加载：只在实际使用时导入

### 11.2 命名冲突

**问题：** 导入的名称与本地名称冲突。

**解决方案：**
1. 使用别名：`引 模块 为 别名`
2. 显式导入：`引 模块 之 名称`

### 11.3 模块缓存

**策略：** 模块只加载一次，后续导入使用缓存。

**好处：**
- 提高性能
- 保证单例模式

---

## 12. 参考资料

- [Python 模块系统](https://docs.python.org/zh-cn/3/tutorial/modules.html)
- [Node.js 模块系统](https://nodejs.org/api/modules.html)
- [Rust 模块系统](https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html)
