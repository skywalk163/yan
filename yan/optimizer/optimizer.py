"""
主优化器类
协调多个优化策略的执行
"""

import time
from typing import List, Optional, Dict, Type, Any

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
        constant_folding: Optional[bool] = None,
        dead_code_elimination: Optional[bool] = None,
        expression_simplification: Optional[bool] = None,
        tail_recursion_optimization: Optional[bool] = None,
        optimization_level: int = OptimizationLevel.O1,
        verbose: bool = False,
        enable_diagnostics: bool = True
    ):
        # 先应用优化级别配置作为默认值
        self.optimization_level = optimization_level
        level_config = OptimizationLevel.get_enabled_optimizations(optimization_level)
        
        # 使用用户自定义配置，如果用户没有指定则使用优化级别的默认值
        self.constant_folding = constant_folding if constant_folding is not None else level_config['constant_folding']
        self.dead_code_elimination = dead_code_elimination if dead_code_elimination is not None else level_config['dead_code_elimination']
        self.expression_simplification = expression_simplification if expression_simplification is not None else level_config['expression_simplification']
        self.tail_recursion_optimization = tail_recursion_optimization if tail_recursion_optimization is not None else level_config['tail_recursion_optimization']
        self.verbose = verbose
        self.enable_diagnostics = enable_diagnostics


class ASTOptimizer:
    """AST 优化器"""
    
    def __init__(self, config: Optional[OptimizerConfig] = None):
        if config is None:
            config = OptimizerConfig()
        self.config = config
        self.optimized_count = 0
        self._optimizations: List[OptimizationStrategy] = self._create_optimizations()
        self._diagnostics: Dict[str, Any] = {
            'optimization_times': {},
            'applied_optimizations': [],
            'node_counts': {},
            'start_time': 0.0,
            'end_time': 0.0
        }
    
    def _create_optimizations(self) -> List[OptimizationStrategy]:
        """根据配置创建优化策略列表"""
        optimizations: List[OptimizationStrategy] = []
        
        if self.config.optimization_level == OptimizationLevel.O0:
            return []
        
        if self.config.constant_folding:
            optimizations.append(ConstantFolding())
        
        if self.config.dead_code_elimination:
            optimizations.append(DeadCodeElimination())
        
        if self.config.expression_simplification:
            optimizations.append(ExpressionSimplification())
        
        if self.config.tail_recursion_optimization:
            optimizations.append(TailRecursionOptimization())
        
        return optimizations
    
    def optimize(self, node: Node) -> Node:
        """执行所有启用的优化"""
        if self.config.enable_diagnostics:
            self._diagnostics['start_time'] = time.time()
        
        original_node = node
        
        for opt in self._optimizations:
            if self.config.enable_diagnostics:
                opt_start = time.time()
            
            node = opt.optimize(node)
            
            if self.config.enable_diagnostics:
                opt_time = time.time() - opt_start
                self._diagnostics['optimization_times'][opt.name] = opt_time
                self._diagnostics['applied_optimizations'].append(opt.name)
            
            self.optimized_count += 1
        
        if self.config.enable_diagnostics:
            self._diagnostics['end_time'] = time.time()
        
        if self.config.verbose:
            self._print_optimization_summary(original_node, node)
        
        return node
    
    def _print_optimization_summary(self, original: Node, optimized: Node):
        """打印优化摘要"""
        print(f"优化器执行摘要:")
        print(f"  应用的优化: {', '.join(self._diagnostics['applied_optimizations'])}")
        print(f"  优化次数: {self.optimized_count}")
        print(f"  总耗时: {self.get_total_time():.4f}s")
    
    def get_total_time(self) -> float:
        """获取优化总耗时"""
        if self.config.enable_diagnostics:
            return self._diagnostics['end_time'] - self._diagnostics['start_time']
        return 0.0
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        stats = {
            'optimizations_count': self.optimized_count,
            'enabled_optimizations': [opt.name for opt in self._optimizations],
            'total_time_ms': self.get_total_time() * 1000,
            'config': {
                'constant_folding': self.config.constant_folding,
                'dead_code_elimination': self.config.dead_code_elimination,
                'expression_simplification': self.config.expression_simplification,
                'tail_recursion_optimization': self.config.tail_recursion_optimization,
                'level': self.config.optimization_level,
                'level_description': OptimizationLevel.get_description(self.config.optimization_level)
            }
        }
        
        if self.config.enable_diagnostics:
            stats['diagnostics'] = {
                'optimization_times_ms': {
                    name: time * 1000 
                    for name, time in self._diagnostics['optimization_times'].items()
                },
                'applied_optimizations': self._diagnostics['applied_optimizations']
            }
        
        return stats
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """获取详细诊断信息"""
        return self._diagnostics
    
    def add_optimization(self, optimization: OptimizationStrategy) -> None:
        """添加自定义优化策略"""
        self._optimizations.append(optimization)
    
    def remove_optimization(self, optimization_type: Type[OptimizationStrategy]) -> None:
        """移除指定类型的优化策略"""
        self._optimizations = [
            opt for opt in self._optimizations
            if not isinstance(opt, optimization_type)
        ]
    
    def clear_optimizations(self) -> None:
        """清除所有优化策略"""
        self._optimizations = []
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self.optimized_count = 0
        self._diagnostics = {
            'optimization_times': {},
            'applied_optimizations': [],
            'node_counts': {},
            'start_time': 0.0,
            'end_time': 0.0
        }