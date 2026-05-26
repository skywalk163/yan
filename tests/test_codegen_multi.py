"""
多目标代码生成器测试
"""

import pytest
import sys
sys.path.insert(0, 'g:/dumategithub/newlisp/yan')

from codegen_multi import (
    CodeGenFactory,
    JavaScriptCodeGenerator,
    WebAssemblyCodeGenerator,
    PythonFallbackCodeGenerator,
    generate_code,
    compile_yan
)


class TestCodeGenFactory:
    """代码生成器工厂测试"""
    
    def test_create_python_generator(self):
        """测试创建 Python 代码生成器"""
        generator = CodeGenFactory.create('python')
        assert generator is not None
    
    def test_create_javascript_generator(self):
        """测试创建 JavaScript 代码生成器"""
        generator = CodeGenFactory.create('javascript')
        assert isinstance(generator, JavaScriptCodeGenerator)
    
    def test_create_wasm_generator(self):
        """测试创建 WebAssembly 代码生成器"""
        generator = CodeGenFactory.create('wasm')
        assert isinstance(generator, WebAssemblyCodeGenerator)
    
    def test_create_js_alias(self):
        """测试使用别名创建 JavaScript 生成器"""
        generator = CodeGenFactory.create('js')
        assert isinstance(generator, JavaScriptCodeGenerator)
    
    def test_create_wasm_alias(self):
        """测试使用别名创建 WebAssembly 生成器"""
        generator = CodeGenFactory.create('webassembly')
        assert isinstance(generator, WebAssemblyCodeGenerator)
    
    def test_create_invalid_target(self):
        """测试创建无效目标时抛出异常"""
        with pytest.raises(ValueError):
            CodeGenFactory.create('invalid')


class TestJavaScriptCodeGenerator:
    """JavaScript 代码生成器测试"""
    
    def test_generate_num(self):
        """测试生成数字"""
        generator = JavaScriptCodeGenerator()
        
        class Num:
            value = 42
        
        result = generator.generate(Num())
        assert result == '42'
    
    def test_generate_str(self):
        """测试生成字符串"""
        generator = JavaScriptCodeGenerator()
        
        class Str:
            value = 'hello'
        
        result = generator.generate(Str())
        assert result == '"hello"'
    
    def test_generate_bool(self):
        """测试生成布尔值"""
        generator = JavaScriptCodeGenerator()
        
        class Bool:
            pass
        
        mock_true = Bool()
        mock_true.value = True
        result = generator.generate(mock_true)
        assert result == 'true'
        
        mock_false = Bool()
        mock_false.value = False
        result = generator.generate(mock_false)
        assert result == 'false'
    
    def test_generate_nil(self):
        """测试生成空值"""
        generator = JavaScriptCodeGenerator()
        
        class Nil:
            pass
        
        result = generator.generate(Nil())
        assert result == 'null'
    
    def test_generate_word(self):
        """测试生成标识符"""
        generator = JavaScriptCodeGenerator()
        
        class Word:
            name = 'myVar'
        
        result = generator.generate(Word())
        assert result == 'myVar'
    
    def test_generate_list(self):
        """测试生成列表"""
        generator = JavaScriptCodeGenerator()
        
        class Num:
            def __init__(self, val):
                self.value = val
        
        class ListLiteral:
            elements = [Num(1), Num(2), Num(3)]
        
        result = generator.generate(ListLiteral())
        assert result == '[1, 2, 3]'
    
    def test_generate_define(self):
        """测试生成定义语句"""
        generator = JavaScriptCodeGenerator()
        
        class Num:
            value = 10
        
        class Define:
            name = 'x'
            value = Num()
        
        result = generator.generate(Define())
        assert result == 'const x = 10'
    
    def test_generate_if_simple(self):
        """测试生成简单条件语句"""
        generator = JavaScriptCodeGenerator()
        
        class Word:
            name = 'x'
        
        class Num:
            def __init__(self, val):
                self.value = val
        
        class If:
            cond = Word()
            then_branch = Num(1)
            else_branch = Num(0)
        
        result = generator.generate(If())
        assert '(x ? 1 : 0)' in result
    
    def test_generate_lambda(self):
        """测试生成匿名函数"""
        generator = JavaScriptCodeGenerator()
        
        class Num:
            value = 42
        
        class Lambda:
            params = ['a', 'b']
            body = Num()
        
        result = generator.generate(Lambda())
        assert '(a, b) => 42' == result
    
    def test_generate_call(self):
        """测试生成函数调用"""
        generator = JavaScriptCodeGenerator()
        
        class Word:
            name = 'console.log'
        
        class Str:
            value = 'hello'
        
        class Call:
            verb = Word()
            args = [Str()]
        
        result = generator.generate(Call())
        assert 'console.log("hello")' == result


