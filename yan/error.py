"""
言语言错误处理模块
提供友好的错误信息，包括源代码片段和建议
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass

from error_formatter import ErrorFormatter, ErrorContext as FormattedErrorContext
from error_suggestions import ErrorSuggestionGenerator


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


class YanError(Exception):
    """言语言错误基类"""
    
    _formatter = ErrorFormatter(use_color=True)
    _suggester = ErrorSuggestionGenerator()
    
    def __init__(
        self,
        message: str,
        location: SourceLocation,
        source: Optional[str] = None,
        suggestion: Optional[str] = None,
        error_type: str = "错误"
    ):
        self.message = message
        self.location = location
        self.source = source
        self.suggestion = suggestion
        self.error_type = error_type
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """格式化错误信息"""
        source_lines = []
        if self.source:
            source_lines = self.source.split('\n')
        
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
            error_type="词法错误"
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
            error_type="语法错误"
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
            error_type="代码生成错误"
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
            error_type="运行时错误"
        )


# ============ 错误建议系统 ============

class ErrorSuggester:
    """错误建议生成器"""
    
    # 常见错误和建议
    COMMON_ERRORS = {
        # 拼写错误
        '定义': '定',
        '如果': '若',
        '那么': '则',
        '函数': '函',
        '打印': '印',
        '列表': '列',
        '字典': '典',
        
        # 常见语法错误
        '期望标识符': '请检查是否遗漏了变量名或函数名',
        '期望 \'=\'': '定义变量时需要使用等号，例如：定变量=值',
        '期望 \'则\'': '条件语句需要使用"则"关键字，例如：若条件则分支',
        '字符串未闭合': '字符串需要用双引号包裹，例如："hello"',
        '数学表达式未闭合': '数学表达式需要用 $() 包裹，例如：$(1+2)',
        'Python代码块未闭合': 'Python代码块需要用 {{}} 包裹，例如：{{x = 1}}',
        '期望变量名': '请提供有效的变量名',
        '期望结构体名称': '请提供结构体的名称',
        '期望 于': '遍历循环需要使用"于"关键字，例如：遍历x于列表：...',
        '期望 于': '遍历循环需要使用"于"关键字，例如：遍历x于列表：...',
    }
    
    # 相似动词建议
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
    
    # 拼写相似的汉字
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
        # 检查常见错误
        if error_message:
            for key, suggestion in cls.COMMON_ERRORS.items():
                if key in error_message:
                    return suggestion
        
        # 检查拼写错误
        if context:
            for wrong, correct in cls.COMMON_ERRORS.items():
                if wrong in context and wrong != correct:
                    return f'您是否想使用 "{correct}"？'
        
        # 检查相似动词
        if context:
            for verb, suggestions in cls.SIMILAR_VERBS.items():
                if verb in context:
                    similar_str = '、'.join(suggestions)
                    return f'相关动词：{similar_str}'
        
        # 检查未定义变量可能的拼写
        if context and '未定义' in error_message:
            # 尝试找到可能的正确拼写
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


# ============ 向后兼容的适配器 ============

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
