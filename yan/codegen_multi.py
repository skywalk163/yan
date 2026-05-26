"""
多目标代码生成器框架
支持 Python、JavaScript、WebAssembly 等目标语言
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

try:
    from nodes import *
    from runtime import ALL_BUILTINS as BUILTINS
except ImportError:
    pass


class CodeGenerator(ABC):
    """代码生成器基类"""
    
    def __init__(self):
        self.user_defined: Dict[str, int] = {}
        self.indent_level = 0
        self.indent_str = "    "
    
    @abstractmethod
    def generate(self, node) -> str:
        """生成目标代码"""
        pass
    
    def indent(self):
        """增加缩进"""
        self.indent_level += 1
    
    def dedent(self):
        """减少缩进"""
        self.indent_level -= 1
    
    def indented(self, text: str) -> str:
        """添加缩进"""
        lines = text.split('\n')
        indented_lines = [f"{self.indent_str * self.indent_level}{line}" for line in lines]
        return '\n'.join(indented_lines)
    
    def _gen_list(self, elements):
        """生成列表字面量"""
        element_strings = [self.generate(e) for e in elements]
        return f'[{", ".join(element_strings)}]'
    
    def _gen_dict(self, items):
        """生成字典字面量"""
        pairs = [f'{self.generate(k)}: {self.generate(v)}' for k, v in items.items()]
        return f'{{{", ".join(pairs)}}}'


class JavaScriptCodeGenerator(CodeGenerator):
    """JavaScript 代码生成器"""
    
    def __init__(self):
        super().__init__()
        self.builtin_map = {
            '输出': 'console.log',
            '打印': 'console.log',
            '加': '+',
            '减': '-',
            '乘': '*',
            '除': '/',
            '余': '%',
            '大': '>',
            '小': '<',
            '等于': '===',
            '不等于': '!==',
            '与': '&&',
            '或': '||',
            '非': '!',
            '赋值': '=',
            '返回': 'return',
            '定义': 'const',
            '函数': 'function',
            '如果': 'if',
            '否则': 'else',
            '循环': 'for',
            '当': 'while',
            '列表': 'Array',
            '映射': 'Map',
            '集合': 'Set',
        }
    
    def generate(self, node) -> str:
        """生成 JavaScript 代码"""
        node_type = type(node).__name__
        
        if hasattr(node, '__class__'):
            class_name = node.__class__.__name__
        else:
            class_name = str(type(node))
        
        if hasattr(self, f'_gen_{class_name.lower()}'):
            return getattr(self, f'_gen_{class_name.lower()}')(node)
        elif hasattr(self, f'_gen_{node_type.lower()}'):
            return getattr(self, f'_gen_{node_type.lower()}')(node)
        elif isinstance(node, (int, float)):
            return repr(node)
        elif isinstance(node, str):
            return f'"{node}"'
        elif isinstance(node, bool):
            return 'true' if node else 'false'
        elif node is None:
            return 'null'
        elif isinstance(node, list):
            return self._gen_list(node)
        elif isinstance(node, dict):
            return self._gen_dict(node)
        else:
            return str(node)
    
    def _gen_program(self, node):
        """生成程序"""
        lines = []
        for stmt in getattr(node, 'statements', []):
            code = self.generate(stmt)
            if code:
                lines.append(code)
        return '\n'.join(lines)
    
    def _gen_num(self, node):
        """生成数字"""
        return repr(node.value)
    
    def _gen_str(self, node):
        """生成字符串"""
        return f'"{node.value}"'
    
    def _gen_bool(self, node):
        """生成布尔值"""
        return 'true' if node.value else 'false'
    
    def _gen_nil(self, node):
        """生成空值"""
        return 'null'
    
    def _gen_word(self, node):
        """生成标识符"""
        return node.name
    
    def _gen_call(self, node):
        """生成函数调用"""
        verb_name = getattr(node.verb, 'name', str(node.verb))
        
        if verb_name == '.':
            if hasattr(node, 'args') and len(node.args) >= 2:
                obj = self.generate(node.args[0])
                attr = self.generate(node.args[1])
                if isinstance(node.args[1], (Word,)):
                    return f'{obj}.{attr}'
                else:
                    return f'{obj}[{attr}]'
            return verb_name
        
        if verb_name == '返回':
            if hasattr(node, 'args') and node.args:
                return f'return {self.generate(node.args[0])}'
            return 'return'
        
        if verb_name in self.builtin_map:
            op = self.builtin_map[verb_name]
            if hasattr(node, 'args') and len(node.args) >= 2:
                left = self.generate(node.args[0])
                right = self.generate(node.args[1])
                return f'({left} {op} {right})'
            elif hasattr(node, 'args') and len(node.args) == 1:
                return f'({op} {self.generate(node.args[0])})'
        
        func_name = self.builtin_map.get(verb_name, verb_name)
        args = [self.generate(a) for a in getattr(node, 'args', [])]
        return f'{func_name}({", ".join(args)})'
    
    def _gen_lambda(self, node):
        """生成匿名函数"""
        params = getattr(node, 'params', [])
        params_str = ', '.join(params) if params else '_'
        body = self.generate(node.body)
        return f'({params_str}) => {body}'
    
    def _gen_define(self, node):
        """生成定义语句"""
        name = node.name
        value = self.generate(node.value)
        
        if isinstance(node.value, (Lambda,)) and hasattr(node.value, 'body'):
            if hasattr(node.value.body, 'statements'):
                return self._gen_function(name, node.value)
        
        return f'const {name} = {value}'
    
    def _gen_function(self, name, node):
        """生成函数定义"""
        params = getattr(node, 'params', [])
        params_str = ', '.join(params) if params else '_'
        
        if hasattr(node, 'body'):
            body = node.body
            if hasattr(body, 'statements'):
                self.indent()
                body_lines = []
                for stmt in body.statements:
                    code = self.generate(stmt)
                    body_lines.append(self.indented(code))
                self.dedent()
                body_code = '\n'.join(body_lines)
                return f'function {name}({params_str}) {{\n{body_code}\n}}'
            else:
                body_code = self.generate(body)
                return f'function {name}({params_str}) {{ return {body_code}; }}'
        
        return f'const {name} = ({params_str}) => {{}}'
    
    def _gen_if(self, node):
        """生成条件语句"""
        cond = self.generate(node.cond)
        then_branch = self.generate(node.then_branch)
        
        if hasattr(node.then_branch, 'statements'):
            self.indent()
            then_lines = []
            for stmt in node.then_branch.statements:
                code = self.generate(stmt)
                then_lines.append(self.indented(code))
            self.dedent()
            then_code = '\n'.join(then_lines)
            
            if hasattr(node, 'else_branch') and node.else_branch:
                self.indent()
                else_lines = []
                for stmt in node.else_branch.statements:
                    code = self.generate(stmt)
                    else_lines.append(self.indented(code))
                self.dedent()
                else_code = '\n'.join(else_lines)
                return f'if ({cond}) {{\n{then_code}\n}} else {{\n{else_code}\n}}'
            else:
                return f'if ({cond}) {{\n{then_code}\n}}'
        
        if hasattr(node, 'else_branch') and node.else_branch:
            else_code = self.generate(node.else_branch)
            return f'({cond} ? {then_branch} : {else_code})'
        else:
            return f'({cond} && {then_branch})'
    
    def _gen_foreach(self, node):
        """生成遍历循环"""
        iterable = self.generate(node.iterable)
        var = getattr(node, 'var', '_')
        
        if hasattr(node, 'body'):
            body = node.body
            if hasattr(body, 'statements'):
                self.indent()
                body_lines = []
                for stmt in body.statements:
                    code = self.generate(stmt)
                    body_lines.append(self.indented(code))
                self.dedent()
                body_code = '\n'.join(body_lines)
                return f'{iterable}.forEach({var} => {{\n{body_code}\n}})'
            else:
                body_code = self.generate(body)
                return f'{iterable}.forEach({var} => {body_code})'
        
        return f'for (const {var} of {iterable}) {{}}'
    
    def _gen_while(self, node):
        """生成 while 循环"""
        cond = self.generate(node.cond)
        
        if hasattr(node, 'body'):
            body = node.body
            if hasattr(body, 'statements'):
                self.indent()
                body_lines = []
                for stmt in body.statements:
                    code = self.generate(stmt)
                    body_lines.append(self.indented(code))
                self.dedent()
                body_code = '\n'.join(body_lines)
                return f'while ({cond}) {{\n{body_code}\n}}'
            else:
                body_code = self.generate(body)
                return f'while ({cond}) {{ {body_code} }}'
        
        return f'while ({cond}) {{}}'
    
    def _gen_block(self, node):
        """生成代码块"""
        lines = []
        for stmt in getattr(node, 'statements', []):
            code = self.generate(stmt)
            lines.extend(code.split('\n'))
        return '\n'.join(lines)
    
    def _gen_listliteral(self, node):
        """生成列表字面量"""
        return self._gen_list(getattr(node, 'elements', []))
    
    def _gen_return(self, node):
        """生成返回语句"""
        return f'return {self.generate(node.value)}'


class WebAssemblyCodeGenerator(CodeGenerator):
    """WebAssembly 代码生成器"""
    
    def __init__(self):
        super().__init__()
        self.functions = []
        self.memory = []
        self.data = []
        self.exports = []
        self.current_function = None
    
    def generate(self, node) -> str:
        """生成 WebAssembly 文本格式代码"""
        self.functions = []
        self.memory = []
        self.data = []
        self.exports = []
        
        result = self._generate_module(node)
        return result
    
    def _generate_module(self, node) -> str:
        """生成完整的 WASM 模块"""
        lines = ['(module']
        
        # 内存声明
        lines.append('  (memory 1)')
        lines.append('  (export "memory" (memory 0))')
        
        # 导入 JavaScript 函数
        lines.append('  (import "env" "console.log" (func $console_log (param i32 i32)))')
        lines.append('  (import "env" "print" (func $print (param i32)))')
        
        # 生成函数
        self._generate_functions(node)
        
        # 添加函数定义
        for func in self.functions:
            lines.append(func)
        
        # 添加数据段
        for data in self.data:
            lines.append(data)
        
        # 添加导出
        for export in self.exports:
            lines.append(export)
        
        lines.append(')')
        return '\n'.join(lines)
    
    def _generate_functions(self, node):
        """生成函数"""
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                self._generate_function(stmt)
    
    def _generate_function(self, stmt):
        """生成单个函数"""
        if hasattr(stmt, 'name') and hasattr(stmt, 'value'):
            name = stmt.name
            value = stmt.value
            
            if hasattr(value, 'params') and hasattr(value, 'body'):
                params = getattr(value, 'params', [])
                param_types = ['(param i32)' for _ in params]
                
                # 生成函数体
                func_lines = ['  (func']
                
                # 函数签名
                func_lines.append(f'    (export "{name}")')
                func_lines.append(f'    {" ".join(param_types)}')
                func_lines.append('    (result i32)')
                
                # 函数体
                func_lines.append('    (local i32)')
                func_body = self._generate_expression(value.body)
                func_lines.append(f'    {func_body}')
                
                func_lines.append('  )')
                self.functions.append('\n'.join(func_lines))
                self.exports.append(f'  (export "{name}" (func $func_{name}))')
    
    def _generate_expression(self, expr) -> str:
        """生成表达式"""
        if hasattr(expr, 'value'):
            if isinstance(expr.value, int):
                return f'(i32.const {expr.value})'
            elif isinstance(expr.value, str):
                # 字符串需要存储到内存
                str_idx = len(self.data)
                encoded = expr.value.encode('utf-8')
                data_str = ' '.join([f'{b}' for b in encoded])
                self.data.append(f'  (data (i32.const {str_idx * 256}) "{data_str}")')
                return f'(i32.const {str_idx * 256})'
        
        if hasattr(expr, 'verb') and hasattr(expr, 'args'):
            verb_name = getattr(expr.verb, 'name', str(expr.verb))
            args = [self._generate_expression(a) for a in expr.args]
            
            if verb_name == '加':
                return f'(i32.add {args[0]} {args[1]})'
            elif verb_name == '减':
                return f'(i32.sub {args[0]} {args[1]})'
            elif verb_name == '乘':
                return f'(i32.mul {args[0]} {args[1]})'
            elif verb_name == '返回':
                return args[0] if args else '(i32.const 0)'
            elif verb_name == '输出':
                return f'(call $console_log {args[0]} (i32.const {len(args[0])}))'
        
        return '(i32.const 0)'


class CodeGenFactory:
    """代码生成器工厂"""
    
    @staticmethod
    def create(target: str) -> CodeGenerator:
        """创建代码生成器"""
        target = target.lower().strip()
        
        if target in ['python', 'py']:
            try:
                from codegen import PythonCodeGen
                return PythonCodeGen()
            except ImportError:
                return PythonFallbackCodeGenerator()
        elif target in ['javascript', 'js', 'ecmascript']:
            return JavaScriptCodeGenerator()
        elif target in ['webassembly', 'wasm', 'wasm-text']:
            return WebAssemblyCodeGenerator()
        else:
            raise ValueError(f"不支持的目标语言: {target}")


class PythonFallbackCodeGenerator(CodeGenerator):
    """Python 代码生成器（降级版本）"""
    
    def __init__(self):
        super().__init__()
    
    def generate(self, node) -> str:
        """生成 Python 代码"""
        if hasattr(node, '__class__'):
            class_name = node.__class__.__name__
        else:
            class_name = str(type(node))
        
        if hasattr(self, f'_gen_{class_name.lower()}'):
            return getattr(self, f'_gen_{class_name.lower()}')(node)
        elif isinstance(node, (int, float)):
            return repr(node)
        elif isinstance(node, str):
            return repr(node)
        elif isinstance(node, bool):
            return 'True' if node else 'False'
        elif node is None:
            return 'None'
        elif isinstance(node, list):
            return self._gen_list(node)
        else:
            return str(node)
    
    def _gen_program(self, node):
        lines = []
        for stmt in getattr(node, 'statements', []):
            code = self.generate(stmt)
            if code:
                lines.append(code)
        return '\n'.join(lines)
    
    def _gen_num(self, node):
        return repr(node.value)
    
    def _gen_str(self, node):
        return repr(node.value)
    
    def _gen_bool(self, node):
        return 'True' if node.value else 'False'
    
    def _gen_nil(self, node):
        return 'None'
    
    def _gen_word(self, node):
        return node.name
    
    def _gen_call(self, node):
        verb_name = getattr(node.verb, 'name', str(node.verb))
        
        if verb_name == '返回':
            if hasattr(node, 'args') and node.args:
                return f'return {self.generate(node.args[0])}'
            return 'return'
        
        func_name = verb_name
        args = [self.generate(a) for a in getattr(node, 'args', [])]
        return f'{func_name}({", ".join(args)})'
    
    def _gen_lambda(self, node):
        params = getattr(node, 'params', [])
        params_str = ', '.join(params) if params else '_'
        body = self.generate(node.body)
        return f'(lambda {params_str}: {body})'
    
    def _gen_define(self, node):
        name = node.name
        value = self.generate(node.value)
        return f'{name} = {value}'
    
    def _gen_if(self, node):
        cond = self.generate(node.cond)
        then_code = self.generate(node.then_branch)
        
        if hasattr(node, 'else_branch') and node.else_branch:
            else_code = self.generate(node.else_branch)
            return f'({then_code} if {cond} else {else_code})'
        else:
            return f'({then_code} if {cond} else None)'
    
    def _gen_block(self, node):
        lines = []
        for stmt in getattr(node, 'statements', []):
            code = self.generate(stmt)
            lines.extend(code.split('\n'))
        return '\n'.join(lines)
    
    def _gen_listliteral(self, node):
        return self._gen_list(getattr(node, 'elements', []))


def generate_code(node, target: str = 'python') -> str:
    """生成目标代码"""
    generator = CodeGenFactory.create(target)
    return generator.generate(node)


def compile_yan(source: str, target: str = 'python') -> str:
    """编译言语言源代码到目标语言"""
    try:
        from parser import Parser
        from lexer import Lexer
        
        lexer = Lexer()
        tokens = lexer.tokenize(source)
        parser = Parser()
        ast = parser.parse(tokens)
        
        generator = CodeGenFactory.create(target)
        return generator.generate(ast)
    except ImportError as e:
        return f"错误：无法导入解析器模块，无法编译到 {target}: {e}"
    except Exception as e:
        return f"编译错误：{e}"


if __name__ == "__main__":
    # 示例：编译简单的言语言代码到不同目标
    test_code = """
定义 加法 函数(甲, 乙)
    返回 甲 + 乙
结束

定义 主 函数
    输出 加法(1, 2)
结束

主()
"""
    
    print("=== Python 输出 ===")
    print(compile_yan(test_code, 'python'))
    
    print("\n=== JavaScript 输出 ===")
    print(compile_yan(test_code, 'javascript'))
    
    print("\n=== WebAssembly 输出 ===")
    print(compile_yan(test_code, 'wasm'))
