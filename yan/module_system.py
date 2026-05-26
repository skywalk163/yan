#!/usr/bin/env python3
"""
言语言模块系统 - 增强版
支持 '导入'（import）和 '导出'（export）语法
新增功能：
- 版本管理
- 依赖解析
- 循环依赖延迟加载
- 模块热更新
- 包缓存机制
"""

import os
import sys
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Module:
    """言语言模块"""
    name: str
    path: Path
    source: str
    exports: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
    # 新增字段
    version: str = "1.0.0"
    last_modified: datetime = field(default_factory=datetime.now)
    source_hash: str = ""
    is_loaded: bool = False
    is_hot_reload_enabled: bool = False
    hot_reload_callbacks: List[Callable] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后计算源码哈希"""
        self.source_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """计算源码哈希值，用于检测变化"""
        return hashlib.md5(self.source.encode('utf-8')).hexdigest()
    
    def export(self, name: str, value: Any):
        """导出一个名称"""
        self.exports[name] = value
    
    def has_export(self, name: str) -> bool:
        """检查是否导出了某个名称"""
        return name in self.exports
    
    def add_hot_reload_callback(self, callback: Callable):
        """添加热更新回调函数"""
        self.hot_reload_callbacks.append(callback)
    
    def trigger_hot_reload(self):
        """触发热更新回调"""
        for callback in self.hot_reload_callbacks:
            try:
                callback(self)
            except Exception as e:
                print(f"热更新回调失败: {e}")
    
    def check_for_changes(self) -> bool:
        """检查模块源文件是否发生变化"""
        if self.path.exists():
            with open(self.path, 'r', encoding='utf-8') as f:
                current_source = f.read()
            current_hash = hashlib.md5(current_source.encode('utf-8')).hexdigest()
            return current_hash != self.source_hash
        return False


@dataclass
class ImportStatement:
    """导入语句"""
    path: str
    alias: Optional[str] = None  # 别名，如：引 "utils" 为 u
    selective: List[str] = field(default_factory=list)  # 选择性导入，如：引 "utils" 取 add, sub
    
    # 新增字段
    version_spec: Optional[str] = None  # 版本约束，如：">= 1.0.0"
    from_package: Optional[str] = None  # 从哪个包导入


class ModuleError(Exception):
    """模块系统错误"""
    def __init__(self, message: str, module_name: str = None):
        self.module_name = module_name
        super().__init__(message)


class CircularDependencyError(ModuleError):
    """循环依赖错误"""
    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        cycle_str = " -> ".join(cycle)
        message = f"检测到循环依赖: {cycle_str}"
        super().__init__(message, module_name=cycle[-1])


class ModuleSystem:
    """言语言模块系统 - 增强版"""
    
    def __init__(self, search_paths: Optional[List[Path]] = None, max_cache_size: int = 100, detect_cycles: bool = True, enable_hot_reload: bool = False):
        self.search_paths: List[Path] = search_paths or []
        self.cache: Dict[str, Module] = {}  # 模块缓存
        self.cache_order: List[str] = []  # LRU顺序
        self.max_cache_size = max_cache_size  # 最大缓存大小
        self.current_path: Optional[Path] = None
        self.detect_cycles = detect_cycles  # 是否检测循环依赖
        self.loading_stack: List[str] = []  # 当前正在加载的模块路径栈（用于循环检测）
        
        # 新增功能
        self.enable_hot_reload = enable_hot_reload  # 是否启用热更新
        self.lazy_modules: Dict[str, Module] = {}  # 延迟加载的模块（用于循环依赖）
        self.hot_reload_interval = 1.0  # 热更新检查间隔（秒）
        self.hot_reload_thread = None  # 热更新监控线程
        self.package_versions: Dict[str, str] = {}  # 包版本映射
        self.dependency_graph: Dict[str, List[str]] = {}  # 依赖图
        
        # 添加当前目录和标准库目录
        self._init_search_paths()
        
        # 初始化热更新监控
        if self.enable_hot_reload:
            self._start_hot_reload_monitor()
    
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
    
    def _update_lru(self, key: str):
        """更新LRU缓存顺序"""
        if key in self.cache_order:
            self.cache_order.remove(key)
        self.cache_order.append(key)
        
        # 如果超过最大缓存大小，移除最久未使用的
        while len(self.cache_order) > self.max_cache_size:
            oldest_key = self.cache_order.pop(0)
            if oldest_key in self.cache:
                del self.cache[oldest_key]
    
    def load_module(self, module_path: str, current_file: Optional[Path] = None, version_spec: Optional[str] = None) -> Module:
        """
        加载一个模块
        如果已在缓存中则直接返回
        
        :param module_path: 模块路径
        :param current_file: 当前文件路径（用于相对路径解析）
        :param version_spec: 版本约束（如 ">= 1.0.0"）
        """
        # 检查缓存
        resolved_path = self.resolve_module(module_path, current_file)
        if not resolved_path:
            raise ModuleError(f"找不到模块: {module_path}", module_path)
        
        # 使用绝对路径作为缓存键
        abs_path = str(resolved_path.resolve())
        
        # 循环依赖检测和延迟加载
        if self.detect_cycles:
            if abs_path in self.loading_stack:
                # 检测到循环依赖，使用延迟加载
                return self._handle_circular_dependency(abs_path, resolved_path)
            
            # 将当前模块加入加载栈
            self.loading_stack.append(abs_path)
        
        if abs_path in self.cache:
            # 命中缓存，检查版本约束
            cached_module = self.cache[abs_path]
            if version_spec and not self._check_version(cached_module.version, version_spec):
                raise ModuleError(f"模块 {module_path} 版本不满足约束: {version_spec}", module_path)
            
            # 更新LRU顺序
            self._update_lru(abs_path)
            # 从加载栈移除
            if self.detect_cycles and abs_path in self.loading_stack:
                self.loading_stack.remove(abs_path)
            return cached_module
        
        try:
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
            
            # 尝试读取版本信息（从 package.json）
            module.version = self._extract_version(resolved_path)
            
            # 检查版本约束
            if version_spec and not self._check_version(module.version, version_spec):
                raise ModuleError(f"模块 {module_path} 版本 {module.version} 不满足约束: {version_spec}", module_path)
            
            # 保存到缓存（带LRU管理）
            self.cache[abs_path] = module
            self._update_lru(abs_path)
            
            # 解析导入语句（第一遍扫描）
            imports = self._parse_imports(source)
            
            # 加载依赖（支持版本约束）
            for imp in imports:
                try:
                    dep_module = self.load_module(imp.path, resolved_path, imp.version_spec)
                    module.dependencies.append(imp.path)
                except ModuleError as e:
                    raise ModuleError(f"加载模块 {module_path} 时失败，依赖 {imp.path} 无法加载", module_path) from e
            
            # 解析导出语句（第一遍扫描）
            exports = self._parse_exports(source)
            for export_name in exports:
                module.exports[export_name] = None  # 占位，实际值在完整编译后填入
            
            # 标记模块已加载
            module.is_loaded = True
            
            # 如果启用热更新，注册监控
            if self.enable_hot_reload:
                module.is_hot_reload_enabled = True
            
            return module
        finally:
            # 从加载栈移除（确保异常时也能清理）
            if self.detect_cycles and abs_path in self.loading_stack:
                self.loading_stack.remove(abs_path)
    
    def _handle_circular_dependency(self, abs_path: str, resolved_path: Path) -> Module:
        """
        处理循环依赖 - 使用延迟加载
        返回一个占位模块，实际内容在后续补全
        """
        if abs_path in self.lazy_modules:
            return self.lazy_modules[abs_path]
        
        # 创建延迟加载的占位模块
        module_name = resolved_path.stem
        lazy_module = Module(
            name=module_name,
            path=resolved_path,
            source="",
            is_loaded=False
        )
        
        # 保存到延迟加载缓存
        self.lazy_modules[abs_path] = lazy_module
        
        return lazy_module
    
    def _extract_version(self, module_path: Path) -> str:
        """
        从模块所在目录的 package.json 中提取版本信息
        """
        package_dir = module_path.parent
        package_json_path = package_dir / "package.json"
        
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_info = json.load(f)
                    return package_info.get("version", "1.0.0")
            except:
                pass
        
        return "1.0.0"
    
    def _check_version(self, current_version: str, version_spec: str) -> bool:
        """
        检查版本是否满足约束
        
        :param current_version: 当前版本
        :param version_spec: 版本约束（如 ">= 1.0.0", "< 2.0.0", "== 1.2.3"）
        :return: 是否满足约束
        """
        try:
            # 解析版本约束
            import re
            match = re.match(r'([<>!=]+)\s*([\d.]+)', version_spec.strip())
            if not match:
                return True  # 无法解析约束，视为满足
            
            operator = match.group(1)
            spec_version = match.group(2)
            
            # 比较版本
            current_parts = list(map(int, current_version.split('.')[:3]))
            spec_parts = list(map(int, spec_version.split('.')[:3]))
            
            # 补齐版本号位数
            while len(current_parts) < 3:
                current_parts.append(0)
            while len(spec_parts) < 3:
                spec_parts.append(0)
            
            if operator == '==' or operator == '=':
                return current_parts == spec_parts
            elif operator == '!=':
                return current_parts != spec_parts
            elif operator == '>':
                return current_parts > spec_parts
            elif operator == '<':
                return current_parts < spec_parts
            elif operator == '>=':
                return current_parts >= spec_parts
            elif operator == '<=':
                return current_parts <= spec_parts
            
            return True
        except:
            return True  # 解析失败，视为满足
    
    def _parse_imports(self, source: str) -> List[ImportStatement]:
        """
        解析源码中的导入语句
        支持：
        - 导入 "module"
        - 导入 "module" 为 alias
        - 导入 "module" 取 name1, name2
        - 导入 "module" 取 name1, name2 为 a, b
        """
        imports: List[ImportStatement] = []
        
        # 匹配导入语句的正则
        # 简单匹配：导入 后接字符串，可选后面的 为 或 取
        import_pattern = re.compile(
            r'导入\s*[\"\']([^\"\']+)[\"\']\s*(?:为\s*(\w+))?\s*(?:取\s*([^\.\n]+))?',
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
        export_pattern = re.compile(r'导出\s*([^\.\n]+)', re.UNICODE)
        
        lines = source.split('\n')
        for line in lines:
            match = export_pattern.search(line)
            if match:
                exports_str = match.group(1).strip()
                
                # 解析导出列表
                parts = [p.strip() for p in exports_str.split(',')]
                
                for part in parts:
                    if part:
                        # 处理"导出 函"或"导出 定"
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
        self.cache_order.clear()
    
    def build_dependency_graph(self) -> Dict[str, List[str]]:
        """
        构建依赖图
        返回: {模块名: [依赖模块名列表]}
        """
        graph = {}
        for module in self.cache.values():
            deps = []
            for dep_path in module.dependencies:
                # 尝试解析依赖模块名称
                dep_module = self.get_module(Path(dep_path).stem)
                if dep_module:
                    deps.append(dep_module.name)
                else:
                    deps.append(Path(dep_path).stem)
            graph[module.name] = deps
        return graph
    
    def find_dependencies(self, module_name: str, include_indirect: bool = True) -> List[str]:
        """
        查找模块的依赖
        :param module_name: 模块名称
        :param include_indirect: 是否包含间接依赖
        :return: 依赖模块名称列表
        """
        module = self.get_module(module_name)
        if not module:
            return []
        
        if not include_indirect:
            return list(set(module.dependencies))
        
        # 使用BFS查找所有依赖
        visited = set()
        queue = [module_name]
        dependencies = []
        
        while queue:
            current_name = queue.pop(0)
            if current_name in visited:
                continue
            visited.add(current_name)
            
            current_module = self.get_module(current_name)
            if not current_module:
                continue
            
            for dep_path in current_module.dependencies:
                dep_name = Path(dep_path).stem
                if dep_name not in visited:
                    dependencies.append(dep_name)
                    queue.append(dep_name)
        
        return list(set(dependencies))
    
    def is_standard_library(self, module_name: str) -> bool:
        """
        检查模块是否是标准库模块
        """
        stdlib_paths = [
            Path(__file__).parent / "lib",
            Path(__file__).parent / "stdlib"
        ]
        
        for stdlib_path in stdlib_paths:
            if stdlib_path.exists():
                candidate = stdlib_path / f"{module_name}.yan"
                if candidate.exists():
                    return True
                candidate_dir = stdlib_path / module_name
                if candidate_dir.is_dir() and (candidate_dir / "index.yan").exists():
                    return True
        
        return False
    
    def list_standard_library_modules(self) -> List[str]:
        """
        列出所有标准库模块
        """
        modules = []
        stdlib_paths = [
            Path(__file__).parent / "lib",
            Path(__file__).parent / "stdlib"
        ]
        
        for stdlib_path in stdlib_paths:
            if stdlib_path.exists():
                for item in stdlib_path.iterdir():
                    if item.is_file() and item.suffix == ".yan":
                        modules.append(item.stem)
                    elif item.is_dir():
                        if (item / "index.yan").exists():
                            modules.append(item.name)
        
        return sorted(list(set(modules)))
    
    # ====================
    # 热更新支持方法
    # ====================
    
    def _start_hot_reload_monitor(self):
        """启动热更新监控线程"""
        import threading
        import time
        
        def monitor():
            while self.enable_hot_reload:
                time.sleep(self.hot_reload_interval)
                self._check_for_changes()
        
        self.hot_reload_thread = threading.Thread(target=monitor, daemon=True)
        self.hot_reload_thread.start()
    
    def _check_for_changes(self):
        """检查所有模块是否发生变化"""
        for abs_path, module in list(self.cache.items()):
            if module.is_hot_reload_enabled and module.check_for_changes():
                print(f"检测到模块变化: {module.name}")
                self.reload_module(abs_path)
    
    def reload_module(self, module_path: str):
        """
        重新加载指定模块
        
        :param module_path: 模块路径（可以是绝对路径字符串或模块名称）
        """
        # 尝试解析路径
        if module_path in self.cache:
            abs_path = module_path
        else:
            # 尝试按名称查找
            module = self.get_module(module_path)
            if module:
                abs_path = str(module.path.resolve())
            else:
                raise ModuleError(f"找不到模块: {module_path}", module_path)
        
        if abs_path not in self.cache:
            raise ModuleError(f"模块不在缓存中: {module_path}", module_path)
        
        # 获取旧模块
        old_module = self.cache[abs_path]
        
        # 读取新源码
        try:
            with open(old_module.path, 'r', encoding='utf-8') as f:
                new_source = f.read()
        except Exception as e:
            raise ModuleError(f"读取模块源码失败: {e}", module_path)
        
        # 更新模块
        old_module.source = new_source
        old_module.source_hash = hashlib.md5(new_source.encode('utf-8')).hexdigest()
        old_module.last_modified = datetime.now()
        
        # 重新解析导入和导出
        imports = self._parse_imports(new_source)
        exports = self._parse_exports(new_source)
        
        # 更新依赖和导出
        old_module.dependencies = []
        for imp in imports:
            old_module.dependencies.append(imp.path)
        
        # 更新导出（保留旧的导出值，只添加新的）
        for export_name in exports:
            if export_name not in old_module.exports:
                old_module.exports[export_name] = None
        
        # 触发热更新回调
        old_module.trigger_hot_reload()
        
        print(f"模块已重新加载: {old_module.name}")
    
    def enable_hot_reload_for_module(self, module_name: str):
        """
        为指定模块启用热更新
        
        :param module_name: 模块名称
        """
        module = self.get_module(module_name)
        if module:
            module.is_hot_reload_enabled = True
        else:
            raise ModuleError(f"找不到模块: {module_name}", module_name)
    
    def disable_hot_reload_for_module(self, module_name: str):
        """
        为指定模块禁用热更新
        
        :param module_name: 模块名称
        """
        module = self.get_module(module_name)
        if module:
            module.is_hot_reload_enabled = False
        else:
            raise ModuleError(f"找不到模块: {module_name}", module_name)
    
    def shutdown_hot_reload(self):
        """停止热更新监控"""
        self.enable_hot_reload = False
        if self.hot_reload_thread:
            self.hot_reload_thread.join(timeout=2)
    
    # ====================
    # 依赖解析方法
    # ====================
    
    def resolve_dependencies(self, module_name: str, version_spec: Optional[str] = None) -> Dict[str, str]:
        """
        解析模块的所有依赖及其版本
        
        :param module_name: 模块名称
        :param version_spec: 版本约束
        :return: {依赖模块名: 版本号}
        """
        dependencies = {}
        module = self.get_module(module_name)
        
        if not module:
            try:
                module = self.load_module(module_name)
            except ModuleError:
                return dependencies
        
        # 遍历直接依赖
        for dep_path in module.dependencies:
            dep_name = Path(dep_path).stem
            dep_module = self.get_module(dep_name)
            if dep_module:
                dependencies[dep_name] = dep_module.version
        
        return dependencies
    
    def validate_dependencies(self) -> List[str]:
        """
        验证所有已加载模块的依赖是否满足版本约束
        
        :return: 不满足约束的依赖列表
        """
        issues = []
        
        for module in self.cache.values():
            imports = self._parse_imports(module.source)
            for imp in imports:
                if imp.version_spec:
                    dep_module = self.get_module(Path(imp.path).stem)
                    if dep_module:
                        if not self._check_version(dep_module.version, imp.version_spec):
                            issues.append(
                                f"{module.name} 依赖 {dep_module.name} {dep_module.version}，但需要 {imp.version_spec}"
                            )
        
        return issues


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
        return token.type == TokenType.WORD and token.value == "导入"
    
    @staticmethod
    def is_export_stmt(tokens: List['Token'], pos: int) -> bool:
        """检查是否是导出语句"""
        from lexer import TokenType
        
        if pos >= len(tokens):
            return False
        
        token = tokens[pos]
        return token.type == TokenType.WORD and token.value == "导出"


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
        result = f'导入 "{self.path}"'
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
        return f"导出 {', '.join(self.names)}"


if __name__ == "__main__":
    # 简单测试
    print("模块系统模块加载成功！")
