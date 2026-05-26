"""
宏系统测试
"""

import pytest
import sys

sys.path.insert(0, 'g:/dumategithub/newlisp/yan')

from macro_system import (
    MacroSystem,
    Macro,
    MacroType,
    MacroContext,
    MacroArg,
    ExpansionResult,
    MacroTransformer,
    FunctionMacroTransformer,
    TemplateMacroTransformer,
    QuoteTransformer,
    RepeatMacroTransformer,
    ConditionalMacroTransformer,
    MacroDecorator,
    MacroError,
    get_global_macro_system,
    expand_macros,
    define_macro
)


class TestMacroContext:
    """宏上下文测试"""
    
    def test_init(self):
        """测试初始化"""
        ctx = MacroContext()
        assert ctx.variables == {}
        assert ctx.macros == {}
        assert ctx.call_stack == []
    
    def test_define_variable(self):
        """测试定义变量"""
        ctx = MacroContext()
        ctx.define_variable("x", 10)
        ctx.define_variable("y", "hello")
        
        assert ctx.get_variable("x") == 10
        assert ctx.get_variable("y") == "hello"
    
    def test_get_undefined_variable(self):
        """测试获取未定义变量"""
        ctx = MacroContext()
        assert ctx.get_variable("undefined") is None
    
    def test_enter_exit_macro(self):
        """测试宏调用栈"""
        ctx = MacroContext()
        
        ctx.enter_macro("macro1")
        assert len(ctx.call_stack) == 1
        assert ctx.call_stack[-1] == "macro1"
        
        ctx.enter_macro("macro2")
        assert len(ctx.call_stack) == 2
        
        ctx.exit_macro()
        assert len(ctx.call_stack) == 1


class TestMacro:
    """宏定义测试"""
    
    def test_macro_init(self):
        """测试宏初始化"""
        macro = Macro(
            name="test",
            macro_type=MacroType.FUNCTION,
            args=["a", "b"],
            body="a + b"
        )
        
        assert macro.name == "test"
        assert macro.macro_type == MacroType.FUNCTION
        assert len(macro.args) == 2
        assert macro.body == "a + b"
    
    def test_macro_repr(self):
        """测试宏字符串表示"""
        macro = Macro(
            name="test",
            macro_type=MacroType.FUNCTION,
            args=["x"],
            body="x"
        )
        
        assert "test" in repr(macro)
        assert "function" in repr(macro)


class TestMacroSystem:
    """宏系统测试"""
    
    def test_init(self):
        """测试初始化"""
        system = MacroSystem()
        assert len(system.macros) > 0  # 应该有内置宏
        assert "调试" in system.list_macros()
        assert "断言" in system.list_macros()
    
    def test_define_macro(self):
        """测试定义宏"""
        system = MacroSystem()
        
        macro = Macro(
            name="我的宏",
            macro_type=MacroType.FUNCTION,
            args=["x"],
            body="@x * 2"
        )
        
        system.define_macro(macro)
        
        assert "我的宏" in system.list_macros()
        assert system.get_macro("我的宏").name == "我的宏"
    
    def test_undefine_macro(self):
        """测试取消宏定义"""
        system = MacroSystem()
        
        # 先定义一个自定义宏
        macro = Macro(
            name="临时宏",
            macro_type=MacroType.FUNCTION,
            args=[],
            body=""
        )
        system.define_macro(macro)
        assert "临时宏" in system.list_macros()
        
        # 取消定义
        result = system.undefine_macro("临时宏")
        assert result is True
        assert "临时宏" not in system.list_macros()
    
    def test_undefine_nonexistent(self):
        """测试取消不存在的宏"""
        system = MacroSystem()
        result = system.undefine_macro("不存在的宏")
        assert result is False
    
    def test_get_nonexistent_macro(self):
        """测试获取不存在的宏"""
        system = MacroSystem()
        assert system.get_macro("不存在的宏") is None
    
    def test_expand_simple_function_macro(self):
        """测试展开简单函数宏"""
        system = MacroSystem()
        
        # 定义一个简单的宏
        system.define_macro(Macro(
            name="双倍",
            macro_type=MacroType.FUNCTION,
            args=["x"],
            body="@x * 2"
        ))
        
        result = system.expand("@双倍(5)")
        assert result.success is True
        assert "5 * 2" in result.code
    
    def test_expand_macro_with_variables(self):
        """测试展开带变量的宏"""
        system = MacroSystem()
        
        system.define_macro(Macro(
            name="计算",
            macro_type=MacroType.FUNCTION,
            args=["a", "b"],
            body="@a + @b"
        ))
        
        result = system.expand("@计算(3, 4)")
        assert result.success is True
        assert "3 + 4" in result.code
    
    def test_expand_conditional_macro(self):
        """测试展开条件宏"""
        system = MacroSystem()
        
        # 设置变量
        system.context.define_variable("条件", True)
        
        result = system.expand("#如果(条件, '真', '假')")
        assert result.success is True
        assert "真" in result.code
    
    def test_expand_conditional_macro_false(self):
        """测试展开条件宏（假分支）"""
        system = MacroSystem()
        
        # 设置变量为假
        system.context.define_variable("条件", False)
        
        result = system.expand("#如果(条件, '真', '假')")
        assert result.success is True
        assert "假" in result.code
    
    def test_expand_repeat_macro(self):
        """测试展开重复宏"""
        system = MacroSystem()
        
        result = system.expand("#重复(3, 输出(@index))")
        assert result.success is True
        
        # 应该有三行输出
        lines = result.code.split('\n')
        assert len(lines) == 3
    
    def test_expand_multiple_macros(self):
        """测试展开多个宏"""
        system = MacroSystem()
        
        result = system.expand("@调试('消息')")
        assert result.success is True
        assert "调试" in result.code


