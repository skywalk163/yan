#!/usr/bin/env python3
"""
言语言模块系统单元测试
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yan_test import *
from yan_assertions import *
from module_system import ModuleSystem, ModuleError, ImportNode, ExportNode


@suite("模块系统基础测试")
class ModuleSystemBasicTests:

    @test("模块系统初始化")
    def test_module_system_init(self):
        """测试模块系统初始化"""
        ms = ModuleSystem()
        # 检查搜索路径不为空
        大于(长度(ms.search_paths), 0)
        # 检查缓存为空
        等(长度(ms.cache), 0)

    @test("模块路径解析 - 标准库")
    def test_resolve_stdlib(self):
        """测试解析标准库模块"""
        ms = ModuleSystem()
        result = ms.resolve_module("math")
        # 应该能找到标准库
        不为空(result)

    @test("模块路径解析 - 相对路径")
    def test_resolve_relative(self):
        """测试解析相对路径模块"""
        ms = ModuleSystem()
        
        # 创建临时测试文件
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_module.yan"
            test_file.write_text("定 x = 1。", encoding='utf-8')
            
            # 测试相对路径解析
            ms.search_paths.append(Path(tmpdir))
            result = ms.resolve_module("test_module")
            不为空(result)
            等(str(result), str(test_file))

    @test("模块路径解析 - 绝对路径")
    def test_resolve_absolute(self):
        """测试解析绝对路径模块"""
        ms = ModuleSystem()
        
        # 创建临时测试文件
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_abs.yan"
            test_file.write_text("定 y = 2。", encoding='utf-8')
            
            # 测试绝对路径解析
            result = ms.resolve_module(str(test_file))
            不为空(result)

    @test("模块路径解析 - 不存在的模块")
    def test_resolve_not_found(self):
        """测试解析不存在的模块"""
        ms = ModuleSystem()
        result = ms.resolve_module("nonexistent_module_xyz123")
        为空(result)

    @test("模块加载")
    def test_load_module(self):
        """测试加载模块"""
        ms = ModuleSystem()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "utils.yan"
            test_file.write_text('出 加。\n定 加 = 函 x y x加 y。', encoding='utf-8')
            
            ms.search_paths.append(Path(tmpdir))
            module = ms.load_module("utils")
            
            不为空(module)
            等(module.name, "utils")
            包含(module.source, "出 加")
            包含(module.exports, "加")


@suite("导入节点测试")
class ImportNodeTests:

    @test("基本导入节点")
    def test_basic_import(self):
        """测试基本导入节点"""
        imp = ImportNode(path="math")
        等(imp.path, "math")
        为空(imp.alias)
        等(长度(imp.selective), 0)

    @test("别名导入节点")
    def test_alias_import(self):
        """测试别名导入节点"""
        imp = ImportNode(path="math", alias="m")
        等(imp.path, "math")
        等(imp.alias, "m")

    @test("选择性导入节点")
    def test_selective_import(self):
        """测试选择性导入节点"""
        imp = ImportNode(path="math", selective=["加", "乘"])
        等(imp.path, "math")
        等(imp.selective, ["加", "乘"])

    @test("导入节点字符串表示")
    def test_import_str(self):
        """测试导入节点字符串表示"""
        imp = ImportNode(path="math", alias="m", selective=["加", "乘"])
        为真(包含(str(imp), "math"))
        为真(包含(str(imp), "m"))


@suite("导出节点测试")
class ExportNodeTests:

    @test("基本导出节点")
    def test_basic_export(self):
        """测试基本导出节点"""
        exp = ExportNode(names=["加", "减"])
        等(exp.names, ["加", "减"])
        等(长度(exp.definitions), 0)

    @test("导出节点字符串表示")
    def test_export_str(self):
        """测试导出节点字符串表示"""
        exp = ExportNode(names=["加", "减"])
        为真(包含(str(exp), "加"))
        为真(包含(str(exp), "减"))


@suite("循环依赖检测测试")
class CircularDependencyTests:

    @test("检测循环依赖")
    def test_detect_circular_dependency(self):
        """测试检测循环依赖"""
        ms = ModuleSystem()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建循环依赖的两个模块
            a_file = Path(tmpdir) / "a.yan"
            b_file = Path(tmpdir) / "b.yan"
            
            a_file.write_text('引 "b"。', encoding='utf-8')
            b_file.write_text('引 "a"。', encoding='utf-8')
            
            ms.search_paths.append(Path(tmpdir))
            
            # 应该抛出循环依赖错误
            try:
                ms.load_module("a")
                为假(True)  # 不应该到达这里
            except ModuleError as e:
                为真(包含(str(e), "循环依赖"))

    @test("检测深层循环依赖")
    def test_detect_deep_circular_dependency(self):
        """测试检测深层循环依赖"""
        ms = ModuleSystem()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            a_file = Path(tmpdir) / "a.yan"
            b_file = Path(tmpdir) / "b.yan"
            c_file = Path(tmpdir) / "c.yan"
            
            a_file.write_text('引 "b"。', encoding='utf-8')
            b_file.write_text('引 "c"。', encoding='utf-8')
            c_file.write_text('引 "a"。', encoding='utf-8')
            
            ms.search_paths.append(Path(tmpdir))
            
            try:
                ms.load_module("a")
                为假(True)
            except ModuleError as e:
                为真(包含(str(e), "循环依赖"))


@suite("模块缓存测试")
class ModuleCacheTests:

    @test("模块缓存")
    def test_module_cache(self):
        """测试模块缓存功能"""
        ms = ModuleSystem()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "cached.yan"
            test_file.write_text("定 x = 1。", encoding='utf-8')
            
            ms.search_paths.append(Path(tmpdir))
            
            # 第一次加载
            module1 = ms.load_module("cached")
            # 第二次加载（应该使用缓存）
            module2 = ms.load_module("cached")
            
            # 应该是同一个对象
            等(id(module1), id(module2))

    @test("清空模块缓存")
    def test_clear_cache(self):
        """测试清空模块缓存"""
        ms = ModuleSystem()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "clear_cache.yan"
            test_file.write_text("定 x = 1。", encoding='utf-8')
            
            ms.search_paths.append(Path(tmpdir))
            ms.load_module("clear_cache")
            
            # 缓存不为空
            大于(长度(ms.cache), 0)
            
            # 清空缓存
            ms.clear_cache()
            
            # 缓存为空
            等(长度(ms.cache), 0)


@suite("代码生成测试")
class CodeGenerationTests:

    @test("导入节点代码生成")
    def test_import_code_gen(self):
        """测试导入节点代码生成"""
        from codegen import PythonCodeGen
        
        codegen = PythonCodeGen()
        
        # 测试基本导入
        imp1 = ImportNode(path="math")
        code1 = codegen._gen_import_node(imp1)
        等(code1, "import math")
        
        # 测试别名导入
        imp2 = ImportNode(path="math", alias="m")
        code2 = codegen._gen_import_node(imp2)
        等(code2, "import math as m")
        
        # 测试选择性导入
        imp3 = ImportNode(path="math", selective=["加", "乘"])
        code3 = codegen._gen_import_node(imp3)
        等(code3, "from math import 加, 乘")

    @test("导出节点代码生成")
    def test_export_code_gen(self):
        """测试导出节点代码生成"""
        from codegen import PythonCodeGen
        
        codegen = PythonCodeGen()
        
        exp = ExportNode(names=["加", "减", "乘"])
        code = codegen._gen_export_node(exp)
        为真(包含(code, "__all__"))
        为真(包含(code, "加"))


if __name__ == "__main__":
    report = run()
    print_summary(report)
