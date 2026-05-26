"""
言语言错误处理模块
提供友好的错误信息，包括源代码片段和建议
"""

from typing import Optional, List, Tuple, Set, Any, Dict
from dataclasses import dataclass, field
import warnings


@dataclass
class SourceLocation:
    """源代码位置"""
    line: int
    col: int
    filename: Optional[str] = None
    
    def __str__(self):
        if self.filename:
            return f"{self.filename}:{self.line}:{self.col}"
        return f"行{self.line}, 列{self.col}"


# =====================================
# 警告配置
# =====================================

@dataclass
class WarningConfig:
    """警告配置"""
    enable_warnings: bool = True  # 是否启用警告
    warn_as_error: bool = False   # 是否将警告当作错误
    warning_types: Set[str] = field(default_factory=lambda: {
        'unused_variable',
        'unused_import',
        'deprecated',
        'unreachable_code',
        'type_mismatch',
        'performance',
        'style',
    })  # 启用的警告类型
    
    def should_warn(self, warning_type: str) -> bool:
        """检查是否应该发出某种类型的警告"""
        if not self.enable_warnings:
            return False
        return warning_type in self.warning_types


# 全局警告配置
_global_warning_config = WarningConfig()


def set_warning_config(config: WarningConfig):
    """设置全局警告配置"""
    global _global_warning_config
    _global_warning_config = config


def get_warning_config() -> WarningConfig:
    """获取全局警告配置"""
    return _global_warning_config


# =====================================
# 警告类
# =====================================

class YanWarning(Warning):
    """言语言警告基类"""
    
    _formatter = None
    
    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None,
        suggestion: Optional[str] = None,
        warning_type: str = "警告",
        code: Optional[str] = None
    ):
        self.message = message
        self.location = location or SourceLocation(0, 0)
        self.source = source
        self.suggestion = suggestion
        self.warning_type = warning_type
        self.code = code
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """格式化警告信息"""
        parts = [f"警告: {self.message}"]
        if self.location:
            parts.append(f"位置: {self.location}")
        if self.suggestion:
            parts.append(f"建议: {self.suggestion}")
        if self.code:
            parts.append(f"代码: {self.code}")
        return "\n".join(parts)


class UnusedVariableWarning(YanWarning):
    """未使用变量警告"""
    
    def __init__(
        self,
        var_name: str,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message=f"未使用的变量: {var_name}",
            location=location,
            source=source,
            suggestion=f"请检查是否需要使用变量 '{var_name}'，或删除未使用的定义",
            warning_type="unused_variable",
            code="W101"
        )


class UnusedImportWarning(YanWarning):
    """未使用导入警告"""
    
    def __init__(
        self,
        import_name: str,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message=f"未使用的导入: {import_name}",
            location=location,
            source=source,
            suggestion=f"请检查是否需要导入 '{import_name}'，或移除该导入语句",
            warning_type="unused_import",
            code="W102"
        )


class DeprecatedWarning(YanWarning):
    """已弃用特性警告"""
    
    def __init__(
        self,
        feature: str,
        replacement: Optional[str] = None,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None
    ):
        message = f"已弃用的特性: {feature}"
        suggestion = "请考虑迁移到新的 API"
        if replacement:
            suggestion = f"请使用 '{replacement}' 替代"
        super().__init__(
            message=message,
            location=location,
            source=source,
            suggestion=suggestion,
            warning_type="deprecated",
            code="W201"
        )


class UnreachableCodeWarning(YanWarning):
    """不可达代码警告"""
    
    def __init__(
        self,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message="不可达代码",
            location=location,
            source=source,
            suggestion="请检查控制流逻辑，移除不可达的代码",
            warning_type="unreachable_code",
            code="W301"
        )


class TypeMismatchWarning(YanWarning):
    """类型不匹配警告"""
    
    def __init__(
        self,
        expected_type: str,
        actual_type: str,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message=f"类型不匹配: 期望 {expected_type}，得到 {actual_type}",
            location=location,
            source=source,
            suggestion="请检查类型转换或变量赋值",
            warning_type="type_mismatch",
            code="W401"
        )


class PerformanceWarning(YanWarning):
    """性能警告"""
    
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message=f"性能警告: {message}",
            location=location,
            source=source,
            suggestion=suggestion,
            warning_type="performance",
            code="W501"
        )


class StyleWarning(YanWarning):
    """代码风格警告"""
    
    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None
    ):
        super().__init__(
            message=f"风格警告: {message}",
            location=location,
            source=source,
            suggestion=suggestion,
            warning_type="style",
            code="W601"
        )


# =====================================
# 警告管理器
# =====================================

