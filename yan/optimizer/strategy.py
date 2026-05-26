"""
优化策略接口定义
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Optional, Dict, Any

from nodes import Node

NodeType = TypeVar('NodeType', bound=Node)


class OptimizationStrategy(ABC):
    """优化策略接口"""
    
    @abstractmethod
    def optimize(self, node: Node) -> Node:
        """执行优化，返回优化后的节点"""
        pass
    
    @property
    def name(self) -> str:
        """优化策略名称"""
        return self.__class__.__name__
    
    @property
    def requires(self) -> list:
        """此优化依赖的其他优化策略"""
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        """获取此优化策略的统计信息"""
        return {'name': self.name}


class OptimizationLevel:
    """优化级别枚举"""
    O0 = 0  
    O1 = 1  
    O2 = 2  
    Os = 3  
    Ofast = 4  
    
    @classmethod
    def get_description(cls, level: int) -> str:
        """获取优化级别的描述"""
        descriptions = {
            cls.O0: "无优化",
            cls.O1: "基础优化（常量折叠、死代码消除、表达式简化）",
            cls.O2: "完全优化（所有优化 + 尾递归优化）",
            cls.Os: "空间优化（优化代码大小）",
            cls.Ofast: "快速优化（牺牲正确性换取速度）"
        }
        return descriptions.get(level, f"未知级别 {level}")
    
    @classmethod
    def get_enabled_optimizations(cls, level: int) -> Dict[str, bool]:
        """根据优化级别获取启用的优化策略"""
        configs = {
            cls.O0: {
                'constant_folding': False,
                'dead_code_elimination': False,
                'expression_simplification': False,
                'tail_recursion_optimization': False
            },
            cls.O1: {
                'constant_folding': True,
                'dead_code_elimination': True,
                'expression_simplification': True,
                'tail_recursion_optimization': False
            },
            cls.O2: {
                'constant_folding': True,
                'dead_code_elimination': True,
                'expression_simplification': True,
                'tail_recursion_optimization': True
            },
            cls.Os: {
                'constant_folding': True,
                'dead_code_elimination': True,
                'expression_simplification': True,
                'tail_recursion_optimization': False
            },
            cls.Ofast: {
                'constant_folding': True,
                'dead_code_elimination': True,
                'expression_simplification': True,
                'tail_recursion_optimization': True
            }
        }
        return configs.get(level, configs[cls.O1])