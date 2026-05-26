"""
优化策略接口定义
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Optional
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


class OptimizationLevel:
    """优化级别枚举"""
    O0 = 0  # 无优化
    O1 = 1  # 基础优化
    O2 = 2  # 完全优化
    Os = 3  # 空间优化
    
    @classmethod
    def get_description(cls, level: int) -> str:
        """获取优化级别的描述"""
        descriptions = {
            cls.O0: "无优化",
            cls.O1: "基础优化（常量折叠、死代码消除）",
            cls.O2: "完全优化（所有优化 + 尾递归优化）",
            cls.Os: "空间优化（优化代码大小）"
        }
        return descriptions.get(level, f"未知级别 {level}")