class WarningManager:
    """警告管理器"""
    
    def __init__(self):
        self.warnings: List[YanWarning] = []
        self.config = get_warning_config()
    
    def emit(self, warning: YanWarning):
        """发出警告"""
        # 检查配置是否启用该类型的警告
        if not self.config.should_warn(warning.warning_type):
            return
        
        self.warnings.append(warning)
        
        # 如果设置了 warn_as_error，抛出异常
        if self.config.warn_as_error:
            raise warning
        
        # 否则输出警告
        warnings.warn(warning)
    
    def emit_unused_variable(self, var_name: str, location: SourceLocation, source: str = None):
        """发出未使用变量警告"""
        self.emit(UnusedVariableWarning(var_name, location, source))
    
    def emit_unused_import(self, import_name: str, location: SourceLocation, source: str = None):
        """发出未使用导入警告"""
        self.emit(UnusedImportWarning(import_name, location, source))
    
    def emit_deprecated(self, feature: str, replacement: str = None, location: SourceLocation = None, source: str = None):
        """发出已弃用警告"""
        self.emit(DeprecatedWarning(feature, replacement, location, source))
    
    def emit_unreachable_code(self, location: SourceLocation = None, source: str = None):
        """发出不可达代码警告"""
        self.emit(UnreachableCodeWarning(location, source))
    
    def emit_type_mismatch(self, expected_type: str, actual_type: str, location: SourceLocation = None, source: str = None):
        """发出类型不匹配警告"""
        self.emit(TypeMismatchWarning(expected_type, actual_type, location, source))
    
    def emit_performance(self, message: str, suggestion: str = None, location: SourceLocation = None, source: str = None):
        """发出性能警告"""
        self.emit(PerformanceWarning(message, suggestion, location, source))
    
    def emit_style(self, message: str, suggestion: str = None, location: SourceLocation = None, source: str = None):
        """发出风格警告"""
        self.emit(StyleWarning(message, suggestion, location, source))
    
    def get_warnings(self) -> List[YanWarning]:
        """获取所有警告"""
        return self.warnings
    
    def has_warnings(self) -> bool:
        """检查是否有警告"""
        return len(self.warnings) > 0
    
    def clear(self):
        """清除所有警告"""
        self.warnings.clear()


# 全局警告管理器
_global_warning_manager = WarningManager()


def get_warning_manager() -> WarningManager:
    """获取全局警告管理器"""
    return _global_warning_manager


# =====================================
# 错误类
# =====================================

class YanError(Exception):
    """言语言错误基类"""
    
    _formatter = None
    _suggester = None
    
    def __init__(
        self,
        message: str,
        location: SourceLocation,
        source: Optional[str] = None,
        suggestion: Optional[str] = None,
        error_type: str = "错误",
        code: Optional[str] = None
    ):
        self.message = message
        self.location = location
        self.source = source
        self.suggestion = suggestion
        self.error_type = error_type
        self.code = code
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """格式化错误信息"""
        source_lines = []
        if self.source:
            source_lines = self.source.split('\n')
        
        if self._formatter:
            from error_formatter import ErrorFormatter, ErrorContext as FormattedErrorContext
            context = FormattedErrorContext(
                error_type=self.error_type,
                file_path=self.location.filename or "未知文件",
                line=self.location.line,
                column=self.location.col,
                end_column=self.location.col + 1,
                source_lines=source_lines,
                message=self.message,
                suggestion=self.suggestion
            )
            return self._formatter.format(context)
        else:
            parts = [f"{self.error_type}: {self.message}"]
            if self.location:
                parts.append(f"位置: {self.location}")
            if self.suggestion:
                parts.append(f"建议: {self.suggestion}")
            return "\n".join(parts)


