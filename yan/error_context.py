#!/usr/bin/env python3
"""
言语言错误上下文提取器

提供错误上下文信息，包括代码片段、高亮、变量状态等
"""

from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class ErrorContext:
    """错误上下文"""
    source: str
    error_line: int
    error_column: int
    context_lines: List[Tuple[int, str]]  # (行号, 代码)
    highlight_start: int
    highlight_end: int
    before_line: str
    error_line_text: str
    after_line: str
    variables: Dict[str, Any]
    
    def get_formatted_context(self, max_line_len: int = 80) -> str:
        """格式化错误上下文"""
        lines = []
        
        # 添加上下文行
        for line_num, line_text in self.context_lines:
            prefix = "→ " if line_num == self.error_line else "  "
            lines.append(f"{prefix}{line_num:4d} │ {line_text}")
        
        # 添加高亮
        if self.context_lines:
            highlight_line = "    │ " + " " * self.error_column + "^" * max(1, self.highlight_end - self.highlight_start)
            lines.append(highlight_line)
        
        return "\n".join(lines)


class ErrorContextExtractor:
    """错误上下文提取器"""
    
    def __init__(self, context_lines: int = 3):
        self.context_lines = context_lines
    
    def extract(
        self,
        source: str,
        error_line: int,
        error_column: int = 0,
        variables: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """提取错误上下文
        
        Args:
            source: 源代码
            error_line: 错误行号（从1开始）
            error_column: 错误列号（从0开始）
            variables: 当前的变量状态
        
        Returns:
            ErrorContext 对象
        """
        lines = source.split('\n')
        
        # 计算上下文范围
        start = max(0, error_line - self.context_lines - 1)
        end = min(len(lines), error_line + self.context_lines)
        
        # 获取上下文行
        context = []
        for i in range(start, end):
            context.append((i + 1, lines[i]))
        
        # 获取错误行及其前后行
        before_line = lines[error_line - 2] if error_line > 1 else ""
        error_line_text = lines[error_line - 1] if error_line <= len(lines) else ""
        after_line = lines[error_line] if error_line < len(lines) else ""
        
        # 计算高亮范围
        highlight_start = error_column
        highlight_end = min(error_column + 1, len(error_line_text))
        
        return ErrorContext(
            source=source,
            error_line=error_line,
            error_column=error_column,
            context_lines=context,
            highlight_start=highlight_start,
            highlight_end=highlight_end,
            before_line=before_line,
            error_line_text=error_line_text,
            after_line=after_line,
            variables=variables or {}
        )
    
    def extract_from_exception(
        self,
        source: str,
        exc: Exception,
        variables: Optional[Dict[str, Any]] = None
    ) -> Optional[ErrorContext]:
        """从异常中提取错误上下文
        
        支持从以下异常中提取位置信息：
        - SyntaxError
        - 自定义 YanError
        """
        import traceback
        
        # 尝试从异常消息中提取行号
        error_line = 1
        error_column = 0
        
        # 从 traceback 中查找行号
        tb_lines = traceback.format_exc().split('\n')
        for line in tb_lines:
            if 'line' in line.lower():
                # 尝试提取行号
                import re
                match = re.search(r'line\s+(\d+)', line)
                if match:
                    error_line = int(match.group(1))
                    break
        
        # 如果是 SyntaxError
        if isinstance(exc, SyntaxError):
            if exc.lineno is not None:
                error_line = exc.lineno
            if exc.offset is not None:
                error_column = exc.offset - 1
        
        return self.extract(source, error_line, error_column, variables)


class VariableInspector:
    """变量检查器，用于获取错误发生时的变量状态"""
    
    def __init__(self):
        self.frame = None
    
    def capture_locals(self, frame) -> Dict[str, Any]:
        """捕获局部变量
        
        Args:
            frame: 栈帧对象
        
        Returns:
            局部变量字典
        """
        self.frame = frame
        
        # 获取局部变量
        local_vars = {}
        
        # 从 frame 获取
        if frame:
            # 过滤内置变量
            for key, value in frame.f_locals.items():
                if not key.startswith('__') and not callable(value):
                    try:
                        # 避免repr()触发异常
                        local_vars[key] = value
                    except:
                        local_vars[key] = f"<{type(value).__name__}>"
        
        return local_vars
    
    def format_variables(self, variables: Dict[str, Any], max_length: int = 50) -> str:
        """格式化变量信息
        
        Args:
            variables: 变量字典
            max_length: 最大显示长度
        
        Returns:
            格式化后的字符串
        """
        if not variables:
            return "(无局部变量)"
        
        parts = []
        for name, value in variables.items():
            # 截断过长的值
            value_str = repr(value)
            if len(value_str) > max_length:
                value_str = value_str[:max_length - 3] + "..."
            
            # 处理特殊类型
            if isinstance(value, list):
                value_str = f"列{value_str[1:-1]}" if len(value) <= 5 else f"列[{len(value)}项]"
            elif isinstance(value, dict):
                value_str = f"典{value_str[1:-1]}" if len(value) <= 5 else f"典{{{len(value)}键}}"
            
            parts.append(f"{name} = {value_str}")
        
        return ", ".join(parts)


def format_error_with_context(
    source: str,
    error_line: int,
    error_column: int,
    error_message: str,
    error_code: str,
    variables: Optional[Dict[str, Any]] = None
) -> str:
    """格式化带上下文的错误信息
    
    Args:
        source: 源代码
        error_line: 错误行号
        error_column: 错误列号
        error_message: 错误消息
        error_code: 错误代码
        variables: 变量状态
    
    Returns:
        格式化的错误信息
    """
    extractor = ErrorContextExtractor()
    context = extractor.extract(source, error_line, error_column, variables)
    
    lines = []
    
    # 错误头部
    lines.append(f"╔══════════════════════════════════════════════════════════════╗")
    lines.append(f"║ [{error_code}] 错误")
    lines.append(f"╚══════════════════════════════════════════════════════════════╝")
    
    # 位置信息
    lines.append(f"\n📍 位置：第 {error_line} 行，第 {error_column + 1} 列")
    
    # 错误消息
    lines.append(f"\n❌ {error_message}")
    
    # 代码上下文
    lines.append(f"\n📄 代码上下文：")
    lines.append("┌────────────────────────────────────────────────────────────┐")
    
    for line_num, line_text in context.context_lines:
        prefix = "→" if line_num == error_line else " "
        lines.append(f"│ {prefix} {line_num:4d} │ {line_text}")
    
    lines.append("│" + " " * 5 + "│" + " " * (context.error_column + 1) + "^")
    lines.append("└────────────────────────────────────────────────────────────┘")
    
    # 变量状态
    if variables:
        inspector = VariableInspector()
        var_str = inspector.format_variables(variables)
        lines.append(f"\n📋 局部变量：{var_str}")
    
    return "\n".join(lines)
