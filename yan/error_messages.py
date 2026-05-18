#!/usr/bin/env python3
"""
言语言错误消息模板库

提供参数化的错误消息和修复建议模板
"""

from typing import Dict, List, Optional, Callable
from error_types import ErrorType


class ErrorMessageTemplate:
    """错误消息模板"""
    
    def __init__(
        self,
        code: str,
        template: str,
        suggestions: List[str],
        examples: Optional[List[str]] = None,
        see_also: Optional[List[str]] = None
    ):
        self.code = code
        self.template = template
        self.suggestions = suggestions
        self.examples = examples or []
        self.see_also = see_also or []
    
    def format(self, **kwargs) -> tuple[str, List[str]]:
        """格式化错误消息
        
        Args:
            **kwargs: 模板参数
        
        Returns:
            (错误消息, 建议列表)
        """
        try:
            message = self.template.format(**kwargs)
        except KeyError as e:
            message = f"{self.template} (缺少参数: {e})"
        
        # 格式化建议
        formatted_suggestions = []
        for suggestion in self.suggestions:
            try:
                formatted_suggestions.append(suggestion.format(**kwargs))
            except KeyError:
                formatted_suggestions.append(suggestion)
        
        return message, formatted_suggestions


class ErrorMessageLibrary:
    """错误消息库"""
    
    def __init__(self):
        self._templates: Dict[str, ErrorMessageTemplate] = {}
        self._init_templates()
    
    def _init_templates(self):
        """初始化错误消息模板"""
        
        # 词法错误 (E1xx)
        self._templates["E101"] = ErrorMessageTemplate(
            code="E101",
            template="词法错误：{message}",
            suggestions=[
                "检查源代码是否有非法字符",
                "确保使用正确的中文标点符号"
            ]
        )
        
        self._templates["E102"] = ErrorMessageTemplate(
            code="E102",
            template="非法字符 '{character}' 在第 {line} 行",
            suggestions=[
                "检查是否使用了非法的ASCII字符",
                "言语言使用中文标点：。 ， 、 ； ：？！"
            ],
            examples=["错误: 使用英文句号. 应使用中文句号。"]
        )
        
        self._templates["E103"] = ErrorMessageTemplate(
            code="E103",
            template="字符串未闭合：缺少结束引号",
            suggestions=[
                "检查字符串是否使用配对的中文引号「」或「」",
                "确保每个开始引号都有对应的结束引号",
                "检查字符串中是否有未转义的引号"
            ],
            examples=[
                "错误: 「你好世界",
                "正确: 「你好世界」"
            ]
        )
        
        self._templates["E104"] = ErrorMessageTemplate(
            code="E104",
            template="无效的数字格式：{value}",
            suggestions=[
                "检查数字格式是否正确",
                "数字可以包含小数点，如 3.14",
                "可以使用科学计数法，如 1e10"
            ]
        )
        
        # 语法错误 (E2xx)
        self._templates["E201"] = ErrorMessageTemplate(
            code="E201",
            template="语法错误：{message}",
            suggestions=[
                "检查语法结构是否正确",
                "参考言语言语法文档"
            ]
        )
        
        self._templates["E202"] = ErrorMessageTemplate(
            code="E202",
            template="缺少 {expected}，在第 {line} 行第 {column} 列",
            suggestions=[
                "在指定位置添加 {expected}",
                "检查前面的表达式是否完整"
            ]
        )
        
        self._templates["E203"] = ErrorMessageTemplate(
            code="E203",
            template="意外的 token：{token}",
            suggestions=[
                "移除意外的 token",
                "检查表达式是否正确闭合"
            ]
        )
        
        self._templates["E205"] = ErrorMessageTemplate(
            code="E205",
            template="代码块未正确闭合",
            suggestions=[
                "确保每个 代码块 都有对应的 结束标记",
                "使用「。」结束函数定义",
                "使用「。」结束语句"
            ],
            examples=[
                "错误: 定 函数 = 函 x 加x x",
                "正确: 定 函数 = 函 x 加x x。"
            ]
        )
        
        # 语义错误 (E3xx)
        self._templates["E301"] = ErrorMessageTemplate(
            code="E301",
            template="类型错误：期望 {expected}，实际得到 {actual}",
            suggestions=[
                "检查变量的类型是否正确",
                "确保操作符两边的类型兼容"
            ]
        )
        
        self._templates["E302"] = ErrorMessageTemplate(
            code="E302",
            template="未定义的变量：{name}",
            suggestions=[
                "检查变量名是否拼写正确",
                "确保变量在使用前已定义"
            ],
            see_also=["E303"]
        )
        
        self._templates["E303"] = ErrorMessageTemplate(
            code="E303",
            template="未定义的函数：{name}",
            suggestions=[
                "检查函数名是否拼写正确",
                "确保函数在使用前已定义",
                "如果是标准库函数，检查是否已导入"
            ],
            see_also=["E302"]
        )
        
        self._templates["E304"] = ErrorMessageTemplate(
            code="E304",
            template="重复定义：{name} 已被定义",
            suggestions=[
                "使用不同的名称",
                "如果要重新定义，先删除旧的定义"
            ]
        )
        
        self._templates["E305"] = ErrorMessageTemplate(
            code="E305",
            template="参数类型错误：函数 {function} 期望 {expected}，但得到 {actual}",
            suggestions=[
                "检查传递给函数的参数类型",
                "查看函数定义了解期望的参数类型"
            ]
        )
        
        self._templates["E306"] = ErrorMessageTemplate(
            code="E306",
            template="参数数量错误：函数 {function} 期望 {expected} 个参数，但得到 {actual} 个",
            suggestions=[
                "检查函数调用时的参数数量",
                "使用 归 或 皆 等高阶函数处理不定数量参数"
            ]
        )
        
        # 运行时错误 (E4xx)
        self._templates["E401"] = ErrorMessageTemplate(
            code="E401",
            template="运行时错误：{message}",
            suggestions=[
                "检查代码逻辑是否正确",
                "添加适当的错误处理"
            ]
        )
        
        self._templates["E402"] = ErrorMessageTemplate(
            code="E402",
            template="除数为零",
            suggestions=[
                "检查除法运算，确保除数不为零",
                "添加除数检查：若 除数等0 则 ...
            ]
        )
        
        self._templates["E403"] = ErrorMessageTemplate(
            code="E403",
            template="索引越界：列表长度为 {length}，但访问了索引 {index}",
            suggestions=[
                "检查索引是否在有效范围内 (0 到 length-1)",
                "使用 首 和 余 函数安全访问列表"
            ]
        )
        
        self._templates["E404"] = ErrorMessageTemplate(
            code="E404",
            template="键不存在：{key}",
            suggestions=[
                "检查字典中是否存在该键",
                "使用 含 键 检查键是否存在"
            ]
        )
        
        self._templates["E405"] = ErrorMessageTemplate(
            code="E405",
            template="类型不匹配：无法对 {type1} 和 {type2} 执行 {operation}",
            suggestions=[
                "确保操作符两边的类型兼容",
                "必要时进行类型转换"
            ]
        )
        
        self._templates["E406"] = ErrorMessageTemplate(
            code="E406",
            template="递归深度超过限制",
            suggestions=[
                "检查递归函数是否有正确的终止条件",
                "考虑使用迭代代替递归"
            ]
        )
        
        # 模块错误 (E5xx)
        self._templates["E501"] = ErrorMessageTemplate(
            code="E501",
            template="模块错误：{message}",
            suggestions=[
                "检查模块是否存在",
                "确保模块路径正确"
            ]
        )
        
        self._templates["E502"] = ErrorMessageTemplate(
            code="E502",
            template="找不到模块：{module}",
            suggestions=[
                "检查模块名称是否正确",
                "确保模块文件存在",
                "检查模块搜索路径"
            ]
        )
        
        self._templates["E503"] = ErrorMessageTemplate(
            code="E503",
            template="循环依赖检测：{module1} 和 {module2} 相互依赖",
            suggestions=[
                "重构模块，消除循环依赖",
                "将共享代码提取到独立模块"
            ]
        )
        
        # 代码生成错误 (E6xx)
        self._templates["E601"] = ErrorMessageTemplate(
            code="E601",
            template="代码生成错误：{message}",
            suggestions=[
                "检查语法是否正确",
                "简化复杂表达式"
            ]
        )
        
        self._templates["E603"] = ErrorMessageTemplate(
            code="E603",
            template="不支持的特性：{feature}",
            suggestions=[
                "该特性尚未实现",
                "使用替代方案实现相同功能"
            ]
        )
    
    def get_template(self, code: str) -> Optional[ErrorMessageTemplate]:
        """获取错误消息模板
        
        Args:
            code: 错误代码 (如 "E201")
        
        Returns:
            错误消息模板，如果不存在返回 None
        """
        return self._templates.get(code)
    
    def format_error(self, code: str, **kwargs) -> tuple[str, List[str]]:
        """格式化错误消息
        
        Args:
            code: 错误代码
            **kwargs: 模板参数
        
        Returns:
            (错误消息, 建议列表)
        """
        template = self.get_template(code)
        if template:
            return template.format(**kwargs)
        
        # 默认消息
        return f"错误 {code}", ["请查阅文档了解更多信息"]
    
    def add_custom_template(self, template: ErrorMessageTemplate):
        """添加自定义模板
        
        Args:
            template: 错误消息模板
        """
        self._templates[template.code] = template
    
    def get_all_codes(self) -> List[str]:
        """获取所有错误代码"""
        return list(self._templates.keys())


# 全局实例
_error_message_library: Optional[ErrorMessageLibrary] = None


def get_error_library() -> ErrorMessageLibrary:
    """获取错误消息库实例"""
    global _error_message_library
    if _error_message_library is None:
        _error_message_library = ErrorMessageLibrary()
    return _error_message_library


def format_error(code: str, **kwargs) -> tuple[str, List[str]]:
    """格式化错误的便捷函数
    
    Args:
        code: 错误代码
        **kwargs: 模板参数
    
    Returns:
        (错误消息, 建议列表)
    """
    return get_error_library().format_error(code, **kwargs)
