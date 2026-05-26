"""
优化策略实现模块
"""

from .constant_folding import ConstantFolding
from .dead_code_elimination import DeadCodeElimination
from .expression_simplification import ExpressionSimplification
from .tail_recursion_optimization import TailRecursionOptimization

__all__ = [
    'ConstantFolding',
    'DeadCodeElimination',
    'ExpressionSimplification',
    'TailRecursionOptimization'
]
