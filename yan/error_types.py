#!/usr/bin/env python3
"""
言语言错误类型定义

提供统一的错误分类、严重级别和错误代码系统
"""

from enum import Enum
from typing import Optional, List, Dict, Any


class ErrorType(Enum):
    """错误类型枚举"""
    # 词法错误 (E1xx)
    LEXER_ERROR = "E101"
    INVALID_CHARACTER = "E102"
    UNCLOSED_STRING = "E103"
    INVALID_NUMBER = "E104"
    UNEXPECTED_TOKEN = "E105"
    
    # 语法错误 (E2xx)
    SYNTAX_ERROR = "E201"
    MISSING_TOKEN = "E202"
    UNEXPECTED_TOKEN_SYNTAX = "E203"
    INVALID_EXPRESSION = "E204"
    UNCLOSED_BLOCK = "E205"
    INVALID_STATEMENT = "E206"
    
    # 语义错误 (E3xx)
    TYPE_ERROR = "E301"
    UNDEFINED_VARIABLE = "E302"
    UNDEFINED_FUNCTION = "E303"
    DUPLICATE_DEFINITION = "E304"
    INVALID_ARGUMENT_TYPE = "E305"
    WRONG_ARGUMENT_COUNT = "E306"
    
    # 运行时错误 (E4xx)
    RUNTIME_ERROR = "E401"
    DIVISION_BY_ZERO = "E402"
    INDEX_OUT_OF_BOUNDS = "E403"
    KEY_NOT_FOUND = "E404"
    TYPE_MISMATCH = "E405"
    RECURSION_DEPTH = "E406"
    STACK_OVERFLOW = "E407"
    
    # 模块错误 (E5xx)
    MODULE_ERROR = "E501"
    MODULE_NOT_FOUND = "E502"
    CIRCULAR_DEPENDENCY = "E503"
    IMPORT_ERROR = "E504"
    EXPORT_ERROR = "E505"
    
    # 代码生成错误 (E6xx)
    CODEGEN_ERROR = "E601"
    INVALID_AST = "E602"
    UNSUPPORTED_FEATURE = "E603"
    
    # 未知错误
    UNKNOWN_ERROR = "E999"


class ErrorSeverity(Enum):
    """错误严重级别"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class YanError(Exception):
    """言语言错误基类"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN_ERROR,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source_file: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.severity = severity
        self.line = line
        self.column = column
        self.source_file = source_file
        self.context = context or {}
        self.suggestions = suggestions or []
        self.original_error = original_error
    
    def get_error_code(self) -> str:
        """获取错误代码"""
        return self.error_type.value
    
    def get_location(self) -> str:
        """获取错误位置"""
        parts = []
        if self.source_file:
            parts.append(self.source_file)
        if self.line is not None:
            parts.append(f"第{self.line}行")
        if self.column is not None:
            parts.append(f"第{self.column}列")
        return "，".join(parts) if parts else "未知位置"
    
    def add_suggestion(self, suggestion: str):
        """添加建议"""
        if suggestion not in self.suggestions:
            self.suggestions.append(suggestion)
    
    def __str__(self) -> str:
        parts = [
            f"[{self.get_error_code()}]",
            f"{self.message}"
        ]
        
        location = self.get_location()
        if location != "未知位置":
            parts.insert(1, f"位置：{location}")
        
        if self.suggestions:
            parts.append("\n可能的解决方案：")
            for i, suggestion in enumerate(self.suggestions, 1):
                parts.append(f"  {i}. {suggestion}")
        
        return "\n".join(parts)


class LexerError(YanError):
    """词法错误"""
    
    def __init__(self, message: str, line: int = None, column: int = None, **kwargs):
        super().__init__(
            message,
            error_type=ErrorType.LEXER_ERROR,
            line=line,
            column=column,
            **kwargs
        )


class ParserError(YanError):
    """语法错误"""
    
    def __init__(self, message: str, line: int = None, column: int = None, **kwargs):
        super().__init__(
            message,
            error_type=ErrorType.SYNTAX_ERROR,
            line=line,
            column=column,
            **kwargs
        )


class TypeError(YanError):
    """类型错误"""
    
    def __init__(self, message: str, line: int = None, column: int = None, **kwargs):
        super().__init__(
            message,
            error_type=ErrorType.TYPE_ERROR,
            line=line,
            column=column,
            **kwargs
        )


class NameError(YanError):
    """名称错误（变量/函数未定义）"""
    
    def __init__(self, message: str, line: int = None, column: int = None, **kwargs):
        super().__init__(
            message,
            error_type=ErrorType.UNDEFINED_VARIABLE,
            line=line,
            column=column,
            **kwargs
        )


class RuntimeError(YanError):
    """运行时错误"""
    
    def __init__(self, message: str, line: int = None, column: int = None, **kwargs):
        super().__init__(
            message,
            error_type=ErrorType.RUNTIME_ERROR,
            line=line,
            column=column,
            **kwargs
        )


class ModuleError(YanError):
    """模块错误"""
    
    def __init__(self, message: str, line: int = None, column: int = None, **kwargs):
        super().__init__(
            message,
            error_type=ErrorType.MODULE_ERROR,
            line=line,
            column=column,
            **kwargs
        )


class CodeGenError(YanError):
    """代码生成错误"""
    
    def __init__(self, message: str, line: int = None, column: int = None, **kwargs):
        super().__init__(
            message,
            error_type=ErrorType.CODEGEN_ERROR,
            line=line,
            column=column,
            **kwargs
        )


def create_error(
    error_type: ErrorType,
    message: str,
    **kwargs
) -> YanError:
    """错误工厂函数"""
    error_classes = {
        ErrorType.LEXER_ERROR: LexerError,
        ErrorType.INVALID_CHARACTER: LexerError,
        ErrorType.UNCLOSED_STRING: LexerError,
        ErrorType.INVALID_NUMBER: LexerError,
        ErrorType.SYNTAX_ERROR: ParserError,
        ErrorType.MISSING_TOKEN: ParserError,
        ErrorType.TYPE_ERROR: TypeError,
        ErrorType.UNDEFINED_VARIABLE: NameError,
        ErrorType.UNDEFINED_FUNCTION: NameError,
        ErrorType.RUNTIME_ERROR: RuntimeError,
        ErrorType.DIVISION_BY_ZERO: RuntimeError,
        ErrorType.MODULE_ERROR: ModuleError,
        ErrorType.MODULE_NOT_FOUND: ModuleError,
        ErrorType.CIRCULAR_DEPENDENCY: ModuleError,
        ErrorType.CODEGEN_ERROR: CodeGenError,
    }
    
    error_class = error_classes.get(error_type, YanError)
    return error_class(message, **kwargs)
