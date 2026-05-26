"""
言语言外部函数接口（FFI）模块
支持调用 Python 函数、C 函数和动态库
"""

import ctypes
import ctypes.util
import sys
import os
import platform
import json
import importlib
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import traceback


class FFIType(Enum):
    """FFI类型"""
    VOID = "void"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    FLOAT = "float"
    DOUBLE = "double"
    CHAR = "char"
    STRING = "string"
    BOOL = "bool"
    POINTER = "pointer"
    FUNCTION = "function"
    ARRAY = "array"
    STRUCT = "struct"


@dataclass
class FFITypeInfo:
    """FFI类型信息"""
    ffi_type: FFIType
    c_type: str
    python_type: type
    size: int = 0
    alignment: int = 0


# 类型映射表
FFI_TYPE_MAP: Dict[str, FFITypeInfo] = {
    "void": FFITypeInfo(FFIType.VOID, "void", None, 0, 0),
    "int8": FFITypeInfo(FFIType.INT8, "int8_t", ctypes.c_int8, 1, 1),
    "int16": FFITypeInfo(FFIType.INT16, "int16_t", ctypes.c_int16, 2, 2),
    "int32": FFITypeInfo(FFIType.INT32, "int32_t", ctypes.c_int32, 4, 4),
    "int64": FFITypeInfo(FFIType.INT64, "int64_t", ctypes.c_int64, 8, 8),
    "uint8": FFITypeInfo(FFIType.UINT8, "uint8_t", ctypes.c_uint8, 1, 1),
    "uint16": FFITypeInfo(FFIType.UINT16, "uint16_t", ctypes.c_uint16, 2, 2),
    "uint32": FFITypeInfo(FFIType.UINT32, "uint32_t", ctypes.c_uint32, 4, 4),
    "uint64": FFITypeInfo(FFIType.UINT64, "uint64_t", ctypes.c_uint64, 8, 8),
    "float": FFITypeInfo(FFIType.FLOAT, "float", ctypes.c_float, 4, 4),
    "double": FFITypeInfo(FFIType.DOUBLE, "double", ctypes.c_double, 8, 8),
    "char": FFITypeInfo(FFIType.CHAR, "char", ctypes.c_char, 1, 1),
    "bool": FFITypeInfo(FFIType.BOOL, "bool", ctypes.c_bool, 1, 1),
    "pointer": FFITypeInfo(FFIType.POINTER, "void*", ctypes.c_void_p, 8, 8),
}


@dataclass
class FunctionSignature:
    """函数签名"""
    name: str
    return_type: FFIType
    arg_types: List[FFIType]
    calling_convention: str = "cdecl"
    library: Optional[str] = None


@dataclass
class FFIFunction:
    """FFI函数封装"""
    name: str
    func: Callable
    signature: FunctionSignature
    doc: str = ""


@dataclass
class FFICallResult:
    """FFI调用结果"""
    success: bool
    value: Any = None
    error: Optional[str] = None
    traceback: Optional[str] = None


class DLLSearchPath:
    """动态库搜索路径"""
    
    def __init__(self):
        self.paths: List[str] = []
        self._init_default_paths()
    
    def _init_default_paths(self):
        """初始化默认搜索路径"""
        # 系统默认路径
        if platform.system() == "Windows":
            self.paths.extend([
                os.environ.get("PATH", ""),
                os.environ.get("SYSTEMROOT", "") + "\\System32",
                os.environ.get("PROGRAMFILES", ""),
                os.environ.get("LOCALAPPDATA", ""),
            ])
        elif platform.system() == "Darwin":
            self.paths.extend([
                "/usr/lib",
                "/usr/local/lib",
                "/Library/Frameworks",
                os.path.expanduser("~/lib"),
            ])
        else:
            self.paths.extend([
                "/usr/lib",
                "/usr/local/lib",
                "/usr/lib64",
                "/usr/local/lib64",
            ])
    
    def add_path(self, path: str):
        """添加搜索路径"""
        if path and os.path.isdir(path):
            self.paths.append(path)
    
    def find_library(self, name: str) -> Optional[str]:
        """查找动态库"""
        # 尝试直接加载
        if os.path.exists(name):
            return name
        
        # 添加平台特定前缀和后缀
        prefixes = ["", "lib"]
        if platform.system() == "Windows":
            suffixes = [".dll", ".dll.a", ".lib"]
        elif platform.system() == "Darwin":
            suffixes = [".dylib", ".so", ".a"]
        else:
            suffixes = [".so", ".so.1", ".a"]
        
        for prefix in prefixes:
            for suffix in suffixes:
                lib_name = prefix + name + suffix
                
                # 尝试 ctypes.util.find_library
                found = ctypes.util.find_library(name)
                if found:
                    return found
                
                # 尝试搜索路径
                for path in self.paths:
                    if os.path.isdir(path):
                        lib_path = os.path.join(path, lib_name)
                        if os.path.exists(lib_path):
                            return lib_path
        
        return None


