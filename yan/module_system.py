#!/usr/bin/env python3
"""
言语言模块系统
支持 '引'（import）和 '出'（export）语法
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class Module:
    """言语言模块"""
    name: str
    path: Path
    source: str
    exports: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
    def export(self, name: str, value: Any):
        """导出一个名称"""
        self.exports[name] = value
    
    def has_export(self, name: str) -> bool:
        """检查是否导出了某个名称"""
        return name in self.exports


@dataclass
class ImportStatement:
    """导入语句"""
    path: str
    alias: Optional[str] = None  # 别名，如：引 "utils" 为 u
    selective: List[str] = field(default_factory=list)  # 选择性导入，如：引 "utils" 取 add, sub


class ModuleError(Exception):
    """模块系统错误"""
    def __init__(self, message: str, module_name: str = None):
        self.module_name = module_name
        super().__init__(message)


class ModuleSystem:
    """言语言模块系统"""
    
    def __init__(self, search_paths: Optional[List[Path]] = None):
        self.search_paths: List[Path] = search_paths or []
        self.cache: Dict[str, Module] = {}  # 模块缓存
        self.current_path: Optional[Path] = None
        
        # 添加当前目录和标准库目录
        self._init_search_paths()
    
    def _init_search_paths(self):
        """初始化搜索路径"""
        # 当前工作目录
        self.search_paths.append(Path.cwd())
        
        # 标准库目录（lib）
        stdlib_path = Path(__file__).parent / "lib"
        if stdlib_path.exists():
            self.search_paths.append(stdlib_path)
        
        # 备用标准库目录（stdlib）
        stdlib_path_backup = Path(__file__).parent / "stdlib"
        if stdlib_path_backup.exists():
            self.search_paths.append(stdlib_path_backup)
    
    def resolve_module(self, module_path: str, current_file: Optional[Path] = None) -> Optional[Path]:
        """
        解析模块路径
        支持：
        - 相对路径："./utils", "../common"
        - 标准库："collections", "math"
        - 绝对路径
        """
        path = Path(module_path)
        
        # 如果是绝对路径，直接检查
        if path.is_absolute():
            return self._check_extension(path)
        
        # 相对路径，相对于当前文件目录
        if current_file and (path.parts[0] == "." or path.parts[0] == ".."):
            base_dir = current_file.parent
            candidate = base_dir / path
            resolved = self._check_extension(candidate)
            if resolved:
                return resolved
        
        # 在搜索路径中查找
        for search_path in self.search_paths:
            candidate = search_path / path
            resolved = self._check_extension(candidate)
            if resolved:
                return resolved
        
        return None
    
    def _check_extension(self, path: Path) -> Optional[Path]:
        """检查文件扩展名"""
        if path.exists() and path.is_file():
            return path
        
        # 尝试添加 .yan 扩展名
        yan_path = path.with_suffix(".yan")
        if yan_path.exists() and yan_path.is_file():
            return yan_path
        
        # 检查是否是目录下的 index.yan
        if path.is_dir():
            index_path = path / "index.yan"
            if index_path.exists():
                return index_path
        
        return None
    
    def load_module(self, module_path: str, current_file: Optional[Path] = None) -> Module:
        """
        加载一个模块
        如果已在缓存中则直接返回
        """
        # 检查缓存
        resolved_path = self.resolve_module(module_path, current_file)
        if not resolved_path:
            raise ModuleError(f"找不到模块: {module_path}", module_path)
        
        # 使用绝对路径作为缓存键
        abs_path = str(resolved_path.resolve())
        if abs_path in self.cache:
            return self.cache[abs_path]
        
        # 读取模块源码
        with open(resolved_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 创建模块对象
        module_name = resolved_path.stem
        module = Module(
            name=module_name,
            path=resolved_path,
            source=source
        )
        
        # 保存到缓存
        self.cache[abs_path] = module
        
        # 解析导入语句（第一遍扫描）
        imports = self._parse_imports(source)
        
        # 加载依赖
        for imp in imports:
            try:
                dep_module = self.load_module(imp.path, resolved_path)
                module.dependencies.append(imp.path)
            except ModuleError as e:
                raise ModuleError(f"加载模块 {module_path} 时失败，依赖 {imp.path} 无法加载", module_path) from e
        
        # 解析导出语句（第一遍扫描）
        exports = self._parse_exports(source)
        for export_name in exports:
            module.exports[export_name] = None  # 占位，实际值在完整编译后填入
        
        return module
    
    def _parse_imports(self, source: str) -> List[ImportStatement]:
        """
        解析源码中的导入语句
        支持：
        - 引 "module"
        - 引 "module" 为 alias
        - 引 "module" 取 name1, name2
        - 引 "module" 取 name1, name2 为 a, b
        """
        imports: List[ImportStatement] = []
        
        # 匹配导入语句的正则
        # 简单匹配：引 后接字符串，可选后面的 为 或 取
        import_pattern = re.compile(
            r'引\s*[\"\']([^\"\']+)[\"\']\s*(?:为\s*(\w+))?\s*(?:取\s*([^\.\n]+))?',
            re.UNICODE
        )
        
        lines = source.split('\n')
        for line in lines:
            match = import_pattern.search(line)
            if match:
                path = match.group(1)
                alias = match.group(2)
                
                selective = []
                if match.group(3):
                    # 解析选择性导入
                    selective_str = match.group(3).strip()
                    if selective_str:
                        # 分割逗号，处理"取 name1, name2 为 a, b"
                        # 这里简化处理，先只支持简单的选择性导入
                        parts = [p.strip() for p in selective_str.split(',')]
                        selective = [p for p in parts if p]
                
                imports.append(ImportStatement(
                    path=path,
                    alias=alias,
                    selective=selective
                ))
        
        return imports
    
    def _parse_exports(self, source: str) -> List[str]:
        """
        解析源码中的导出语句
        支持：
        - 出 name
        - 出 name1, name2
        - 出 函 ...
        - 出 定 ...
        """
        exports: List[str] = []
        
        # 简单匹配导出语句
        export_pattern = re.compile(r'出\s*([^\.\n]+)', re.UNICODE)
        
        lines = source.split('\n')
        for line in lines:
            match = export_pattern.search(line)
            if match:
                exports_str = match.group(1).strip()
                
                # 解析导出列表
                parts = [p.strip() for p in exports_str.split(',')]
                
                for part in parts:
                    if part:
                        # 处理"出 函"或"出 定"
                        if part.startswith("函") or part.startswith("定"):
                            # 尝试提取函数名或变量名
                            # 这里简化处理，在实际的词法/语法分析中会更准确
                            name_match = re.search(r'(?:函|定)\s*(\w+)', part)
                            if name_match:
                                exports.append(name_match.group(1))
                        else:
                            # 直接导出名称
                            exports.append(part)
        
        return exports
    
    def get_module(self, name: str) -> Optional[Module]:
        """从缓存中获取模块"""
        for module in self.cache.values():
            if module.name == name:
                return module
        return None
    
    def clear_cache(self):
        """清空模块缓存"""
        self.cache.clear()


# =====================================
# 语法分析扩展：模块语句
# =====================================

class ModuleParser:
    """模块语句解析器（扩展）"""
    
    @staticmethod
    def is_import_stmt(tokens: List['Token'], pos: int) -> bool:
        """检查是否是导入语句"""
        from lexer import TokenType
        
        if pos >= len(tokens):
            return False
        
        token = tokens[pos]
        return token.type == TokenType.WORD and token.value == "引"
    
    @staticmethod
    def is_export_stmt(tokens: List['Token'], pos: int) -> bool:
        """检查是否是导出语句"""
        from lexer import TokenType
        
        if pos >= len(tokens):
            return False
        
        token = tokens[pos]
        return token.type == TokenType.WORD and token.value == "出"


# =====================================
# 节点定义
# =====================================

@dataclass
class ImportNode:
    """导入语句节点"""
    path: str
    alias: Optional[str] = None
    selective: List[str] = field(default_factory=list)
    
    def __str__(self):
        result = f'引 "{self.path}"'
        if self.alias:
            result += f" 为 {self.alias}"
        if self.selective:
            result += f" 取 {', '.join(self.selective)}"
        return result


@dataclass
class ExportNode:
    """导出语句节点"""
    names: List[str]
    definitions: List[Any] = field(default_factory=list)  # 可以是 FunctionDef, VarDef等
    
    def __str__(self):
        return f"出 {', '.join(self.names)}"


if __name__ == "__main__":
    # 简单测试
    print("模块系统模块加载成功！")