class TestFunctionMacroTransformer:
    """函数宏转换器测试"""
    
    def test_transform_simple(self):
        """测试简单转换"""
        macro = Macro(
            name="test",
            macro_type=MacroType.FUNCTION,
            args=["x"],
            body="@x * @x"
        )
        
        transformer = FunctionMacroTransformer(macro)
        context = MacroContext()
        
        result = transformer.transform("5", context)
        
        assert result.success is True
        assert "5 * 5" in result.code
    
    def test_transform_multiple_args(self):
        """测试多参数转换"""
        macro = Macro(
            name="add",
            macro_type=MacroType.FUNCTION,
            args=["a", "b"],
            body="@a + @b"
        )
        
        transformer = FunctionMacroTransformer(macro)
        context = MacroContext()
        
        result = transformer.transform("3, 4", context)
        
        assert result.success is True
        assert "3 + 4" in result.code


class TestQuoteTransformer:
    """引用转换器测试"""
    
    def test_quote(self):
        """测试引用"""
        transformer = QuoteTransformer()
        
        quoted = transformer.quote("x + y")
        assert "__quote__" in quoted
        
        # 展开引用
        expanded = transformer.expand_quotes(f"结果: {quoted}")
        assert "x + y" in expanded
    
    def test_unquote(self):
        """测试反引用"""
        transformer = QuoteTransformer()
        context = MacroContext()
        context.define_variable("value", 42)
        
        # 使用原始字符串避免转义问题
        code = r"${value}"
        result = transformer.unquote(code, context)
        
        assert "42" in result


class TestRepeatMacroTransformer:
    """重复宏转换器测试"""
    
    def test_transform(self):
        """测试重复转换"""
        transformer = RepeatMacroTransformer()
        context = MacroContext()
        
        result = transformer.transform("#重复(2, 打印('hello'))", context)
        
        assert result.success is True
        assert "打印('hello')" in result.code


class TestConditionalMacroTransformer:
    """条件宏转换器测试"""
    
    def test_transform_true(self):
        """测试条件为真"""
        transformer = ConditionalMacroTransformer()
        context = MacroContext()
        context.define_variable("flag", True)
        
        result = transformer.transform("#如果(flag, 'yes', 'no')", context)
        
        assert result.success is True
        assert "yes" in result.code
    
    def test_transform_false(self):
        """测试条件为假"""
        transformer = ConditionalMacroTransformer()
        context = MacroContext()
        context.define_variable("flag", False)
        
        result = transformer.transform("#如果(flag, 'yes', 'no')", context)
        
        assert result.success is True
        assert "no" in result.code


class TestGlobalMacroSystem:
    """全局宏系统测试"""
    
    def test_get_global_system(self):
        """测试获取全局系统"""
        system1 = get_global_macro_system()
        system2 = get_global_macro_system()
        
        assert system1 is system2  # 应该返回同一个实例
    
    def test_expand_macros_function(self):
        """测试快捷展开函数"""
        # 定义测试宏
        define_macro("测试", ["x"], "@x + 1", MacroType.FUNCTION)
        
        result = expand_macros("@测试(5)")
        assert "5 + 1" in result


class TestMacroDecorator:
    """宏装饰器测试"""
    
    def test_decorator(self):
        """测试装饰器"""
        system = MacroSystem()
        decorator = MacroDecorator(system)
        
        @decorator.macro(name="add_one", args=["x"])
        def add_one():
            """@x + 1"""
            pass
        
        assert "add_one" in system.list_macros()


class TestExpansionResult:
    """展开结果测试"""
    
    def test_success_result(self):
        """测试成功结果"""
        result = ExpansionResult(code="expanded", success=True)
        
        assert result.success is True
        assert result.code == "expanded"
        assert result.error is None
    
    def test_failure_result(self):
        """测试失败结果"""
        result = ExpansionResult(
            code="original",
            success=False,
            error="测试错误"
        )
        
        assert result.success is False
        assert result.error == "测试错误"
    
    def test_result_with_stats(self):
        """测试带统计的结果"""
        result = ExpansionResult(
            code="expanded",
            success=True,
            stats={"iterations": 5}
        )
        
        assert result.stats["iterations"] == 5


class TestMacroTypes:
    """宏类型测试"""
    
    def test_macro_types(self):
        """测试宏类型枚举"""
        assert MacroType.FUNCTION.value == "function"
        assert MacroType.TEMPLATE.value == "template"
        assert MacroType.CONDITIONAL.value == "conditional"
        assert MacroType.REPEAT.value == "repeat"
        assert MacroType.QUOTE.value == "quote"
        assert MacroType.UNQUOTE.value == "unquote"


class TestBuiltinMacros:
    """内置宏测试"""
    
    def test_debug_macro(self):
        """测试调试宏"""
        system = MacroSystem()
        
        assert "调试" in system.list_macros()
        macro = system.get_macro("调试")
        assert macro.doc == "打印调试信息"
    
    def test_assert_macro(self):
        """测试断言宏"""
        system = MacroSystem()
        
        assert "断言" in system.list_macros()
        macro = system.get_macro("断言")
        assert macro.doc == "断言条件为真"
    
    def test_timer_macro(self):
        """测试计时宏"""
        system = MacroSystem()
        
        assert "计时" in system.list_macros()
        macro = system.get_macro("计时")
        assert macro.doc == "测量代码块执行时间"


class TestMacroError:
    """宏错误测试"""
    
    def test_macro_error(self):
        """测试宏错误"""
        error = MacroError("测试错误")
        assert "测试错误" in str(error)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])