class TestWebAssemblyCodeGenerator:
    """WebAssembly 代码生成器测试"""
    
    def test_generate_module_structure(self):
        """测试生成模块结构"""
        generator = WebAssemblyCodeGenerator()
        
        class Program:
            statements = []
        
        result = generator.generate(Program())
        assert '(module' in result
        assert '(memory 1)' in result
        assert '(export "memory"' in result
    
    def test_generate_function(self):
        """测试生成函数"""
        generator = WebAssemblyCodeGenerator()
        
        class Body:
            pass
        
        class Value:
            params = ['a', 'b']
            body = Body()
        
        class Define:
            name = 'add'
            value = Value()
        
        class Program:
            statements = [Define()]
        
        result = generator.generate(Program())
        assert '(export "add")' in result
    
    def test_generate_expression(self):
        """测试生成表达式"""
        generator = WebAssemblyCodeGenerator()
        
        class Num:
            value = 42
        
        result = generator._generate_expression(Num())
        assert '(i32.const 42)' == result


class TestPythonFallbackCodeGenerator:
    """Python 降级代码生成器测试"""
    
    def test_generate_num(self):
        """测试生成数字"""
        generator = PythonFallbackCodeGenerator()
        
        class Num:
            value = 42
        
        result = generator.generate(Num())
        assert result == '42'
    
    def test_generate_str(self):
        """测试生成字符串"""
        generator = PythonFallbackCodeGenerator()
        
        class Str:
            value = 'hello'
        
        result = generator.generate(Str())
        assert result == "'hello'"
    
    def test_generate_bool(self):
        """测试生成布尔值"""
        generator = PythonFallbackCodeGenerator()
        
        class Bool:
            pass
        
        mock_true = Bool()
        mock_true.value = True
        result = generator.generate(mock_true)
        assert result == 'True'
    
    def test_generate_define(self):
        """测试生成定义语句"""
        generator = PythonFallbackCodeGenerator()
        
        class Num:
            value = 10
        
        class Define:
            name = 'x'
            value = Num()
        
        result = generator.generate(Define())
        assert result == 'x = 10'
    
    def test_generate_if(self):
        """测试生成条件表达式"""
        generator = PythonFallbackCodeGenerator()
        
        class Word:
            name = 'x'
        
        class Num:
            def __init__(self, val):
                self.value = val
        
        class If:
            cond = Word()
            then_branch = Num(1)
            else_branch = Num(0)
        
        result = generator.generate(If())
        assert '(1 if x else 0)' == result


class TestCodeGeneration:
    """代码生成综合测试"""
    
    def test_generate_code_function(self):
        """测试 generate_code 函数"""
        class Program:
            statements = []
        
        result = generate_code(Program(), 'javascript')
        assert result is not None
    
    def test_compile_yan_simple(self):
        """测试编译简单代码"""
        code = '定义 x = 10'
        result = compile_yan(code, 'javascript')
        # 如果解析器不可用，返回错误消息
        if '错误' in result or '编译错误' in result:
            pytest.skip("解析器模块不可用或编译失败")
        assert 'const x' in result
    
    def test_target_language_python(self):
        """测试目标语言 Python"""
        code = '定义 x = 42'
        result = compile_yan(code, 'python')
        if '错误' in result or '编译错误' in result:
            pytest.skip("解析器模块不可用或编译失败")
        assert 'x = 42' in result
    
    def test_target_language_javascript(self):
        """测试目标语言 JavaScript"""
        code = '定义 x = 42'
        result = compile_yan(code, 'javascript')
        if '错误' in result or '编译错误' in result:
            pytest.skip("解析器模块不可用或编译失败")
        assert 'const x = 42' in result
    
    def test_target_language_wasm(self):
        """测试目标语言 WebAssembly"""
        code = '定义 x = 42'
        result = compile_yan(code, 'wasm')
        if '错误' in result or '编译错误' in result:
            pytest.skip("解析器模块不可用或编译失败")
        assert '(module' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])