"""
言语言错误建议生成器
自动生成错误修复建议
"""
from typing import List, Set, Optional


class ErrorSuggestionGenerator:
    """错误建议生成器"""
    
    def suggest_similar_name(self, name: str, candidates: Set[str], max_suggestions: int = 3) -> List[str]:
        """
        建议相似的名称
        
        Args:
            name: 错误的名称
            candidates: 候选名称集合
            max_suggestions: 最多建议数量
        
        Returns:
            相似名称列表，按相似度排序
        """
        if name in candidates:
            return []
        
        distances = []
        for candidate in candidates:
            distance = self._levenshtein_distance(name, candidate)
            distances.append((candidate, distance))
        
        distances.sort(key=lambda x: x[1])
        
        suggestions = []
        for candidate, distance in distances:
            if distance <= len(name) // 2 + 1:
                suggestions.append(candidate)
                if len(suggestions) >= max_suggestions:
                    break
        
        return suggestions
    
    def suggest_arity_fix(self, func_name: str, expected: int, actual: int) -> str:
        """
        生成参数数量错误建议
        
        Args:
            func_name: 函数名
            expected: 期望参数数量
            actual: 实际参数数量
        
        Returns:
            建议文本
        """
        if actual < expected:
            missing = expected - actual
            return f"函数 {func_name} 需要 {expected} 个参数，缺少 {missing} 个参数。"
        else:
            extra = actual - expected
            return f"函数 {func_name} 只需要 {expected} 个参数，提供了 {actual} 个（多 {extra} 个）。"
    
    def suggest_type_fix(self, expected_type: str, actual_type: str) -> str:
        """
        生成类型错误建议
        
        Args:
            expected_type: 期望类型
            actual_type: 实际类型
        
        Returns:
            建议文本
        """
        return f"期望类型：{expected_type}，实际类型：{actual_type}。"
    
    def suggest_index_fix(self, index: int, length: int) -> str:
        """
        生成索引越界建议
        
        Args:
            index: 错误的索引
            length: 列表长度
        
        Returns:
            建议文本
        """
        if index < 0:
            return f"索引 {index} 为负数，请使用 0-{length-1} 之间的正索引。"
        else:
            return f"索引 {index} 超出范围，列表长度为 {length}，有效索引为 0-{length-1}。"
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算编辑距离（Levenshtein Distance）
        
        Args:
            s1: 字符串1
            s2: 字符串2
        
        Returns:
            编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
