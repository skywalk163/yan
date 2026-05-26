"""
表达式简化优化
简化布尔表达式和其他可简化的表达式
"""

from nodes import Node, Bool, Call, Word
from optimizer.strategy import OptimizationStrategy


class ExpressionSimplification(OptimizationStrategy):
    """表达式简化优化策略"""
    
    def optimize(self, node: Node) -> Node:
        """执行表达式简化优化"""
        return self._simplify_expressions(node)
    
    def _simplify_expressions(self, node: Node) -> Node:
        """递归遍历 AST 并简化表达式"""
        if isinstance(node, Call):
            # 递归优化参数
            new_args = [self._simplify_expressions(arg) for arg in node.args]
            
            # 尝试简化表达式
            simplified = self._simplify_call(node.verb.name, new_args)
            if simplified is not None:
                return simplified
            
            # 返回优化后的调用节点
            return Call(node.verb, new_args, node.is_partial)
        
        elif isinstance(node, Node):
            # 递归优化子节点
            for attr_name in dir(node):
                if not attr_name.startswith('_'):
                    attr_value = getattr(node, attr_name)
                    if isinstance(attr_value, Node):
                        setattr(node, attr_name, self._simplify_expressions(attr_value))
                    elif isinstance(attr_value, list):
                        new_list = []
                        for item in attr_value:
                            if isinstance(item, Node):
                                new_list.append(self._simplify_expressions(item))
                            else:
                                new_list.append(item)
                        setattr(node, attr_name, new_list)
        
        return node
    
    def _simplify_call(self, verb_name: str, args: list) -> Node:
        """简化特定的表达式"""
        if verb_name == '且':
            return self._simplify_and(args)
        elif verb_name == '或':
            return self._simplify_or(args)
        elif verb_name == '非':
            return self._simplify_not(args)
        return None
    
    def _simplify_and(self, args: list) -> Node:
        """简化布尔与表达式"""
        # 检查是否有 False
        for arg in args:
            if isinstance(arg, Bool) and arg.value is False:
                return Bool(False)
        
        # 移除 True 参数
        filtered = [arg for arg in args if not (isinstance(arg, Bool) and arg.value is True)]
        
        if len(filtered) == 0:
            return Bool(True)
        elif len(filtered) == 1:
            return filtered[0]
        else:
            return None  # 返回 None 表示无法简化
    
    def _simplify_or(self, args: list) -> Node:
        """简化布尔或表达式"""
        # 检查是否有 True
        for arg in args:
            if isinstance(arg, Bool) and arg.value is True:
                return Bool(True)
        
        # 移除 False 参数
        filtered = [arg for arg in args if not (isinstance(arg, Bool) and arg.value is False)]
        
        if len(filtered) == 0:
            return Bool(False)
        elif len(filtered) == 1:
            return filtered[0]
        else:
            return None  # 返回 None 表示无法简化
    
    def _simplify_not(self, args: list) -> Node:
        """简化布尔非表达式"""
        if len(args) == 1 and isinstance(args[0], Bool):
            return Bool(not args[0].value)
        return None
