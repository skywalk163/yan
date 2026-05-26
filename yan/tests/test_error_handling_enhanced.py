"""
错误处理增强测试
测试错误恢复、智能建议等新功能
"""

import pytest
from error import YanError, SourceLocation, ParserError, LexerError, RuntimeError
from error_recovery import (
    ErrorRecoveryManager,
    ErrorContextCollector,
    SkipStatementStrategy,
    InsertMissingTokenStrategy,
    ReplaceInvalidTokenStrategy,
    ContinueAfterErrorStrategy,
    get_recovery_manager,
    get_context_collector
)
from smart_error_suggestor import (
    SmartErrorSuggestor,
    Suggestion,
    get_smart_suggestor,
    suggest_for_error
)


class TestErrorRecovery:
    """测试错误恢复功能"""
    
    def test_recovery_manager_init(self):
        """测试恢复管理器初始化"""
        rm = ErrorRecoveryManager()
        
        assert rm.max_errors == 10
        assert rm.enable_recovery == True
        assert rm.error_count == 0
    
    def test_recovery_manager_should_recover(self):
        """测试是否应该恢复"""
        rm = ErrorRecoveryManager(max_errors=2)
        
        assert rm.should_recover() == True
        
        # 添加两个错误
        error1 = ParserError("测试错误1", SourceLocation(1, 1))
        error2 = ParserError("测试错误2", SourceLocation(2, 2))
        rm.recover(error1)
        rm.recover(error2)
        
        # 第三个错误应该不恢复
        assert rm.should_recover() == False
    
    def test_skip_statement_strategy(self):
        """测试跳过语句策略"""
        strategy = SkipStatementStrategy()
        
        # 语法错误应该可以恢复
        syntax_error = ParserError("语法错误", SourceLocation(1, 1))
        assert strategy.can_recover(syntax_error) == True
        
        # 词法错误应该可以恢复
        lexer_error = LexerError("词法错误", SourceLocation(1, 1))
        assert strategy.can_recover(lexer_error) == True
        
        # 运行时错误不应该被此策略恢复
        runtime_error = RuntimeError("运行时错误", SourceLocation(1, 1))
        assert strategy.can_recover(runtime_error) == False
    
    def test_insert_missing_token_strategy(self):
        """测试插入缺失令牌策略"""
        strategy = InsertMissingTokenStrategy()
        
        # 期望关键字的错误应该可以恢复
        error = ParserError("期望 '则'", SourceLocation(1, 1))
        assert strategy.can_recover(error) == True
        
        # 缺少关键字的错误应该可以恢复
        error2 = ParserError("缺少 '于' 关键字", SourceLocation(1, 1))
        assert strategy.can_recover(error2) == True
    
    def test_replace_invalid_token_strategy(self):
        """测试替换无效令牌策略"""
        strategy = ReplaceInvalidTokenStrategy()
        
        # 无效字符错误应该可以恢复
        error = LexerError("无效字符", SourceLocation(1, 1))
        assert strategy.can_recover(error) == True
        
        # 非法令牌错误应该可以恢复
        error2 = LexerError("非法令牌", SourceLocation(1, 1))
        assert strategy.can_recover(error2) == True
    
    def test_continue_after_error_strategy(self):
        """测试继续执行策略"""
        strategy = ContinueAfterErrorStrategy()
        
        # 运行时错误应该可以恢复
        runtime_error = RuntimeError("运行时错误", SourceLocation(1, 1))
        assert strategy.can_recover(runtime_error) == True
        
        # 语法错误不应该被此策略恢复
        syntax_error = ParserError("语法错误", SourceLocation(1, 1))
        assert strategy.can_recover(syntax_error) == False
    
    def test_recovery_action_recording(self):
        """测试恢复操作记录"""
        rm = ErrorRecoveryManager()
        error = ParserError("测试错误", SourceLocation(1, 1))
        
        action = rm.recover(error)
        
        assert action is not None
        assert action.applied == True
        assert action.original_error == error
        assert len(rm.recovery_actions) == 1
    
    def test_recovery_summary(self):
        """测试恢复摘要"""
        rm = ErrorRecoveryManager()
        
        # 添加一些错误
        rm.recover(ParserError("错误1", SourceLocation(1, 1)))
        rm.recover(LexerError("错误2", SourceLocation(2, 2)))
        
        summary = rm.get_recovery_summary()
        
        assert summary['total_errors'] == 2
        assert summary['recovered_errors'] == 2
        assert summary['unrecovered_errors'] == 0
    
    def test_recovery_manager_reset(self):
        """测试恢复管理器重置"""
        rm = ErrorRecoveryManager()
        
        rm.recover(ParserError("错误", SourceLocation(1, 1)))
        assert rm.error_count == 1
        
        rm.reset()
        assert rm.error_count == 0
        assert len(rm.errors) == 0
        assert len(rm.recovery_actions) == 0