class CFunction:
    """C函数封装"""
    
    def __init__(self, func, restype, argtypes):
        self.func = func
        self.restype = restype
        self.argtypes = argtypes
    
    def __call__(self, *args) -> Any:
        """调用C函数"""
        try:
            return self.func(*args)
        except Exception as e:
            raise FFIError(f"C函数调用失败: {e}")


class FFIError(Exception):
    """FFI错误"""
    pass


class YanFFI:
    """言语言FFI主类"""
    
    def __init__(self):
        self._libraries: Dict[str, ctypes.CDLL] = {}
        self._functions: Dict[str, FFIFunction] = {}
        self._python_functions: Dict[str, Callable] = {}
        self._search_path = DLLSearchPath()
        self._type_converters: Dict[str, Callable] = {}
        self._setup_type_converters()
    
    def _setup_type_converters(self):
        """设置类型转换器"""
        # Python类型到FFI类型的转换
        self._type_converters = {
            int: lambda x: FFIType.INT64,
            float: lambda x: FFIType.DOUBLE,
            str: lambda x: FFIType.STRING,
            bool: lambda x: FFIType.BOOL,
            bytes: lambda x: FFIType.ARRAY,
            list: lambda x: FFIType.ARRAY,
            dict: lambda x: FFIType.STRUCT,
            type(None): lambda x: FFIType.VOID,
        }
    
    def load_library(self, name: str, path: Optional[str] = None) -> str:
        """加载动态库"""
        if name in self._libraries:
            return name
        
        lib_path = path or self._search_path.find_library(name)
        
        if not lib_path or not os.path.exists(lib_path):
            raise FFIError(f"找不到动态库: {name}")
        
        try:
            lib = ctypes.CDLL(lib_path)
            self._libraries[name] = lib
            return name
        except Exception as e:
            raise FFIError(f"加载动态库失败: {lib_path}: {e}")
    
    def unload_library(self, name: str) -> bool:
        """卸载动态库"""
        if name in self._libraries:
            del self._libraries[name]
            return True
        return False
    
    def register_function(
        self,
        name: str,
        func: Callable,
        return_type: FFIType = FFIType.VOID,
        arg_types: List[FFIType] = None,
        doc: str = ""
    ):
        """注册函数"""
        signature = FunctionSignature(
            name=name,
            return_type=return_type,
            arg_types=arg_types or []
        )
        
        ffi_func = FFIFunction(
            name=name,
            func=func,
            signature=signature,
            doc=doc
        )
        
        self._functions[name] = ffi_func
    
    def register_c_function(
        self,
        library: str,
        name: str,
        return_type: FFIType = FFIType.INT32,
        arg_types: List[FFIType] = None
    ) -> CFunction:
        """注册C函数"""
        if library not in self._libraries:
            self.load_library(library)
        
        lib = self._libraries[library]
        
        # 获取C函数
        if not hasattr(lib, name):
            raise FFIError(f"动态库 {library} 中没有找到函数: {name}")
        
        c_func = getattr(lib, name)
        
        # 设置返回类型
        restype = self._get_ctype(return_type)
        c_func.restype = restype
        
        # 设置参数类型
        argtypes = []
        for arg_type in (arg_types or []):
            argtypes.append(self._get_ctype(arg_type))
        c_func.argtypes = argtypes
        
        # 创建封装
        wrapped = CFunction(c_func, restype, argtypes)
        
        # 注册
        self.register_function(
            name=name,
            func=wrapped,
            return_type=return_type,
            arg_types=arg_types
        )
        
        return wrapped
    
    def _get_ctype(self, ffi_type: FFIType):
        """获取ctypes类型"""
        type_info = FFI_TYPE_MAP.get(ffi_type.value)
        if type_info:
            return type_info.python_type
        return ctypes.c_void_p
    
    def call(self, name: str, *args, **kwargs) -> FFICallResult:
        """调用FFI函数"""
        if name not in self._functions:
            return FFICallResult(
                success=False,
                error=f"未注册的函数: {name}"
            )
        
        try:
            func = self._functions[name].func
            result = func(*args, **kwargs)
            return FFICallResult(success=True, value=result)
        except Exception as e:
            return FFICallResult(
                success=False,
                error=str(e),
                traceback=traceback.format_exc()
            )
    
    def call_python(self, module: str, func_name: str, *args, **kwargs) -> FFICallResult:
        """调用Python模块中的函数"""
        try:
            # 导入模块
            mod = importlib.import_module(module)
            
            # 获取函数
            if not hasattr(mod, func_name):
                return FFICallResult(
                    success=False,
                    error=f"模块 {module} 中没有找到函数: {func_name}"
                )
            
            func = getattr(mod, func_name)
            
            # 调用函数
            result = func(*args, **kwargs)
            return FFICallResult(success=True, value=result)
        except Exception as e:
            return FFICallResult(
                success=False,
                error=str(e),
                traceback=traceback.format_exc()
            )
    
    def call_c(self, library: str, func_name: str, *args) -> FFICallResult:
        """调用C函数"""
        try:
            if library not in self._libraries:
                self.load_library(library)
            
            lib = self._libraries[library]
            
            if not hasattr(lib, func_name):
                return FFICallResult(
                    success=False,
                    error=f"动态库 {library} 中没有找到函数: {func_name}"
                )
            
            c_func = getattr(lib, func_name)
            result = c_func(*args)
            
            return FFICallResult(success=True, value=result)
        except Exception as e:
            return FFICallResult(
                success=False,
                error=str(e),
                traceback=traceback.format_exc()
            )
    
    def get_function(self, name: str) -> Optional[FFIFunction]:
        """获取注册的函数"""
        return self._functions.get(name)
    
    def list_functions(self) -> List[str]:
        """列出所有注册的函数"""
        return list(self._functions.keys())
    
    def list_libraries(self) -> List[str]:
        """列出已加载的库"""
        return list(self._libraries.keys())
    
    def add_search_path(self, path: str):
        """添加动态库搜索路径"""
        self._search_path.add_path(path)
    
    def to_ctype(self, value: Any, target_type: FFIType) -> Any:
        """Python值转换为C类型"""
        if target_type == FFIType.INT8:
            return ctypes.c_int8(value)
        elif target_type == FFIType.INT16:
            return ctypes.c_int16(value)
        elif target_type == FFIType.INT32:
            return ctypes.c_int32(value)
        elif target_type == FFIType.INT64:
            return ctypes.c_int64(value)
        elif target_type == FFIType.UINT8:
            return ctypes.c_uint8(value)
        elif target_type == FFIType.UINT16:
            return ctypes.c_uint16(value)
        elif target_type == FFIType.UINT32:
            return ctypes.c_uint32(value)
        elif target_type == FFIType.UINT64:
            return ctypes.c_uint64(value)
        elif target_type == FFIType.FLOAT:
            return ctypes.c_float(value)
        elif target_type == FFIType.DOUBLE:
            return ctypes.c_double(value)
        elif target_type == FFIType.BOOL:
            return ctypes.c_bool(value)
        elif target_type == FFIType.STRING:
            return value.encode('utf-8') if isinstance(value, str) else value
        else:
            return value
    
    def from_ctype(self, value: Any, source_type: FFIType) -> Any:
        """C类型转换为Python值"""
        if value is None:
            return None
        
        if source_type == FFIType.STRING:
            return value.decode('utf-8') if isinstance(value, bytes) else value
        
        if hasattr(value, 'value'):
            return value.value
        
        return value


