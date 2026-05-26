"""
优化器增强测试
测试优化级别、策略模式、统计信息等新功能
"""

import pytest
from optimizer import ASTOptimizer, OptimizerConfig
from optimizer.strategy import OptimizationLevel
from optimizer.optimizations import (
    ConstantFolding,
    DeadCodeElimination,
    ExpressionSimplification,
    TailRecursionOptimization
)
from nodes import Num, Bool, Call, Word, If, Block, Define, Lambda


class TestOptimizerConfig:
    """测试优化器配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = OptimizerConfig()
        
        assert config.constant_folding == True
        assert config.dead_code_elimination == True
        assert config.expression_simplification == True
        assert config.tail_recursion_optimization == True
        assert config.optimization_level == OptimizationLevel.O1
        assert config.verbose == False
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = OptimizerConfig(
            constant_folding=False,
            optimization_level=OptimizationLevel.O2,
            verbose=True
        )
        
        assert config.constant_folding == False
        assert config.optimization_level == OptimizationLevel.O2
        assert config.verbose == True


class TestOptimizationLevels:
    """测试优化级别"""
    
    def test_optimization_level_descriptions(self):
        """测试优化级别描述"""
        assert OptimizationLevel.get_description(OptimizationLevel.O0) == "无优化"
        assert OptimizationLevel.get_description(OptimizationLevel.O1) == "基础优化（常量折叠、死代码消除）"
        assert OptimizationLevel.get_description(OptimizationLevel.O2) == "完全优化（所有优化 + 尾递归优化）"
        assert OptimizationLevel.get_description(OptimizationLevel.Os) == "空间优化（优化代码大小）"
    
    def test_o0_no_optimizations(self):
        """测试 O0 级别不执行任何优化"""
        config = OptimizerConfig(optimization_level=OptimizationLevel.O0)
        optimizer = ASTOptimizer(config)
        
        # 验证没有启用任何优化
        assert len(optimizer._optimizations) == 0
    
    def test_o1_basic_optimizations(self):
        """测试 O1 级别启用基础优化"""
        config = OptimizerConfig(optimization_level=OptimizationLevel.O1)
        optimizer = ASTOptimizer(config)
        
        # 验证启用了基础优化
        optimization_names = [opt.name for opt in optimizer._optimizations]
        assert "ConstantFolding" in optimization_names
        assert "DeadCodeElimination" in optimization_names
        assert "ExpressionSimplification" in optimization_names
    
    def test_o2_full_optimizations(self):
        """测试 O2 级别启用所有优化"""
        config = OptimizerConfig(optimization_level=OptimizationLevel.O2)
        optimizer = ASTOptimizer(config)
        
        # 验证启用了所有优化
        optimization_names = [opt.name for opt in optimizer._optimizations]
        assert "TailRecursionOptimization" in optimization_names


class TestOptimizerStatistics:
    """测试优化器统计信息"""
    
    def test_get_optimization_stats(self):
        """测试获取优化统计信息"""
        config = OptimizerConfig()
        optimizer = ASTOptimizer(config)
        
        stats = optimizer.get_optimization_stats()
        
        assert "optimizations_count" in stats
        assert "enabled_optimizations" in stats
        assert "config" in stats
        
        # 验证配置信息
        assert stats["config"]["constant_folding"] == True
        assert isinstance(stats["enabled_optimizations"], list)


class TestOptimizerExtensions:
    """测试优化器扩展功能"""
    
    def test_add_custom_optimization(self):
        """测试添加自定义优化策略"""
        config = OptimizerConfig()
        optimizer = ASTOptimizer(config)
        
        # 创建一个简单的自定义优化策略
        class CustomOptimization:
            name = "CustomOptimization"
        
        # 添加自定义优化
        optimizer.add_optimization(CustomOptimization())
        
        # 验证自定义优化被添加
        optimization_names = [opt.name for opt in optimizer._optimizations]
        assert "CustomOptimization" in optimization_names
    
    def test_remove_optimization(self):
        """测试移除优化策略"""
        config = OptimizerConfig()
        optimizer = ASTOptimizer(config)
        
        # 移除常量折叠优化
        optimizer.remove_optimization(ConstantFolding)
        
        # 验证常量折叠被移除
        optimization_names = [opt.name for opt in optimizer._optimizations]
        assert "ConstantFolding" not in optimization_names


class TestOptimizationStrategyInterface:
    """测试优化策略接口"""
    
    def test_strategy_name(self):
        """测试策略名称属性"""
        cf = ConstantFolding()
        dce = DeadCodeElimination()
        es = ExpressionSimplification()
        tro = TailRecursionOptimization()
        
        assert cf.name == "ConstantFolding"
        assert dce.name == "DeadCodeElimination"
        assert es.name == "ExpressionSimplification"
        assert tro.name == "TailRecursionOptimization"
    
    def test_strategy_requires(self):
        """测试策略依赖属性"""
        cf = ConstantFolding()
        
        # 默认情况下没有依赖
        assert cf.requires == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