class TestErrorContextCollector:
    """测试错误上下文收集器"""
    
    def test_context_collector_init(self):
        """测试上下文收集器初始化"""
        cc = ErrorContextCollector()
        
        assert cc.symbol_table == {}
        assert cc.call_stack == []
        assert cc.source_code == ""
    
    def test_add_symbol(self):
        """测试添加符号"""
        cc = ErrorContextCollector()
        location = SourceLocation(1, 1)
        
        cc.add_symbol("test_var", 42, location)
        
        assert "test_var" in cc.symbol_table
        assert cc.symbol_table["test_var"]['value'] == 42
        assert cc.symbol_table["test_var"]['type'] == 'int'
    
    def test_call_stack(self):
        """测试调用栈"""
        cc = ErrorContextCollector()
        location = SourceLocation(1, 1)
        
        cc.push_call("test_func", location)
        assert len(cc.call_stack) == 1
        
        popped = cc.pop_call()
        assert popped['function'] == "test_func"
        assert len(cc.call_stack) == 0
    
    def test_set_source_code(self):
        """测试设置源代码"""
        cc = ErrorContextCollector()
        code = "第一行\n第二行\n第三行"
        
        cc.set_source_code(code)
        
        assert cc.source_code == code
        assert cc.line_numbers[1] == "第一行"
        assert cc.line_numbers[2] == "第二行"
        assert cc.line_numbers[3] == "第三行"
    
    def test_get_context_for_error(self):
        """测试获取错误上下文"""
        cc = ErrorContextCollector()
        cc.set_source_code("def x = 1")
        cc.add_symbol("x", 1, SourceLocation(1, 1))
        
        error = ParserError("测试错误", SourceLocation(1, 5))
        context = cc.get_context_for_error(error)
        
        assert 'error' in context
        assert 'line_content' in context
        assert 'nearby_symbols' in context
        assert 'call_stack' in context


class TestSmartErrorSuggestor:
    """测试智能错误建议器"""
    
    def test_suggestor_init(self):
        """测试建议器初始化"""
        suggestor = SmartErrorSuggestor()
        
        assert suggestor.context_collector is None
    
    def test_pattern_matching(self):
        """测试模式匹配"""
        suggestor = SmartErrorSuggestor()
        
        error = ParserError("期望 '则'", SourceLocation(1, 1))
        suggestions = suggestor.suggest(error)
        
        assert len(suggestions) > 0
        assert any("那么" in s.text for s in suggestions)
    
    def test_spelling_correction(self):
        """测试拼写修正"""
        suggestor = SmartErrorSuggestor()
        
        error = ParserError("定议 x = 1", SourceLocation(1, 1), source="定议 x = 1")
        suggestions = suggestor.suggest(error)
        
        # 应该检测到 "定议" 应该是 "定义"
        assert len(suggestions) > 0
    
    def test_context_analysis(self):
        """测试上下文分析"""
        suggestor = SmartErrorSuggestor()
        
        source = "如果 x > 0"
        error = ParserError("期望 '则'", SourceLocation(1, 1), source=source)
        suggestions = suggestor.suggest(error)
        
        # 应该检测到缺少 "那么"
        assert len(suggestions) > 0
    
    def test_suggestion_types(self):
        """测试建议类型"""
        suggestor = SmartErrorSuggestor()
        
        error = ParserError("期望 '则'", SourceLocation(1, 1))
        suggestions = suggestor.suggest(error)
        
        # 检查建议类型
        for s in suggestions:
            assert s.type in ["suggestion", "fix", "reference", "example"]
    
    def test_confidence_sorting(self):
        """测试置信度排序"""
        suggestor = SmartErrorSuggestor()
        
        error = ParserError("期望 '则'", SourceLocation(1, 1))
        suggestions = suggestor.suggest(error)
        
        # 应该按置信度排序
        confidences = [s.confidence for s in suggestions]
        assert confidences == sorted(confidences, reverse=True)
    
    def test_generate_code_fix(self):
        """测试生成代码修复"""
        suggestor = SmartErrorSuggestor()
        
        error = ParserError("期望 '则'", SourceLocation(1, 1))
        fix = suggestor.generate_code_fix(error)
        
        assert fix is not None
        assert "那么" in fix


class TestGlobalInstances:
    """测试全局实例"""
    
    def test_global_recovery_manager(self):
        """测试全局恢复管理器"""
        rm = get_recovery_manager()
        
        assert isinstance(rm, ErrorRecoveryManager)
    
    def test_global_context_collector(self):
        """测试全局上下文收集器"""
        cc = get_context_collector()
        
        assert isinstance(cc, ErrorContextCollector)
    
    def test_global_smart_suggestor(self):
        """测试全局智能建议器"""
        suggestor = get_smart_suggestor()
        
        assert isinstance(suggestor, SmartErrorSuggestor)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
