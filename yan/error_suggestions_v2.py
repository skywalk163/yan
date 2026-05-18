#!/usr/bin/env python3
"""
言语言智能建议引擎 V2

提供基于上下文的智能错误修复建议
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
import re


@dataclass
class Suggestion:
    """建议项"""
    text: str
    confidence: float  # 0.0 - 1.0
    category: str  # "spelling", "syntax", "type", "fix"
    auto_fix: Optional[str] = None


class ErrorPatternMatcher:
    """错误模式匹配器"""
    
    # 常见错误模式及其建议
    PATTERNS = {
        # 拼写错误
        (r'^未定义的变量[：:]\s*(\w+)$', 'undefined_variable'): [
            (r'变|名|量', 'variable', 0.3),
            (r'函数|函', 'function', 0.3),
        ],
        
        # 语法错误
        (r'^缺少\s*[""''「」]?$', 'missing_quote'): [
            ('添加配对的引号', 0.9),
        ],
        
        # 类型错误
        (r'^类型错误', 'type_error'): [
            ('检查变量类型', 0.7),
            ('使用类型转换', 0.6),
        ],
    }
    
    @classmethod
    def match(cls, error_message: str) -> List[Suggestion]:
        """匹配错误模式"""
        suggestions = []
        
        for pattern, suggestions_list in cls.PATTERNS.items():
            if isinstance(pattern[0], str):
                # 简单字符串匹配
                if pattern[0] in error_message:
                    for item in suggestions_list:
                        if isinstance(item, tuple) and len(item) == 2:
                            suggestions.append(Suggestion(
                                text=item[0],
                                confidence=item[1],
                                category='pattern'
                            ))
        
        return suggestions


class SpellingCorrector:
    """拼写纠错器"""
    
    # 言语言关键字和常用词
    KEYWORDS = {
        # 控制流
        '若': 'if/when', '则': 'then', '否则': 'else',
        '遍历': 'for/each', '当': 'while', '循环': 'loop',
        
        # 定义
        '定': 'define/let', '函': 'function',
        '类': 'class', '构': 'struct',
        
        # 布尔
        '真': 'true', '假': 'false', '空': 'null/none',
        
        # 运算
        '加': 'add', '减': 'sub', '乘': 'mul', '除': 'div',
        '等': 'eq', '不等': 'neq', '大': 'gt', '小': 'lt',
        '且': 'and', '或': 'or', '非': 'not',
        
        # 列表
        '列': 'list', '典': 'dict', '首': 'head', '余': 'tail',
        '长': 'length', '含': 'contains',
        
        # 高阶函数
        '皆': 'map', '只': 'filter', '归': 'reduce',
        
        # I/O
        '印': 'print', '读': 'read', '写': 'write',
        '引': 'import', '出': 'export',
    }
    
    # 用户可能打错的常用词
    COMMON_WORDS = [
        '加', '减', '乘', '除', '印', '读', '写',
        '引', '出', '函', '定', '列', '典',
        '首', '余', '长', '含', '皆', '只', '归',
        '若', '则', '否则', '遍历', '当', '真', '假',
        '等', '不等', '大', '小', '且', '或', '非'
    ]
    
    @classmethod
    def get_similar(cls, word: str, max_suggestions: int = 3) -> List[Tuple[str, float]]:
        """获取相似词
        
        Args:
            word: 输入的词
            max_suggestions: 最大建议数
        
        Returns:
            [(相似词, 相似度), ...]
        """
        similarities = []
        
        for candidate in cls.COMMON_WORDS:
            ratio = SequenceMatcher(None, word, candidate).ratio()
            if ratio > 0.5:  # 相似度阈值
                similarities.append((candidate, ratio))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:max_suggestions]
    
    @classmethod
    def suggest_correction(cls, undefined_name: str) -> List[Suggestion]:
        """建议拼写纠错
        
        Args:
            undefined_name: 未定义的名称
        
        Returns:
            建议列表
        """
        suggestions = []
        similar = cls.get_similar(undefined_name)
        
        for similar_word, confidence in similar:
            explanations = cls.KEYWORDS.get(similar_word, '')
            suggestions.append(Suggestion(
                text=f"是否想输入「{similar_word}」？{explanations}",
                confidence=confidence,
                category='spelling',
                auto_fix=similar_word
            ))
        
        return suggestions


class SmartSuggestionEngine:
    """智能建议引擎"""
    
    def __init__(self):
        self.pattern_matcher = ErrorPatternMatcher()
        self.spelling_corrector = SpellingCorrector()
        self._known_variables: List[str] = []
        self._known_functions: List[str] = []
    
    def set_known_names(self, variables: List[str], functions: List[str]):
        """设置已知的变量和函数名"""
        self._known_variables = variables
        self._known_functions = functions
    
    def generate_suggestions(
        self,
        error_message: str,
        error_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Suggestion]:
        """生成智能建议
        
        Args:
            error_message: 错误消息
            error_type: 错误类型
            context: 错误上下文
        
        Returns:
            建议列表，按置信度排序
        """
        all_suggestions = []
        
        # 1. 模式匹配
        pattern_suggestions = self.pattern_matcher.match(error_message)
        all_suggestions.extend(pattern_suggestions)
        
        # 2. 拼写纠错
        if '未定义' in error_message or 'undefined' in error_message.lower():
            # 提取变量名
            match = re.search(r'[未]?定义的[变量函数]*[：:]\s*(\w+)', error_message)
            if match:
                undefined_name = match.group(1)
                spelling_suggestions = self.spelling_corrector.suggest_correction(undefined_name)
                all_suggestions.extend(spelling_suggestions)
        
        # 3. 类型相关建议
        if '类型' in error_message or 'type' in error_message.lower():
            all_suggestions.append(Suggestion(
                text="检查变量类型是否正确",
                confidence=0.8,
                category='type'
            ))
            all_suggestions.append(Suggestion(
                text="考虑进行类型转换",
                confidence=0.6,
                category='type'
            ))
        
        # 4. 上下文相关建议
        if context:
            # 括号匹配
            if '括号' in error_message or 'bracket' in error_message.lower():
                all_suggestions.append(Suggestion(
                    text="检查括号是否配对：()",
                    confidence=0.9,
                    category='syntax'
                ))
            
            # 引号匹配
            if '引号' in error_message or 'quote' in error_message.lower():
                all_suggestions.append(Suggestion(
                    text="检查引号是否配对：「」",
                    confidence=0.9,
                    category='syntax'
                ))
        
        # 5. 基于上下文的建议
        if context and 'near' in context:
            near = context['near']
            if near:
                all_suggestions.append(Suggestion(
                    text=f"检查「{near}」附近的语法",
                    confidence=0.7,
                    category='context'
                ))
        
        # 按置信度排序
        all_suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        # 返回前5个建议
        return all_suggestions[:5]
    
    def format_suggestions(self, suggestions: List[Suggestion]) -> str:
        """格式化建议列表
        
        Args:
            suggestions: 建议列表
        
        Returns:
            格式化后的字符串
        """
        if not suggestions:
            return ""
        
        lines = ["\n💡 可能的解决方案："]
        
        for i, suggestion in enumerate(suggestions, 1):
            confidence_bar = "█" * int(suggestion.confidence * 5) + "░" * (5 - int(suggestion.confidence * 5))
            lines.append(f"  {i}. {suggestion.text} [{confidence_bar}]")
        
        return "\n".join(lines)


def get_suggestions(
    error_message: str,
    error_type: str,
    context: Optional[Dict[str, Any]] = None
) -> List[Suggestion]:
    """获取建议的便捷函数"""
    engine = SmartSuggestionEngine()
    return engine.generate_suggestions(error_message, error_type, context)


def format_and_display_suggestions(
    error_message: str,
    error_type: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """获取并格式化建议"""
    suggestions = get_suggestions(error_message, error_type, context)
    engine = SmartSuggestionEngine()
    return engine.format_suggestions(suggestions)
