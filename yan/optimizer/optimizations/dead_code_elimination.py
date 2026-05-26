"""
死代码消除优化
移除永远不会执行的代码分支
"""

from nodes import Node, Bool, If, Block
from optimizer.strategy import OptimizationStrategy


class DeadCodeElimination(OptimizationStrategy):
    """死代码消除优化策略"""
    
    def optimize(self, node: Node) -> Node:
        """执行死代码消除优化"""
        return self._eliminate_dead_code(node)
    
    def _eliminate_dead_code(self, node: Node) -> Node:
        """递归遍历 AST 并消除死代码"""
        if isinstance(node, If):
            # 优化条件表达式
            node.cond = self._eliminate_dead_code(node.cond)
            
            # 检查条件是否为常量布尔值
            if isinstance(node.cond, Bool):
                if node.cond.value:
                    # 条件永远为真，返回 then_branch
                    return self._eliminate_dead_code(node.then_branch)
                else:
                    # 条件永远为假，返回 else_branch（如果存在）
                    if node.else_branch:
                        return self._eliminate_dead_code(node.else_branch)
                    return None  # 没有 else 分支，返回空
            
            # 递归优化分支
            node.then_branch = self._eliminate_dead_code(node.then_branch)
            if node.else_branch:
                node.else_branch = self._eliminate_dead_code(node.else_branch)
            
            return node
        
        elif isinstance(node, Block):
            # 优化块中的语句
            new_statements = []
            for stmt in node.statements:
                optimized = self._eliminate_dead_code(stmt)
                if optimized is not None:
                    new_statements.append(optimized)
            node.statements = new_statements
            return node
        
        elif isinstance(node, Node):
            # 递归优化子节点
            for attr_name in dir(node):
                if not attr_name.startswith('_'):
                    attr_value = getattr(node, attr_name)
                    if isinstance(attr_value, Node):
                        optimized = self._eliminate_dead_code(attr_value)
                        if optimized is None:
                            setattr(node, attr_name, None)
                        else:
                            setattr(node, attr_name, optimized)
                    elif isinstance(attr_value, list):
                        new_list = []
                        for item in attr_value:
                            if isinstance(item, Node):
                                optimized = self._eliminate_dead_code(item)
                                if optimized is not None:
                                    new_list.append(optimized)
                            else:
                                new_list.append(item)
                        setattr(node, attr_name, new_list)
        
        return node
