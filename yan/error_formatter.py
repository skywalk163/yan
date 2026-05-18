"""
言语言错误格式化器
提供清晰、友好、可操作的错误信息
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ErrorContext:
    """错误上下文信息"""
    error_type: str
    file_path: str
    line: int
    column: int
    end_column: int
    source_lines: List[str]
    message: str
    suggestion: Optional[str] = None
    similar_names: Optional[List[str]] = None
    
    @property
    def width(self) -> int:
        """错误标记宽度"""
        return self.end_column - self.column


class ErrorFormatter:
    """错误格式化器"""
    
    COLORS = {
        'red': '\033[91m',
        'yellow': '\033[93m',
        'cyan': '\033[96m',
        'gray': '\033[90m',
        'bold': '\033[1m',
        'underline': '\033[4m',
        'reset': '\033[0m'
    }
    
    def __init__(self, use_color: bool = True):
        self.use_color = use_color
    
    def format(self, context: ErrorContext) -> str:
        """格式化错误信息"""
        lines = []
        
        lines.append(self._format_header(context))
        lines.append(self._format_location(context))
        lines.append("")
        lines.extend(self._format_source_snippet(context))
        lines.append(self._format_message(context))
        
        if context.suggestion:
            lines.append("")
            lines.append(self._format_suggestion(context))
        
        return "\n".join(lines)
    
    def _format_header(self, context: ErrorContext) -> str:
        """格式化错误标题"""
        if self.use_color:
            return f"{self.COLORS['bold']}{self.COLORS['red']}错误：{context.error_type}{self.COLORS['reset']}"
        else:
            return f"错误：{context.error_type}"
    
    def _format_location(self, context: ErrorContext) -> str:
        """格式化位置信息"""
        return f"  文件：{context.file_path}\n  位置：第 {context.line} 行，第 {context.column}-{context.end_column} 列"
    
    def _format_source_snippet(self, context: ErrorContext) -> List[str]:
        """格式化源代码片段"""
        lines = []
        
        start_line = max(1, context.line - 1)
        end_line = min(len(context.source_lines), context.line + 1)
        
        line_num_width = len(str(end_line))
        
        for i in range(start_line - 1, end_line):
            line_num = i + 1
            source_line = context.source_lines[i]
            
            if self.use_color:
                line_num_str = f"{self.COLORS['gray']}第 {line_num} 行{self.COLORS['reset']}"
            else:
                line_num_str = f"第 {line_num} 行"
            
            if line_num == context.line:
                if self.use_color:
                    lines.append(f"  {line_num_str} | {self.COLORS['bold']}{source_line}{self.COLORS['reset']}")
                else:
                    lines.append(f"  {line_num_str} | {source_line}")
            else:
                lines.append(f"  {line_num_str} | {source_line}")
        
        error_marker = self._format_error_marker(context)
        lines.append(error_marker)
        
        return lines
    
    def _format_error_marker(self, context: ErrorContext) -> str:
        """格式化错误位置标记"""
        line_num_width = len(str(min(len(context.source_lines), context.line + 1)))
        indent = " " * (line_num_width + 4)
        
        underline = " " * (context.column - 1) + "^" * max(1, context.width)
        
        if self.use_color:
            error_desc = f"{self.COLORS['red']}{context.message}{self.COLORS['reset']}"
        else:
            error_desc = context.message
        
        return f"{indent}{underline}\n{indent}  {error_desc}"
    
    def _format_message(self, context: ErrorContext) -> str:
        """格式化错误消息"""
        if context.similar_names:
            similar = "、".join(context.similar_names)
            return f"您是否想使用：{similar}？"
        return ""
    
    def _format_suggestion(self, context: ErrorContext) -> str:
        """格式化修复建议"""
        if self.use_color:
            return f"{self.COLORS['cyan']}建议：{context.suggestion}{self.COLORS['reset']}"
        else:
            return f"建议：{context.suggestion}"
