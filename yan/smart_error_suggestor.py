"""
智能错误建议系统（增强版）
基于上下文分析提供精准的错误修复建议
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from error import YanError, SourceLocation


@dataclass
class ErrorPattern:
    """错误模式定义"""
    pattern: str  # 正则表达式或关键词
    pattern_type: str = "keyword"  # 'keyword', 'regex', 'exact'
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 0.8
    requires_context: bool = False


@dataclass
class Suggestion:
    """建议对象"""
    text: str
    confidence: float
    type: str = "suggestion"  # 'suggestion', 'fix', 'reference', 'example'
    code_fix: Optional[str] = None
    reference_url: Optional[str] = None
    example_code: Optional[str] = None


class SmartErrorSuggestor:
    """智能错误建议生成器"""
    
    # 错误模式库
    ERROR_PATTERNS: List[ErrorPattern] = [
        # 词法错误模式
        ErrorPattern(
            pattern="无效字符",
            suggestions=[
                "请检查是否输入了非法字符或特殊符号",
                "确保使用的是中文全角符号，如：，。；：""''",
                "英文符号需要使用半角形式，如：, . ; : \"\" ''"
            ]
        ),
        ErrorPattern(
            pattern="字符串未闭合",
            suggestions=[
                "字符串需要用双引号包裹，例如：\"你好\"",
                "检查是否缺少闭合的引号",
                "确保字符串中的引号正确转义"
            ]
        ),
        ErrorPattern(
            pattern="未定义的标识符",
            suggestions=[
                "请检查变量名或函数名是否拼写正确",
                "确保在使用前已经定义了该变量或函数",
                "检查是否遗漏了必要的导入语句"
            ]
        ),
        # 语法错误模式
        ErrorPattern(
            pattern="期望 '则'",
            suggestions=[
                "条件语句需要使用\"则\"或\"那么\"关键字，例如：如果 条件 则 ...",
                "检查\"如果\"语句后面是否缺少\"则\"或\"那么\"",
                "正确语法：如果 条件 则 代码块",
                "正确语法：如果 条件 那么 代码块"
            ]
        ),
        ErrorPattern(
            pattern="期望 '于'",
            suggestions=[
                "遍历循环需要使用\"于\"关键字，例如：遍历 x 于 列表",
                "检查\"遍历\"关键字后面是否缺少\"于\"",
                "正确语法：遍历 变量 于 集合"
            ]
        ),
        ErrorPattern(
            pattern="期望 '的'",
            suggestions=[
                "检查是否缺少\"的\"关键字",
                "在结构体访问时需要使用\"的\"，例如：对象的属性"
            ]
        ),
        ErrorPattern(
            pattern="表达式未闭合",
            suggestions=[
                "数学表达式需要用 $() 包裹，例如：$(1 + 2)",
                "检查括号是否配对完整",
                "确保所有开括号都有对应的闭括号"
            ]
        ),
        ErrorPattern(
            pattern="代码块未闭合",
            suggestions=[
                "代码块需要用 {{}} 包裹，例如：{{ x = 1 }}",
                "检查是否缺少闭合的花括号",
                "确保代码块正确嵌套"
            ]
        ),
        # 运行时错误模式
        ErrorPattern(
            pattern="参数数量错误",
            suggestions=[
                "请检查函数调用的参数数量",
                "确保提供了正确数量的参数",
                "参考函数定义确认参数要求"
            ]
        ),
        ErrorPattern(
            pattern="类型错误",
            suggestions=[
                "请检查操作数的类型是否正确",
                "确保类型匹配，如：数字不能与字符串相加",
                "考虑使用类型转换函数"
            ]
        ),
        ErrorPattern(
            pattern="索引越界",
            suggestions=[
                "检查索引值是否在有效范围内",
                "列表索引从0开始，有效范围是0到长度减1",
                "使用长度函数检查列表长度"
            ]
        ),
        ErrorPattern(
            pattern="除以零",
            suggestions=[
                "请检查除法运算的除数是否可能为零",
                "在除法前添加条件检查",
                "使用条件语句避免除以零的情况"
            ]
        ),
        ErrorPattern(
            pattern="文件未找到",
            suggestions=[
                "检查文件路径是否正确",
                "确保文件存在于指定位置",
                "使用绝对路径或相对路径时要注意工作目录"
            ]
        ),
    ]
    
    # 常见拼写错误映射
    SPELLING_CORRECTIONS: Dict[str, str] = {
        '定议': '定义',
        '定仪': '定义',
        '义定': '定义',
        '函说': '函数',
        '函素': '函数',
        '列抱': '列表',
        '列标': '列表',
        '字点': '字典',
        '字点': '字典',
        '如裹': '如果',
        '如锅': '如果',
        '那末': '那么',
        '哪么': '那么',
        '遍力': '遍历',
        '变历': '遍历',
        '当是': '当时',
        '当实': '当时',
        '印出': '输出',
        '印入': '输出',
        '加如': '加入',
        '加如': '加入',
        '取的': '取出',
        '取的': '取出',
        '为真': '真',
        '为假': '假',
        '真的': '真',
        '假的': '假',
    }
    
    # 关键词相似性映射
    KEYWORD_SIMILARITY: Dict[str, List[str]] = {
        '定义': ['函', '设定', '声明'],
        '函数': ['定义', '方法', '过程'],
        '列表': ['字典', '序列', '数组'],
        '字典': ['列表', '映射', '对象'],
        '如果': ['当', '假设', '若'],
        '遍历': ['当', '循环', '迭代'],
        '当': ['遍历', '如果', '每当'],
        '输出': ['打印', '显示', '写入'],
        '加入': ['添加', '插入', '追加'],
        '取出': ['获取', '得到', '读取'],
        '真': ['是', '正确', '成立'],
        '假': ['否', '错误', '不成立'],
    }
    
    def __init__(self):
        self.context_collector = None
    
    def set_context_collector(self, collector):
        """设置上下文收集器"""
        self.context_collector = collector
    
    def suggest(self, error: YanError) -> List[Suggestion]:
        """生成错误建议"""
        suggestions = []
        
        # 1. 基于错误模式匹配的建议
        pattern_suggestions = self._match_patterns(error.message)
        suggestions.extend(pattern_suggestions)
        
        # 2. 基于拼写修正的建议
        spelling_suggestions = self._check_spelling(error)
        suggestions.extend(spelling_suggestions)
        
        # 3. 基于上下文的建议
        context_suggestions = self._analyze_context(error)
        suggestions.extend(context_suggestions)
        
        # 4. 相似名称建议（如果有上下文）
        if self.context_collector:
            name_suggestions = self._suggest_similar_names(error)
            suggestions.extend(name_suggestions)
        
        # 按置信度排序
        suggestions.sort(key=lambda s: s.confidence, reverse=True)
        
        return suggestions
    
    def _match_patterns(self, message: str) -> List[Suggestion]:
        """匹配错误模式"""
        suggestions = []
        
        for pattern in self.ERROR_PATTERNS:
            if pattern.pattern_type == "keyword":
                if pattern.pattern in message:
                    for text in pattern.suggestions:
                        suggestions.append(Suggestion(
                            text=text,
                            confidence=pattern.confidence,
                            type="suggestion"
                        ))
            elif pattern.pattern_type == "regex":
                import re
                if re.search(pattern.pattern, message):
                    for text in pattern.suggestions:
                        suggestions.append(Suggestion(
                            text=text,
                            confidence=pattern.confidence,
                            type="suggestion"
                        ))
        
        return suggestions
    
    def _check_spelling(self, error: YanError) -> List[Suggestion]:
        """检查拼写错误"""
        suggestions = []
        
        message = error.message
        source = error.source or ""
        
        # 检查错误消息中的拼写错误
        for wrong, correct in self.SPELLING_CORRECTIONS.items():
            if wrong in message or wrong in source:
                suggestions.append(Suggestion(
                    text=f'您是否想输入 "{correct}" 而不是 "{wrong}"？',
                    confidence=0.9,
                    type="fix"
                ))
        
        return suggestions
    
    def _analyze_context(self, error: YanError) -> List[Suggestion]:
        """分析上下文提供建议"""
        suggestions = []
        
        # 如果有源代码，分析附近的代码
        if error.source:
            lines = error.source.split('\n')
            if error.location.line > 0 and error.location.line <= len(lines):
                line_content = lines[error.location.line - 1]
                
                # 检查常见的语法问题
                if '如果' in line_content and '则' not in line_content:
                    suggestions.append(Suggestion(
                        text='条件语句中"如果"后面缺少"则"关键字',
                        confidence=0.85,
                        type="fix",
                        example_code="如果 条件 则 代码块"
                    ))
                
                if '遍历' in line_content and '于' not in line_content:
                    suggestions.append(Suggestion(
                        text='遍历循环中"遍历"后面缺少"于"关键字',
                        confidence=0.85,
                        type="fix",
                        example_code="遍历 x 于 列表：..."
                    ))
        
        return suggestions
    
    def _suggest_similar_names(self, error: YanError) -> List[Suggestion]:
        """建议相似的名称"""
        suggestions = []
        
        if not self.context_collector:
            return suggestions
        
        # 获取当前作用域中的符号
        context = self.context_collector.get_context_for_error(error)
        nearby_symbols = context.get('nearby_symbols', [])
        symbol_names = [sym['name'] for sym in nearby_symbols]
        
        # 分析错误消息中的名称
        message = error.message
        
        # 尝试找到可能拼错的名称
        for wrong, correct in self.SPELLING_CORRECTIONS.items():
            if wrong in message:
                if correct in symbol_names:
                    suggestions.append(Suggestion(
                        text=f'您是否想使用已定义的符号 "{correct}"？',
                        confidence=0.9,
                        type="fix"
                    ))
        
        # 检查关键词相似性
        for keyword, similar in self.KEYWORD_SIMILARITY.items():
            if keyword in message:
                suggestions.append(Suggestion(
                    text=f'相关关键词：{", ".join(similar)}',
                    confidence=0.7,
                    type="reference"
                ))
        
        return suggestions
    
    def generate_code_fix(self, error: YanError) -> Optional[str]:
        """生成代码修复建议"""
        message = error.message
        
        if "期望 '则'" in message:
            return "在 '如果' 语句后添加 '则' 或 '那么' 关键字"
        
        if "期望 '于'" in message:
            return "在 '遍历' 关键字后添加 '于' 关键字"
        
        if "字符串未闭合" in message:
            return "添加闭合的双引号"
        
        if "表达式未闭合" in message:
            return "使用 $() 包裹数学表达式"
        
        return None


# 全局智能建议器
_global_smart_suggestor = SmartErrorSuggestor()


def get_smart_suggestor() -> SmartErrorSuggestor:
    """获取全局智能建议器"""
    return _global_smart_suggestor


def suggest_for_error(error: YanError) -> List[Suggestion]:
    """为错误生成建议"""
    return _global_smart_suggestor.suggest(error)
