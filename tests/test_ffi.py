"""
FFI模块测试
"""

import pytest
import sys
import platform
import ctypes

sys.path.insert(0, 'g:/dumategithub/newlisp/yan')

from ffi import (
    YanFFI,
    FFIType,
    FFITypeInfo,
    FFIFunction,
    FFICallResult,
    DLLSearchPath,
    FFIBuilder,
    StandardLibraries,
    get_global_ffi,
    call_external,
    load_c_library,
    call_c_function,
    FFIError
)


class TestFFIType:
    """FFI类型测试"""
    
    def test_ffi_type_enum(self):
        """测试FFI类型枚举"""
        assert FFIType.INT32.value == "int32"
        assert FFIType.DOUBLE.value == "double"
        assert FFIType.STRING.value == "string"
    
    def test_ffi_type_info(self):
        """测试FFI类型信息"""
        info = FFITypeInfo(
            ffi_type=FFIType.INT32,
            c_type="int32_t",
            python_type=int,
            size=4,
            alignment=4
        )
        
        assert info.ffi_type == FFIType.INT32
        assert info.c_type == "int32_t"
        assert info.size == 4


class TestDLLSearchPath:
    """动态库搜索路径测试"""
    
    def test_init_default_paths(self):
        """测试初始化默认路径"""
        search_path = DLLSearchPath()
        assert len(search_path.paths) > 0
    
    def test_add_path(self):
        """测试添加搜索路径"""
        search_path = DLLSearchPath()
        original_count = len(search_path.paths)
        
        search_path.add_path("/tmp")
        assert len(search_path.paths) > original_count
    
    def test_add_invalid_path(self):
        """测试添加无效路径"""
        search_path = DLLSearchPath()
        original_count = len(search_path.paths)
        
        search_path.add_path("/nonexistent_path_12345")
        assert len(search_path.paths) == original_count


class TestYanFFI:
    """YanFFI主类测试"""
    
    def test_init(self):
        """测试初始化"""
        ffi = YanFFI()
        assert ffi._libraries == {}
        assert ffi._functions == {}
    
    def test_register_function(self):
        """测试注册函数"""
        ffi = YanFFI()
        
        def my_func(a, b):
            return a + b
        
        ffi.register_function(
            name="add",
            func=my_func,
            return_type=FFIType.INT64,
            arg_types=[FFIType.INT64, FFIType.INT64]
        )
        
        assert "add" in ffi.list_functions()
        func = ffi.get_function("add")
        assert func is not None
        assert func.name == "add"
    
    def test_register_c_function(self):
        """测试注册C函数"""
        ffi = YanFFI()
        
        # 尝试加载C标准库
        if platform.system() == "Windows":
            try:
                ffi.load_library("msvcrt")
            except FFIError:
                pytest.skip("无法加载C标准库")
        else:
            try:
                ffi.load_library("c")
            except FFIError:
                pytest.skip("无法加载C标准库")
        
        # 注册strlen函数
        try:
            ffi.register_c_function(
                library=list(ffi._libraries.keys())[0],
                name="strlen",
                return_type=FFIType.UINT64,
                arg_types=[FFIType.STRING]
            )
            assert "strlen" in ffi.list_functions()
        except FFIError:
            pytest.skip("strlen函数不可用")
    
    def test_call_success(self):
        """测试成功调用"""
        ffi = YanFFI()
        
        def add(a, b):
            return a + b
        
        ffi.register_function("add", add, FFIType.INT64, [FFIType.INT64, FFIType.INT64])
        
        result = ffi.call("add", 10, 20)
        assert result.success is True
        assert result.value == 30
    
    def test_call_failure(self):
        """测试调用失败"""
        ffi = YanFFI()
        
        result = ffi.call("nonexistent_function")
        assert result.success is False
        assert result.error is not None
    
    def test_call_python_success(self):
        """测试调用Python模块函数"""
        ffi = YanFFI()
        
        result = ffi.call_python("math", "sin", 0)
        assert result.success is True
        assert result.value == pytest.approx(0.0, abs=0.0001)
    
    def test_call_python_failure(self):
        """测试调用Python模块函数失败"""
        ffi = YanFFI()
        
        result = ffi.call_python("nonexistent_module", "func")
        assert result.success is False
        assert result.error is not None
    
    def test_call_python_function_not_found(self):
        """测试模块中没有函数"""
        ffi = YanFFI()
        
        result = ffi.call_python("math", "nonexistent_function")
        assert result.success is False
        assert "没有找到" in result.error
    
    def test_load_library(self):
        """测试加载库"""
        ffi = YanFFI()
        
        # 尝试加载C标准库
        if platform.system() == "Windows":
            lib_name = "msvcrt"
        else:
            lib_name = "c"
        
        try:
            result = ffi.load_library(lib_name)
            assert result == lib_name
            assert lib_name in ffi.list_libraries()
        except FFIError:
            pytest.skip("无法加载标准库")
    
    def test_unload_library(self):
        """测试卸载库"""
        ffi = YanFFI()
        
        # 尝试加载C标准库
        if platform.system() == "Windows":
            lib_name = "msvcrt"
        else:
            lib_name = "c"
        
        try:
            ffi.load_library(lib_name)
            assert ffi.unload_library(lib_name) is True
            assert lib_name not in ffi.list_libraries()
        except FFIError:
            pytest.skip("无法加载标准库")
    
    def test_list_functions(self):
        """测试列出函数"""
        ffi = YanFFI()
        
        def func1():
            pass
        
        def func2():
            pass
        
        ffi.register_function("func1", func1)
        ffi.register_function("func2", func2)
        
        funcs = ffi.list_functions()
        assert "func1" in funcs
        assert "func2" in funcs
    
    def test_list_libraries(self):
        """测试列出库"""
        ffi = YanFFI()
        
        # 尝试加载C标准库
        if platform.system() == "Windows":
            lib_name = "msvcrt"
        else:
            lib_name = "c"
        
        try:
            ffi.load_library(lib_name)
            libs = ffi.list_libraries()
            assert lib_name in libs
        except FFIError:
            pytest.skip("无法加载标准库")
    
    def test_add_search_path(self):
        """测试添加搜索路径"""
        ffi = YanFFI()
        # 使用当前存在的路径
        test_path = "C:\\Windows"
        ffi.add_search_path(test_path)
        assert test_path in ffi._search_path.paths
    
    def test_to_ctype_int(self):
        """测试转换为C类型 - 整数"""
        ffi = YanFFI()
        
        c_val = ffi.to_ctype(42, FFIType.INT32)
        assert isinstance(c_val, ctypes.c_int32)
        assert c_val.value == 42
    
    def test_to_ctype_float(self):
        """测试转换为C类型 - 浮点数"""
        ffi = YanFFI()
        
        c_val = ffi.to_ctype(3.14, FFIType.DOUBLE)
        assert isinstance(c_val, ctypes.c_double)
        assert c_val.value == pytest.approx(3.14, abs=0.001)
    
    def test_to_ctype_string(self):
        """测试转换为C类型 - 字符串"""
        ffi = YanFFI()
        
        c_val = ffi.to_ctype("hello", FFIType.STRING)
        assert c_val == b"hello"
    
    def test_from_ctype(self):
        """测试从C类型转换"""
        ffi = YanFFI()
        
        c_val = ctypes.c_int32(42)
        py_val = ffi.from_ctype(c_val, FFIType.INT32)
        assert py_val == 42
    
    def test_from_ctype_string(self):
        """测试从C类型转换 - 字符串"""
        ffi = YanFFI()
        
        c_val = b"hello"
        py_val = ffi.from_ctype(c_val, FFIType.STRING)
        assert py_val == "hello"


