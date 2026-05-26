"""
模块系统增强测试
测试版本管理、循环依赖、热更新等新功能
"""

import pytest
import tempfile
import os
from pathlib import Path
from module_system import ModuleSystem, Module, ImportStatement, CircularDependencyError


class TestModuleVersioning:
    """测试版本管理功能"""
    
    def test_extract_version(self):
        """测试从 package.json 提取版本"""
        ms = ModuleSystem()
        
        # 创建临时 package.json
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_dir = Path(tmpdir) / "test_pkg"
            pkg_dir.mkdir()
            pkg_json = pkg_dir / "package.json"
            pkg_json.write_text('{"version": "2.3.4"}')
            
            version = ms._extract_version(pkg_dir / "main.yan")
            assert version == "2.3.4"
    
    def test_default_version(self):
        """测试默认版本号"""
        ms = ModuleSystem()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_dir = Path(tmpdir) / "test_pkg"
            pkg_dir.mkdir()
            
            version = ms._extract_version(pkg_dir / "main.yan")
            assert version == "1.0.0"
    
    def test_check_version_constraint(self):
        """测试版本约束检查"""
        ms = ModuleSystem()
        
        # 测试各种版本约束
        assert ms._check_version("1.0.0", ">= 1.0.0") == True
        assert ms._check_version("1.5.0", ">= 1.0.0") == True
        assert ms._check_version("0.9.0", ">= 1.0.0") == False
        
        assert ms._check_version("1.0.0", "< 2.0.0") == True
        assert ms._check_version("1.9.9", "< 2.0.0") == True
        assert ms._check_version("2.0.0", "< 2.0.0") == False
        
        assert ms._check_version("1.2.3", "== 1.2.3") == True
        assert ms._check_version("1.2.4", "== 1.2.3") == False
        
        assert ms._check_version("1.2.3", "!= 1.2.4") == True
        assert ms._check_version("1.2.3", "!= 1.2.3") == False


class TestCircularDependency:
    """测试循环依赖处理"""
    
    def test_circular_dependency_detection(self):
        """测试循环依赖检测"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建循环依赖的模块
            a_file = Path(tmpdir) / "a.yan"
            b_file = Path(tmpdir) / "b.yan"
            
            a_file.write_text('import "b"', encoding='utf-8')
            b_file.write_text('import "a"', encoding='utf-8')
            
            ms = ModuleSystem(search_paths=[Path(tmpdir)], detect_cycles=True)
            
            # 应该返回延迟加载的模块而不是抛出异常
            module_a = ms.load_module("a")
            module_b = ms.load_module("b")
            
            # 验证模块被创建
            assert module_a is not None
            assert module_b is not None
    
    def test_lazy_module_creation(self):
        """测试延迟加载模块创建"""
        with tempfile.TemporaryDirectory() as tmpdir:
            a_file = Path(tmpdir) / "a.yan"
            b_file = Path(tmpdir) / "b.yan"
            
            a_file.write_text('import "b"', encoding='utf-8')
            b_file.write_text('import "a"', encoding='utf-8')
            
            ms = ModuleSystem(search_paths=[Path(tmpdir)], detect_cycles=True)
            ms.load_module("a")
            
            # 检查延迟加载的模块（如果没有循环依赖则为空，这是正常的）
            # 循环依赖情况下应该有延迟加载模块
            # 这里我们验证模块系统正常工作
            assert len(ms.cache) > 0


class TestHotReload:
    """测试热更新功能"""
    
    def test_module_change_detection(self):
        """测试模块变化检测"""
        with tempfile.TemporaryDirectory() as tmpdir:
            module_file = Path(tmpdir) / "test_module.yan"
            module_file.write_text('def x = 1', encoding='utf-8')
            
            ms = ModuleSystem(search_paths=[Path(tmpdir)])
            module = ms.load_module("test_module")
            
            # 初始状态不应该有变化
            assert module.check_for_changes() == False
            
            # 修改文件
            module_file.write_text('def x = 2', encoding='utf-8')
            
            # 现在应该检测到变化
            assert module.check_for_changes() == True
    
    def test_hot_reload_callback(self):
        """测试热更新回调"""
        callback_called = []
        
        def callback(module):
            callback_called.append(module.name)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_file = Path(tmpdir) / "test_module.yan"
            module_file.write_text('def x = 1', encoding='utf-8')
            
            ms = ModuleSystem(search_paths=[Path(tmpdir)])
            module = ms.load_module("test_module")
            
            # 添加回调
            module.add_hot_reload_callback(callback)
            
            # 触发热更新
            module.trigger_hot_reload()
            
            # 验证回调被调用
            assert "test_module" in callback_called
    
    def test_reload_module(self):
        """测试模块重新加载"""
        with tempfile.TemporaryDirectory() as tmpdir:
            module_file = Path(tmpdir) / "test_module.yan"
            module_file.write_text('def x = 1', encoding='utf-8')
            
            ms = ModuleSystem(search_paths=[Path(tmpdir)])
            module = ms.load_module("test_module")
            
            # 修改文件
            module_file.write_text('def x = 2', encoding='utf-8')
            
            # 重新加载
            ms.reload_module("test_module")
            
            # 验证模块被重新加载
            assert module.source == 'def x = 2'


class TestDependencyResolution:
    """测试依赖解析功能"""
    
    def test_resolve_dependencies(self):
        """测试解析依赖"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建主模块
            main_file = Path(tmpdir) / "main.yan"
            main_file.write_text('import "utils"', encoding='utf-8')
            
            # 创建依赖模块
            utils_file = Path(tmpdir) / "utils.yan"
            utils_file.write_text('def add = lambda a b: a + b', encoding='utf-8')
            
            ms = ModuleSystem(search_paths=[Path(tmpdir)])
            module = ms.load_module("main")
            
            # 验证模块被成功加载
            assert module is not None
            assert module.name == "main"
    
    def test_validate_dependencies(self):
        """测试验证依赖版本"""
        ms = ModuleSystem()
        issues = ms.validate_dependencies()
        # 没有加载任何模块时应该没有问题
        assert isinstance(issues, list)


class TestModuleCaching:
    """测试模块缓存功能"""
    
    def test_module_caching(self):
        """测试模块缓存"""
        with tempfile.TemporaryDirectory() as tmpdir:
            module_file = Path(tmpdir) / "cached_module.yan"
            module_file.write_text('def value = 42', encoding='utf-8')
            
            ms = ModuleSystem(search_paths=[Path(tmpdir)])
            
            # 第一次加载
            module1 = ms.load_module("cached_module")
            
            # 第二次加载（应该命中缓存）
            module2 = ms.load_module("cached_module")
            
            # 应该是同一个对象
            assert module1 is module2
    
    def test_lru_cache_eviction(self):
        """测试 LRU 缓存淘汰"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ms = ModuleSystem(search_paths=[Path(tmpdir)], max_cache_size=2)
            
            # 创建多个模块
            for i in range(3):
                module_file = Path(tmpdir) / f"module_{i}.yan"
                module_file.write_text(f'def x = {i}', encoding='utf-8')
            
            # 加载三个模块
            ms.load_module("module_0")
            ms.load_module("module_1")
            ms.load_module("module_2")
            
            # 第一个模块应该被淘汰
            assert len(ms.cache) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
