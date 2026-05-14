"""
言语言模块加载器
"""

import os
import sys
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path

from error import RuntimeError, SourceLocation
from lexer import Lexer
from parser import Parser, process_adverbs
from codegen import PythonCodeGen
from nodes import Import, Export, Define


@dataclass
class Module:
    """模块对象"""
    name: str
    path: str
    exports: Dict[str, Any] = field(default_factory=dict)
    namespace: Dict[str, Any] = field(default_factory=dict)
    loaded: bool = False


class ModuleLoader:
    """模块加载器"""
    
    def __init__(self, search_paths: List[str] = None):
        self.search_paths = search_paths or self._default_paths()
        self.loaded_modules: Dict[str, Module] = {}
        self.loading_modules: Set[str] = set()  # 检测循环导入
    
    @staticmethod
    def _default_paths() -> List[str]:
        """默认搜索路径"""
        paths = []
        
        # 当前目录
        paths.append(os.getcwd())
        
        # 源码目录（如果从其他目录运行）
        src_dir = os.path.dirname(os.path.abspath(__file__))
        if src_dir not in paths:
            paths.append(src_dir)
        
        # examples 目录
        examples_path = os.path.join(src_dir, 'examples')
        if os.path.exists(examples_path):
            paths.append(examples_path)
        
        # 内置标准库目录
        lib_path = os.path.join(src_dir, 'lib')
        if os.path.exists(lib_path):
            paths.append(lib_path)
        
        # YANPATH 环境变量
        yanpath = os.environ.get('YANPATH')
        if yanpath:
            paths.extend(yanpath.split(os.pathsep))
        
        # 标准库目录
        home = Path.home()
        stdlib_path = home / '.yan' / 'lib'
        if stdlib_path.exists():
            paths.append(str(stdlib_path))
        
        # 第三方库目录
        packages_path = home / '.yan' / 'packages'
        if packages_path.exists():
            paths.append(str(packages_path))
        
        return paths
    
    def load(self, module_name: str, env: Dict[str, Any] = None) -> Module:
        """加载模块"""
        # 检查缓存
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        # 检测循环导入
        if module_name in self.loading_modules:
            raise RuntimeError(
                f"检测到循环导入: {module_name}",
                SourceLocation(0, 0)
            )
        
        self.loading_modules.add(module_name)
        
        try:
            # 查找模块文件
            module_path = self._find_module(module_name)
            if not module_path:
                raise RuntimeError(
                    f"模块 '{module_name}' 未找到",
                    SourceLocation(0, 0),
                    suggestion=f"请检查模块名是否正确，或使用 '言包 安装 {module_name}' 安装模块"
                )
            
            # 创建模块对象
            module = Module(module_name, module_path)
            
            # 解析模块
            self._parse_module(module, env)
            
            # 缓存
            self.loaded_modules[module_name] = module
            module.loaded = True
            
            return module
        
        finally:
            self.loading_modules.discard(module_name)
    
    def _find_module(self, name: str) -> Optional[str]:
        """查找模块文件"""
        for path in self.search_paths:
            # 单文件模块: 模块名.yan
            file_path = os.path.join(path, f"{name}.yan")
            if os.path.exists(file_path):
                return os.path.abspath(file_path)
            
            # 包模块: 模块名/主.yan
            init_path = os.path.join(path, name, "主.yan")
            if os.path.exists(init_path):
                return os.path.abspath(init_path)
            
            # 包模块: 模块名/__init__.yan
            init_path = os.path.join(path, name, "__init__.yan")
            if os.path.exists(init_path):
                return os.path.abspath(init_path)
        
        return None
    
    def _parse_module(self, module: Module, env: Dict[str, Any] = None):
        """解析模块"""
        # 读取源码
        with open(module.path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 词法分析
        lexer = Lexer()
        tokens = lexer.tokenize(source, module.path)
        
        # 语法分析
        parser = Parser()
        ast = parser.parse(tokens)
        ast = process_adverbs(ast)
        
        # 创建模块命名空间
        module_env = self._create_module_env(env)
        
        # 执行模块代码
        codegen = PythonCodeGen()
        py_code = codegen.generate(ast)
        
        # 执行代码
        try:
            exec(py_code, module_env, module_env)
        except Exception as e:
            raise RuntimeError(
                f"模块 '{module.name}' 执行错误: {e}",
                SourceLocation(0, 0)
            )
        
        # 提取导出
        exports = self._extract_exports(ast, module_env)
        module.exports = exports
        module.namespace = module_env
    
    def _create_module_env(self, parent_env: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建模块执行环境"""
        # 导入运行时函数
        from runtime import ALL_BUILTINS
        
        env = {}
        
        # 添加内置函数
        for name, (func, _) in ALL_BUILTINS.items():
            env[func.__name__] = func
        
        # 添加常用 Python 模块
        env.update({
            '__builtins__': __builtins__,
            'True': True,
            'False': False,
            'None': None,
        })
        
        return env
    
    def _extract_exports(self, ast, env: Dict[str, Any]) -> Dict[str, Any]:
        """从 AST 和环境中提取导出"""
        exports = {}
        
        for stmt in ast.statements:
            if isinstance(stmt, Export):
                for name in stmt.names:
                    if name == '__default__':
                        # 默认导出
                        exports['__default__'] = env.get('__default__')
                    elif name in env:
                        exports[name] = env[name]
                    else:
                        # 警告：导出的名称不存在
                        print(f"警告: 导出的名称 '{name}' 未定义", file=sys.stderr)
        
        # 如果没有显式导出，导出所有定义
        if not exports:
            for stmt in ast.statements:
                if isinstance(stmt, Define):
                    name = stmt.name
                    if name in env:
                        exports[name] = env[name]
        
        return exports
    
    def get_export(self, module_name: str, export_name: str, env: Dict[str, Any] = None) -> Any:
        """获取模块的导出"""
        module = self.load(module_name, env)
        
        if export_name not in module.exports:
            available = list(module.exports.keys())
            raise RuntimeError(
                f"模块 '{module_name}' 没有导出 '{export_name}'",
                SourceLocation(0, 0),
                suggestion=f"可用导出: {', '.join(available)}"
            )
        
        return module.exports[export_name]
    
    def get_all_exports(self, module_name: str, env: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取模块的所有导出"""
        module = self.load(module_name, env)
        return module.exports.copy()


# 全局模块加载器实例
_global_loader: Optional[ModuleLoader] = None


def get_module_loader() -> ModuleLoader:
    """获取全局模块加载器"""
    global _global_loader
    if _global_loader is None:
        _global_loader = ModuleLoader()
    return _global_loader


def reset_module_loader():
    """重置模块加载器（用于测试）"""
    global _global_loader
    _global_loader = None