class LexerError(YanError):
    """词法错误"""
    
    def __init__(
        self,
        message: str,
        location: SourceLocation,
        source: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(
            message=message,
            location=location,
            source=source,
            suggestion=suggestion,
            error_type="词法错误",
            code="E101"
        )


class ParserError(YanError):
    """语法错误"""
    
    def __init__(
        self,
        message: str,
        location: SourceLocation,
        source: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(
            message=message,
            location=location,
            source=source,
            suggestion=suggestion,
            error_type="语法错误",
            code="E201"
        )


class CodeGenError(YanError):
    """代码生成错误"""
    
    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        if location is None:
            location = SourceLocation(0, 0)
        super().__init__(
            message=message,
            location=location,
            source=source,
            suggestion=suggestion,
            error_type="代码生成错误",
            code="E301"
        )


class RuntimeError(YanError):
    """运行时错误"""
    
    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        source: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        if location is None:
            location = SourceLocation(0, 0)
        super().__init__(
            message=message,
            location=location,
            source=source,
            suggestion=suggestion,
            error_type="运行时错误",
            code="E401"
        )


# =====================================
# 错误恢复机制
# =====================================

class ErrorRecoveryStrategy:
    """错误恢复策略"""
    
    def __init__(
        self,
        max_errors: int = 10,
        skip_to_next_statement: bool = True,
        continue_after_error: bool = False
    ):
        self.max_errors = max_errors
        self.skip_to_next_statement = skip_to_next_statement
        self.continue_after_error = continue_after_error
        self.error_count = 0
        self.recovery_actions: List[Dict[str, Any]] = []
    
    def should_recover(self) -> bool:
        """检查是否应该尝试恢复"""
        if not self.continue_after_error:
            return False
        return self.error_count < self.max_errors
    
    def record_error(self, error: YanError):
        """记录错误"""
        self.error_count += 1
        self.recovery_actions.append({
            'type': 'error',
            'error': error,
            'action': 'continue' if self.should_recover() else 'stop'
        })
    
    def reset(self):
        """重置错误计数器"""
        self.error_count = 0
        self.recovery_actions.clear()
    
    def get_summary(self) -> str:
        """获取恢复摘要"""
        if self.error_count == 0:
            return "无错误"
        return f"共遇到 {self.error_count} 个错误，恢复 {len([a for a in self.recovery_actions if a['action'] == 'continue'])} 次"


# =====================================
# 错误建议系统
# =====================================

class ErrorSuggester:
    """错误建议生成器"""
    
    COMMON_ERRORS = {
        '定义': '定',
        '如果': '若',
        '那么': '则',
        '函数': '函',
        '打印': '印',
        '列表': '列',
        '字典': '典',
        
        '期望标识符': '请检查是否遗漏了变量名或函数名',
        '期望 \'=\'': '定义变量时需要使用等号，例如：定变量=值',
        '期望 \'则\'': '条件语句需要使用"则"关键字，例如：若条件则分支',
        '字符串未闭合': '字符串需要用双引号包裹，例如："hello"',
        '数学表达式未闭合': '数学表达式需要用 $() 包裹，例如：$(1+2)',
        'Python代码块未闭合': 'Python代码块需要用 {{}} 包裹，例如：{{x = 1}}',
        '期望变量名': '请提供有效的变量名',
        '期望结构体名称': '请提供结构体的名称',
        '期望 于': '遍历循环需要使用"于"关键字，例如：遍历x于列表：...',
    }
    
    SIMILAR_VERBS = {
        '加': ['减', '乘', '除'],
        '减': ['加', '乘', '除'],
        '乘': ['加', '减', '除'],
        '除': ['加', '减', '乘', '模'],
        '列': ['典', '序'],
        '典': ['列', '序'],
        '印': ['读', '写'],
        '若': ['遍历', '当'],
        '定': ['函'],
        '函': ['定'],
        '遍历': ['当', '若'],
        '当': ['遍历', '若'],
    }
    
    SIMILAR_CHARS = {
        '定': ['丁', '订', '盯'],
        '函': ['函', '涵', '寒'],
        '若': ['苦', '偌', '诺'],
        '则': ['侧', '测', '册'],
        '加': ['架', '茄', '贺'],
        '减': ['咸', '感', '碱'],
        '乘': ['剩', '乖', '乘'],
        '除': ['余', '途', '涂'],
        '列': ['烈', '裂', '冽'],
        '印': ['仰', '抑', '迎'],
    }
    
    @classmethod
    def suggest(cls, error_message: Optional[str] = None, context: Optional[str] = None) -> Optional[str]:
        """根据错误信息生成建议"""
        if error_message:
            for key, suggestion in cls.COMMON_ERRORS.items():
                if key in error_message:
                    return suggestion
        
        if context:
            for wrong, correct in cls.COMMON_ERRORS.items():
                if wrong in context and wrong != correct:
                    return f'您是否想使用 "{correct}"？'
        
        if context:
            for verb, suggestions in cls.SIMILAR_VERBS.items():
                if verb in context:
                    similar_str = '、'.join(suggestions)
                    return f'相关动词：{similar_str}'
        
        if context and '未定义' in error_message:
            for correct, wrong_list in cls.COMMON_ERRORS.items():
                if isinstance(wrong_list, list):
                    for wrong in wrong_list:
                        if wrong in context:
                            return f'您是否想使用 "{correct}"？'
        
        return None
    
    @classmethod
    def suggest_similar_verb(cls, verb: str) -> Optional[str]:
        """建议相似的动词"""
        if verb in cls.SIMILAR_VERBS:
            similar = cls.SIMILAR_VERBS[verb]
            return f'相关动词: {", ".join(similar)}'
        return None


# =====================================
# 向后兼容的适配器
# =====================================

def create_lexer_error(message: str, line: int, col: int, source: Optional[str] = None) -> LexerError:
    """创建词法错误（向后兼容）"""
    location = SourceLocation(line, col)
    suggestion = ErrorSuggester.suggest(message)
    return LexerError(message, location, source, suggestion)


def create_parser_error(message: str, line: int, col: int, source: Optional[str] = None) -> ParserError:
    """创建语法错误（向后兼容）"""
    location = SourceLocation(line, col)
    suggestion = ErrorSuggester.suggest(message)
    return ParserError(message, location, source, suggestion)