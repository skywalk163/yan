"""
主优化器类
协调多个优化策略的执行
"""

from typing import List, Optional, Dict, Type
from nodes import Node
from optimizer.strategy import OptimizationStrategy, OptimizationLevel
from optimizer.optimizations import (
    ConstantFolding,
    DeadCodeElimination,
    ExpressionSimplification,
    TailRecursionOptimization
)


class OptimizerConfig:
    """优化器配置"""
    def __init__(
        self,
        constant_folding: bool = True,
        dead_code_elimination: bool = True,
        expression_simplification: bool = True,
        tail_recursion_optimization: bool = True,
        optimization_level: int = OptimizationLevel.O1,
        verbose: bool = False
    ):
        self.constant_folding = constant_folding
        self.dead_code_elimination = dead_code_elimination
        self.expression_simplification = expression_simplification
        self.tail_recursion_optimization = tail_recursion_optimization
        self.optimization_level = optimization_level
        self.verbose = verbose


class ASTOptimizer:
    """AST 优化器"""
    
    def __init__(self, config: Optional[OptimizerConfig] = None):
        if config is None:
            config = OptimizerConfig()
        self.config = config
        self.optimized_count = 0
        self._optimizations: List[OptimizationStrategy] = self._create_optimizations()
    
    def _create_optimizations(self) -> List[OptimizationStrategy]:
        """根据配置创建优化策略列表"""
        optimizations: List[OptimizationStrategy] = []
        
        # 根据优化级别设置配置
        if self.config.optimization_level == OptimizationLevel.O0:
            return []
        
        # O1 及以上：基础优化
        if self.config.constant_folding:
            optimizations.append(ConstantFolding())
        
        if self.config.dead_code_elimination:
            optimizations.append(DeadCodeElimination())
        
        if self.config.expression_simplification:
            optimizations.append(ExpressionSimplification())
        
        # 尾递归优化：如果启用并且级别 >= O1
        if self.config.tail_recursion_optimization:
            optimizations.append(TailRecursionOptimization())
        
        return optimizations
    
    def optimize(self, node: Node) -> Node:
        """执行所有启用的优化"""
        for opt in self._optimizations:
            node = opt.optimize(node)
            # 统计优化次数（简化方式）
            self.optimized_count += 1
        
        return node
    
    def get_optimization_stats(self) -> Dict:
        """获取优化统计信息"""
        return {
            'optimizations_count': self.optimized_count,
            'enabled_optimizations': [opt.name for opt in self._optimizations],
            'config': {
                'constant_folding': self.config.constant_folding,
                'dead_code_elimination': self.config.dead_code_elimination,
                'expression_simplification': self.config.expression_simplification,
                'tail_recursion_optimization': self.config.tail_recursion_optimization,
                'level': self.config.optimization_level
            }
        }
    
    def add_optimization(self, optimization: OptimizationStrategy) -> None:
        """添加自定义优化策略"""
        self._optimizations.append(optimization)
    
    def remove_optimization(self, optimization_type: Type[OptimizationStrategy]) -> None:
        """移除指定类型的优化策略"""
        self._optimizations = [
            opt for opt in self._optimizations
            if not isinstance(opt, optimization_type)
        ]