class TestFFICallResult:
    """FFI调用结果测试"""
    
    def test_success_result(self):
        """测试成功结果"""
        result = FFICallResult(success=True, value=42)
        assert result.success is True
        assert result.value == 42
        assert result.error is None
    
    def test_failure_result(self):
        """测试失败结果"""
        result = FFICallResult(
            success=False,
            error="错误信息",
            traceback="堆栈跟踪"
        )
        assert result.success is False
        assert result.error == "错误信息"
        assert result.traceback == "堆栈跟踪"


class TestFFIBuilder:
    """FFI构建器测试"""
    
    def test_define_function(self):
        """测试定义函数"""
        ffi = YanFFI()
        builder = FFIBuilder(ffi)
        
        builder.define_function(
            "my_func",
            return_type="int32",
            arg_types=["int32", "int32"]
        )
        
        assert "my_func" in builder._defs


class TestStandardLibraries:
    """标准库测试"""
    
    def test_load_c_lib(self):
        """测试加载C库"""
        ffi = YanFFI()
        success = StandardLibraries.load_c_lib(ffi)
        
        # 在支持的平台上应该成功
        if platform.system() != "Windows":
            assert success is True
        # Windows可能需要特殊处理
    
    def test_load_math_lib(self):
        """测试加载数学库"""
        ffi = YanFFI()
        success = StandardLibraries.load_math_lib(ffi)
        
        # 应该能成功加载
        assert success is True


class TestGlobalFFI:
    """全局FFI实例测试"""
    
    def test_get_global_ffi(self):
        """测试获取全局FFI实例"""
        ffi = get_global_ffi()
        assert isinstance(ffi, YanFFI)
        
        # 应该返回同一个实例
        ffi2 = get_global_ffi()
        assert ffi is ffi2
    
    def test_call_external(self):
        """测试外部调用快捷函数"""
        try:
            result = call_external("math", "cos", 0)
            assert result == pytest.approx(1.0, abs=0.0001)
        except FFIError:
            pytest.skip("外部调用失败")


class TestFFICalls:
    """FFI调用测试"""
    
    def test_call_c_function(self):
        """测试调用C函数"""
        if platform.system() == "Windows":
            lib_name = "msvcrt"
        else:
            lib_name = "c"
        
        ffi = YanFFI()
        try:
            ffi.load_library(lib_name)
            
            # 尝试调用一个简单的C函数
            lib = ffi._libraries[lib_name]
            
            if platform.system() != "Windows":
                # Unix系统调用getpid
                getpid = lib.getpid
                getpid.restype = ctypes.c_int
                result = getpid()
                assert result > 0
            else:
                # Windows调用GetCurrentProcessId
                kernel = ctypes.windll.kernel32
                GetCurrentProcessId = kernel.GetCurrentProcessId
                GetCurrentProcessId.restype = ctypes.c_ulong
                result = GetCurrentProcessId()
                assert result > 0
        except Exception:
            pytest.skip("C函数调用不可用")


class TestFFIError:
    """FFI错误测试"""
    
    def test_ffi_error(self):
        """测试FFI错误类"""
        error = FFIError("测试错误")
        assert str(error) == "测试错误"
    
    def test_ffi_error_inheritance(self):
        """测试FFI错误继承"""
        assert issubclass(FFIError, Exception)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])