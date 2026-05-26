"""
尾递归优化策略
检测并标记尾递归函数，用于代码生成阶段的优化
"""

from nodes import Node, Define, Lambda, Call, Word, If, Block
from optimizer.strategy import OptimizationStrategy


class TailRecursionOptimization(OptimizationStrategy):
    """尾递归优化策略"""
    
    def optimize(self, node: Node) -> Node:
        """执行尾递归优化（检测并标记尾递归函数）"""
        return self._detect_tail_recursion(node)
    
    def _detect_tail_recursion(self, node: Node) -> Node:
        """检测尾递归函数"""
        if isinstance(node, Define):
            if isinstance(node.value, Lambda):
                # 检查是否是尾递归函数
                if self._is_tail_recursive(node.value.body, node.name):
                    # 标记这个函数需要优化
                    if not hasattr(node.value, 'is_tail_recursive'):
                        node.value.is_tail_recursive = True
            return node
        elif isinstance(node, Block):
            # 递归处理块中的语句
            new_statements = []
            for stmt in node.statements:
                new_statements.append(self._detect_tail_recursion(stmt))
            return Block(statements=new_statements)
        elif isinstance(node, Lambda):
            # 直接处理 lambda
            if self._is_tail_recursive(node.body, None):
                if not hasattr(node, 'is_tail_recursive'):
                    node.is_tail_recursive = True
            return node
        elif isinstance(node, If):
            # 处理条件分支
            node.cond = self._detect_tail_recursion(node.cond)
            node.then_branch = self._detect_tail_recursion(node.then_branch)
            if node.else_branch:
                node.else_branch = self._detect_tail_recursion(node.else_branch)
            return node
        elif isinstance(node, Node):
            # 递归处理其他节点类型
            for attr_name in dir(node):
                if not attr_name.startswith('_'):
                    attr_value = getattr(node, attr_name)
                    if isinstance(attr_value, Node):
                        setattr(node, attr_name, self._detect_tail_recursion(attr_value))
                    elif isinstance(attr_value, list):
                        new_list = []
                        for item in attr_value:
                            if isinstance(item, Node):
                                new_list.append(self._detect_tail_recursion(item))
                            else:
                                new_list.append(item)
                        setattr(node, attr_name, new_list)
        return node
    
    def _is_tail_recursive(self, node: Node, func_name: str) -> bool:
        """检查函数体是否以尾递归形式调用自身"""
        if func_name is None:
            return False
        
        if isinstance(node, Call) and node.verb.name == func_name:
            # 直接尾递归调用
            return True
        elif isinstance(node, If):
            # 检查两个分支是否都以尾递归调用结束
            then_tail = self._is_tail_recursive(node.then_branch, func_name)
            else_tail = False
            if node.else_branch:
                else_tail = self._is_tail_recursive(node.else_branch, func_name)
            return then_tail or else_tail
        elif isinstance(node, Block):
            # 检查块的最后一条语句
            if node.statements:
                return self._is_tail_recursive(node.statements[-1], func_name)
        return False
