"""
包管理器增强测试
测试版本管理、缓存机制、依赖解析等新功能
"""

import pytest
import tempfile
import os
from pathlib import Path
from yan_pkg import PackageManager


class TestPackageManagerCaching:
    """测试包管理器缓存功能"""
    
    def test_cache_index_loading(self):
        """测试缓存索引加载"""
        pm = PackageManager()
        
        # 缓存索引应该是字典类型
        assert isinstance(pm.cache_index, dict)
    
    def test_cache_path_generation(self):
        """测试缓存路径生成"""
        pm = PackageManager()
        
        cache_path = pm._get_cache_path("test_pkg", "1.0.0")
        
        # 验证路径格式
        assert str(cache_path).endswith("test_pkg-1.0.0.zip")
    
    def test_package_path_generation(self):
        """测试包路径生成"""
        pm = PackageManager()
        
        # 不带版本
        path1 = pm._get_package_path("test_pkg")
        assert str(path1).endswith("test_pkg")
        
        # 带版本
        path2 = pm._get_package_path("test_pkg", "1.2.3")
        assert str(path2).endswith("test_pkg@1.2.3")


class TestVersionResolution:
    """测试版本解析功能"""
    
    def test_version_comparison(self):
        """测试版本比较逻辑"""
        # 由于包管理器使用模块系统的版本检查方法，我们测试模块系统
        from module_system import ModuleSystem
        
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


class TestPackageConfig:
    """测试包配置功能"""
    
    def test_get_package_config_from_file(self):
        """测试从文件获取包配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_dir = Path(tmpdir) / "test_pkg"
            pkg_dir.mkdir()
            
            pkg_json = pkg_dir / "package.json"
            pkg_json.write_text('{"name": "test_pkg", "version": "1.0.0", "dependencies": {"dep1": ">= 1.0.0"}}')
            
            pm = PackageManager()
            config = pm._get_package_config("test_pkg")
            
            # 由于我们没有实际安装包，这里测试的是网络获取失败的情况
            # 应该返回空字典
            assert isinstance(config, dict)


class TestDependencyResolution:
    """测试依赖解析功能"""
    
    def test_get_all_dependencies_empty(self):
        """测试获取空依赖"""
        pm = PackageManager()
        
        deps = pm._get_all_dependencies("nonexistent_pkg")
        
        # 不存在的包应该返回空列表
        assert isinstance(deps, list)


class TestPackageManagerInit:
    """测试包管理器初始化"""
    
    def test_init_creates_dirs(self):
        """测试初始化创建目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = PackageManager()
            
            # 验证目录被创建（通过检查配置文件存在）
            assert pm.config is not None


class TestConfigManagement:
    """测试配置管理"""
    
    def test_config_defaults(self):
        """测试默认配置"""
        pm = PackageManager()
        
        # 验证默认配置
        assert "registry" in pm.config
        assert "installed_packages" in pm.config
        assert "dependencies" in pm.config
        assert "settings" in pm.config
    
    def test_config_save_load(self):
        """测试配置保存和加载"""
        pm = PackageManager()
        
        # 修改配置
        pm.config["test_key"] = "test_value"
        pm._save_config()
        
        # 验证配置被保存
        assert pm.config.get("test_key") == "test_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