class FFIBuilder:
    """FFI构建器，用于简化FFI函数定义"""
    
    def __init__(self, ffi: YanFFI):
        self.ffi = ffi
        self._defs: Dict[str, Dict] = {}
    
    def define_function(
        self,
        name: str,
        return_type: str = "int32",
        arg_types: List[str] = None
    ):
        """定义函数"""
        self._defs[name] = {
            "return_type": return_type,
            "arg_types": arg_types or []
        }
        return self
    
    def link(self, library: str):
        """链接到库"""
        for name, def_info in self._defs.items():
            return_type = FFIType(def_info["return_type"])
            arg_types = [FFIType(t) for t in def_info["arg_types"]]
            
            self.ffi.register_c_function(
                library=library,
                name=name,
                return_type=return_type,
                arg_types=arg_types
            )
        return self
    
    def python_function(self, name: str, func: Callable):
        """注册Python函数"""
        self.ffi.register_function(name, func)
        return self


# 常用C库预定义
class StandardLibraries:
    """标准库链接"""
    
    @staticmethod
    def load_c_lib(ffi: YanFFI) -> bool:
        """加载C标准库"""
        try:
            if platform.system() == "Windows":
                # Windows上的C标准库
                ffi.load_library("msvcrt")
                ffi.load_library("ucrtbase")
            else:
                # Unix上的C标准库
                ffi.load_library("c")
            return True
        except FFIError:
            return False
    
    @staticmethod
    def load_math_lib(ffi: YanFFI) -> bool:
        """加载数学库"""
        try:
            if platform.system() == "Windows":
                ffi.load_library("msvcrt")
            else:
                ffi.load_library("m")
            return True
        except FFIError:
            return False
    
    @staticmethod
    def load_pthread_lib(ffi: YanFFI) -> bool:
        """加载POSIX线程库"""
        try:
            if platform.system() == "Windows":
                return False
            else:
                ffi.load_library("pthread")
            return True
        except FFIError:
            return False


