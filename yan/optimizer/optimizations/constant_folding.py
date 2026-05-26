"""
常量折叠优化
在编译时计算常量表达式的值
"""

from nodes import Node, Num, Bool, Call, Word
from optimizer.strategy import OptimizationStrategy


class ConstantFolding(OptimizationStrategy):
    """常量折叠优化策略"""
    
    def optimize(self, node: Node) -> Node:
        """执行常量折叠优化"""
        return self._fold_constants(node)
    
    def _fold_constants(self, node: Node) -> Node:
        """递归遍历 AST 并进行常量折叠"""
        if isinstance(node, Call):
            # 递归优化参数
            new_args = [self._fold_constants(arg) for arg in node.args]
            
            # 检查是否所有参数都是常量
            verb_name = node.verb.name
            if all(isinstance(arg, (Num, Bool)) for arg in new_args):
                # 尝试计算常量表达式
                result = self._evaluate_constant(verb_name, new_args)
                if result is not None:
                    return result
            
            # 返回优化后的调用节点
            return Call(node.verb, new_args, node.is_partial)
        
        elif isinstance(node, Node):
            # 递归优化子节点
            for attr_name in dir(node):
                if not attr_name.startswith('_'):
                    attr_value = getattr(node, attr_name)
                    if isinstance(attr_value, Node):
                        setattr(node, attr_name, self._fold_constants(attr_value))
                    elif isinstance(attr_value, list):
                        new_list = []
                        for item in attr_value:
                            if isinstance(item, Node):
                                new_list.append(self._fold_constants(item))
                            else:
                                new_list.append(item)
                        setattr(node, attr_name, new_list)
        
        return node
    
    def _evaluate_constant(self, verb_name: str, args: list) -> Node:
        """计算常量表达式的值"""
        try:
            if verb_name == '加':
                if len(args) >= 2:
                    return Num(sum(arg.value for arg in args if isinstance(arg, Num)))
            elif verb_name == '减':
                if len(args) >= 2:
                    values = [arg.value for arg in args if isinstance(arg, Num)]
                    if values:
                        result = values[0]
                        for val in values[1:]:
                            result -= val
                        return Num(result)
            elif verb_name == '乘':
                if len(args) >= 2:
                    result = 1
                    for arg in args:
                        if isinstance(arg, Num):
                            result *= arg.value
                    return Num(result)
            elif verb_name == '除':
                if len(args) >= 2:
                    values = [arg.value for arg in args if isinstance(arg, Num)]
                    if values:
                        result = values[0]
                        for val in values[1:]:
                            if val == 0:
                                return None  # 除以零，不优化
                            result /= val
                        return Num(result)
            elif verb_name == '模':
                if len(args) >= 2 and isinstance(args[0], Num) and isinstance(args[1], Num):
                    if args[1].value == 0:
                        return None
                    return Num(args[0].value % args[1].value)
            elif verb_name == '幂':
                if len(args) >= 2 and isinstance(args[0], Num) and isinstance(args[1], Num):
                    return Num(args[0].value ** args[1].value)
            elif verb_name == '且':
                if all(isinstance(arg, Bool) for arg in args):
                    return Bool(all(arg.value for arg in args))
            elif verb_name == '或':
                if all(isinstance(arg, Bool) for arg in args):
                    return Bool(any(arg.value for arg in args))
            elif verb_name == '非':
                if len(args) == 1 and isinstance(args[0], Bool):
                    return Bool(not args[0].value)
            elif verb_name == '大于':
                if len(args) >= 2 and isinstance(args[0], Num) and isinstance(args[1], Num):
                    return Bool(args[0].value > args[1].value)
            elif verb_name == '小于':
                if len(args) >= 2 and isinstance(args[0], Num) and isinstance(args[1], Num):
                    return Bool(args[0].value < args[1].value)
            elif verb_name == '等于':
                if len(args) >= 2:
                    return Bool(args[0].value == args[1].value)
            elif verb_name == '不等':
                if len(args) >= 2:
                    return Bool(args[0].value != args[1].value)
            elif verb_name == '大于等于':
                if len(args) >= 2 and isinstance(args[0], Num) and isinstance(args[1], Num):
                    return Bool(args[0].value >= args[1].value)
            elif verb_name == '小于等于':
                if len(args) >= 2 and isinstance(args[0], Num) and isinstance(args[1], Num):
                    return Bool(args[0].value <= args[1].value)
            
            return None
        except Exception:
            return None
