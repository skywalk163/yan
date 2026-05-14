"""
言语言错误处理模块
提供友好的错误信息，包括源代码片段和建议
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass


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
        lines = []
        
        # 错误标题
        lines.append(f"{self.error_type}: {self.message}")
        lines.append(f"  位置: {self.location}")
        
        # 源代码片段
        if self.source:
            snippet = self._get_source_snippet()
            if snippet:
                lines.append("")
                lines.append(snippet)
        
        # 建议
        if self.suggestion:
            lines.append("")
            lines.append(f"  提示: {self.suggestion}")
        
        return '\n'.join(lines)
    
    def _get_source_snippet(self) -> str:
        """获取源代码片段，带高亮"""
        if not self.source:
            return ""
        
        source_lines = self.source.split('\n')
        if self.location.line <= 0 or self.location.line > len(source_lines):
            return ""
        
        # 获取错误行
        error_line = source_lines[self.location.line - 1]
        
        # 构建片段（显示前后各 2 行）
        start_line = max(1, self.location.line - 2)
        end_line = min(len(source_lines), self.location.line + 2)
        
        lines = []
        for i in range(start_line, end_line + 1):
            line_content = source_lines[i - 1]
            prefix = "  > " if i == self.location.line else "    "
            lines.append(f"{prefix}{i:4d} | {line_content}")
            
            # 在错误行下方显示指示符
            if i == self.location.line:
                indent = len(prefix) + 7  # 前缀 + 行号 + " | "
                pointer = ' ' * (self.location.col - 1) + '^' + '~' * (len(error_line) - self.location.col)
                lines.append(' ' * indent + pointer)
        
        return '\n'.join(lines)


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
        'Python 代码块未闭合': 'Python 代码块需要用 {{}} 包裹，例如：{{x = 1}}',
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
    }
    
    @classmethod
    def suggest(cls, error_message: str, context: Optional[str] = None) -> Optional[str]:
        """根据错误信息生成建议"""
        # 检查常见错误
        for key, suggestion in cls.COMMON_ERRORS.items():
            if key in error_message:
                return suggestion
        
        # 检查拼写错误
        if context:
            for wrong, correct in cls.COMMON_ERRORS.items():
                if wrong in context and wrong != correct:
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