# 全局FFI实例
_global_ffi: Optional[YanFFI] = None


def get_global_ffi() -> YanFFI:
    """获取全局FFI实例"""
    global _global_ffi
    if _global_ffi is None:
        _global_ffi = YanFFI()
    return _global_ffi


def call_external(module: str, func: str, *args, **kwargs) -> Any:
    """调用外部Python函数（快捷函数）"""
    ffi = get_global_ffi()
    result = ffi.call_python(module, func, *args, **kwargs)
    if result.success:
        return result.value
    else:
        raise FFIError(result.error or "调用失败")


def load_c_library(name: str, path: Optional[str] = None) -> str:
    """加载C库（快捷函数）"""
    ffi = get_global_ffi()
    return ffi.load_library(name, path)


def call_c_function(library: str, func: str, *args) -> Any:
    """调用C函数（快捷函数）"""
    ffi = get_global_ffi()
    result = ffi.call_c(library, func, *args)
    if result.success:
        return result.value
    else:
        raise FFIError(result.error or "调用失败")


# 示例使用
if __name__ == "__main__":
    ffi = YanFFI()
    
    # 注册Python函数
    def my_add(a, b):
        return a + b
    
    ffi.register_function("my_add", my_add, FFIType.INT64, [FFIType.INT64, FFIType.INT64])
    
    # 调用注册的函数
    result = ffi.call("my_add", 10, 20)
    print(f"my_add(10, 20) = {result.value}")
    
    # 加载C标准库
    if StandardLibraries.load_c_lib(ffi):
        print("C标准库加载成功")
        print(f"已加载的库: {ffi.list_libraries()}")
    
    # 调用Python标准库
    result = ffi.call_python("math", "sin", 0)
    print(f"math.sin(0) = {result.value}")
    
    # 调用Python标准库（使用快捷函数）
    try:
        result = call_external("time", "time")
        print(f"time.time() = {result}")
    except FFIError as e:
        print(f"调用失败: {e}")
    
    print(f"注册的函数: {ffi.list_functions()}")