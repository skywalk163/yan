"""
言语言沙箱执行环境
"""

import sys
import os
import io
import traceback
from typing import Dict, Any, Optional, Tuple


class SandboxError(Exception):
    """沙箱执行错误"""
    pass


class Sandbox:
    """沙箱执行环境"""
    
    def __init__(self, 
                 allow_file_access: bool = False,
                 allow_network_access: bool = False,
                 allow_subprocess: bool = False,
                 max_execution_time: int = 30,
                 max_memory_mb: int = 256,
                 stdout_limit: int = 1024 * 1024,  # 1MB
                 stderr_limit: int = 1024 * 1024   # 1MB
                 ):
        """
        初始化沙箱环境
        
        Args:
            allow_file_access: 是否允许文件系统访问
            allow_network_access: 是否允许网络访问
            allow_subprocess: 是否允许启动子进程
            max_execution_time: 最大执行时间（秒）
            max_memory_mb: 最大内存使用（MB）
            stdout_limit: 标准输出限制（字节）
            stderr_limit: 标准错误限制（字节）
        """
        self.allow_file_access = allow_file_access
        self.allow_network_access = allow_network_access
        self.allow_subprocess = allow_subprocess
        self.max_execution_time = max_execution_time
        self.max_memory_mb = max_memory_mb
        self.stdout_limit = stdout_limit
        self.stderr_limit = stderr_limit
        
        # 保存原始模块引用
        self._original_open = open
        self._original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__
        
        # 限制的模块列表
        self._blocked_modules = {
            'os', 'subprocess', 'sys', 'socket', 'urllib', 'requests',
            'http', 'ftplib', 'smtplib', 'email', 'pickle', 'marshal',
            'ctypes', 'cffi', 'multiprocessing', 'threading', 'asyncio'
        }
    
    def _restrict_open(self, *args, **kwargs):
        """限制文件访问"""
        if not self.allow_file_access:
            raise SandboxError("文件访问被禁止")
        return self._original_open(*args, **kwargs)
    
    def _restrict_import(self, name, *args, **kwargs):
        """限制模块导入"""
        module_name = name.split('.')[0]
        if module_name in self._blocked_modules:
            if module_name == 'sys':
                # 允许有限的 sys 访问
                import sys as sys_module
                return sys_module
            raise SandboxError(f"禁止导入模块: {name}")
        return self._original_import(name, *args, **kwargs)
    
    def _capture_output(self, func, *args, **kwargs):
        """捕获标准输出和标准错误"""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        
        try:
            result = func(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        stdout_output = stdout_buffer.getvalue()
        stderr_output = stderr_buffer.getvalue()
        
        # 限制输出大小
        if len(stdout_output) > self.stdout_limit:
            stdout_output = stdout_output[:self.stdout_limit] + "... [输出已截断]"
        if len(stderr_output) > self.stderr_limit:
            stderr_output = stderr_output[:self.stderr_limit] + "... [输出已截断]"
        
        return result, stdout_output, stderr_output
    
    def _setup_environment(self) -> Dict[str, Any]:
        """设置沙箱执行环境"""
        env = {
            '__builtins__': __builtins__,
            '__name__': '__sandbox__',
            '__doc__': None,
            '__package__': None,
            '__loader__': None,
            '__spec__': None,
        }
        
        # 添加安全的内置函数
        safe_builtins = {}
        for name in dir(__builtins__):
            if name not in {'open', '__import__', 'eval', 'exec'}:
                safe_builtins[name] = getattr(__builtins__, name)
        
        env['__builtins__'] = safe_builtins
        env['open'] = self._restrict_open
        env['__import__'] = self._restrict_import
        
        return env
    
    def execute(self, code: str, globals_dict: Optional[Dict[str, Any]] = None) -> Tuple[Any, str, str, Optional[str]]:
        """
        在沙箱中执行代码
        
        Args:
            code: 要执行的代码
            globals_dict: 额外的全局变量
        
        Returns:
            (返回值, 标准输出, 标准错误, 错误信息)
        """
        env = self._setup_environment()
        
        if globals_dict:
            env.update(globals_dict)
        
        try:
            result, stdout, stderr = self._capture_output(exec, code, env, env)
            return result, stdout, stderr, None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            traceback_str = traceback.format_exc()
            return None, "", traceback_str, error_msg
    
    def evaluate(self, expression: str, globals_dict: Optional[Dict[str, Any]] = None) -> Tuple[Any, str, str, Optional[str]]:
        """
        在沙箱中求值表达式
        
        Args:
            expression: 要求值的表达式
            globals_dict: 额外的全局变量
        
        Returns:
            (返回值, 标准输出, 标准错误, 错误信息)
        """
        env = self._setup_environment()
        
        if globals_dict:
            env.update(globals_dict)
        
        try:
            result, stdout, stderr = self._capture_output(eval, expression, env)
            return result, stdout, stderr, None
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            traceback_str = traceback.format_exc()
            return None, "", traceback_str, error_msg


class YanSandbox(Sandbox):
    """言语言专用沙箱"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def execute_yan_code(self, yan_code: str) -> Tuple[Any, str, str, Optional[str]]:
        """
        在沙箱中执行言语言代码
        
        Args:
            yan_code: 言语言代码
        
        Returns:
            (返回值, 标准输出, 标准错误, 错误信息)
        """
        from lexer import Lexer
        from parser import Parser
        from codegen import PythonCodeGen
        from runtime import ALL_BUILTINS
        
        try:
            # 分词
            lexer = Lexer()
            tokens = lexer.tokenize(yan_code)
            
            # 解析
            parser = Parser()
            ast = parser.parse(tokens)
            
            # 生成 Python 代码
            codegen = PythonCodeGen()
            python_code = codegen.generate(ast)
            
            # 准备运行时环境
            runtime_env = {}
            for name, (func, arity) in ALL_BUILTINS.items():
                runtime_env[name] = func
                # 使用函数的实际名称（代码生成器使用 __name__）
                func_name = func.__name__ if hasattr(func, '__name__') else name
                runtime_env[func_name] = func
            
            # 在沙箱中执行
            return self.execute(python_code, runtime_env)
            
        except Exception as e:
            error_msg = f"编译错误: {type(e).__name__}: {str(e)}"
            traceback_str = traceback.format_exc()
            return None, "", traceback_str, error_msg


# 便捷函数
def safe_exec(code: str, **kwargs) -> Tuple[Any, str, str, Optional[str]]:
    """安全执行代码的便捷函数"""
    sandbox = Sandbox(**kwargs)
    return sandbox.execute(code)


def safe_eval(expression: str, **kwargs) -> Tuple[Any, str, str, Optional[str]]:
    """安全求值表达式的便捷函数"""
    sandbox = Sandbox(**kwargs)
    return sandbox.evaluate(expression)


def safe_yan_exec(yan_code: str, **kwargs) -> Tuple[Any, str, str, Optional[str]]:
    """安全执行言语言代码的便捷函数"""
    sandbox = YanSandbox(**kwargs)
    return sandbox.execute_yan_code(yan_code)