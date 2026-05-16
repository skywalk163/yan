"""
言语言代码生成器（性能优化版）
优化热点：
1. 减少 isinstance() 调用
2. 优化字符串拼接
3. 缓存运算符映射
"""

from enum import Enum

class NodeType(Enum):
    PROGRAM = 1
    NUM = 2
    STR = 3
    BOOL = 4
    NULL = 5
    WORD = 6
    DEFINE = 7
    LAMBDA = 8
    CALL = 9
    IF = 10
    WHILE = 11
    PYTHON = 12

class CodeGenError(Exception):
    pass

class PythonCodeGen:
    OP_MAP = {
        '加': '+',
        '减': '-',
        '乘': '*',
        '除': '/',
        '等于': '==',
        '不等': '!=',
        '大于': '>',
        '小于': '<',
        '大等于': '>=',
        '小等于': '<=',
    }
    
    def __init__(self):
        self.indent_level = 0
    
    def generate(self, ast):
        if not ast:
            return ""
        
        node_type = ast[0]
        
        if node_type == NodeType.PROGRAM:
            return self._gen_program(ast)
        elif node_type == NodeType.NUM:
            return self._gen_number(ast)
        elif node_type == NodeType.STR:
            return self._gen_string(ast)
        elif node_type == NodeType.BOOL:
            return self._gen_bool(ast)
        elif node_type == NodeType.NULL:
            return 'None'
        elif node_type == NodeType.WORD:
            return self._gen_word(ast)
        elif node_type == NodeType.DEFINE:
            return self._gen_define(ast)
        elif node_type == NodeType.LAMBDA:
            return self._gen_lambda(ast)
        elif node_type == NodeType.CALL:
            return self._gen_call(ast)
        elif node_type == NodeType.IF:
            return self._gen_if(ast)
        elif node_type == NodeType.WHILE:
            return self._gen_while(ast)
        elif node_type == NodeType.PYTHON:
            return self._gen_python(ast)
        
        return ""
    
    def _gen_program(self, node):
        statements = node[1][0]
        lines = []
        
        for stmt in statements:
            code = self.generate(stmt)
            if code:
                lines.append(code)
        
        return '\n'.join(lines)
    
    def _gen_number(self, node):
        return node[1]
    
    def _gen_string(self, node):
        return repr(node[1])
    
    def _gen_bool(self, node):
        return 'True' if node[1] else 'False'
    
    def _gen_word(self, node):
        return str(node[1]) if len(node) > 1 else ''
    
    def _gen_define(self, node):
        name = node[1][0]
        value = self.generate(node[1][1])
        return f"{name} = {value}"
    
    def _gen_lambda(self, node):
        name = node[1][0]
        params = node[1][1]
        body = self.generate(node[1][2])
        
        param_str = ', '.join(params)
        return f"def {name}({param_str}):\n    {body}"
    
    def _gen_call(self, node):
        verb = node[1][0]
        args = node[1][1]
        
        if verb == '列':
            return self._gen_list(args)
        elif verb == '入':
            return self._gen_index(args)
        elif verb == '取':
            return self._gen_index(args)
        elif verb == '添':
            return self._gen_append(args)
        elif verb == '连':
            return self._gen_concat(args)
        elif verb == '印':
            return self._gen_print(args)
        elif verb == '长':
            return self._gen_len(args)
        elif verb in self.OP_MAP:
            return self._gen_op(verb, args)
        else:
            return self._gen_func_call(verb, args)
    
    def _gen_list(self, args):
        if not args:
            return '[]'
        return '[' + ', '.join(self.generate(arg) for arg in args) + ']'
    
    def _gen_index(self, args):
        if len(args) < 2:
            return ''
        obj = self.generate(args[0])
        idx = self.generate(args[1])
        return f"{obj}[{idx}]"
    
    def _gen_append(self, args):
        if len(args) < 2:
            return ''
        obj = self.generate(args[0])
        item = self.generate(args[1])
        return f"{obj}.append({item})"
    
    def _gen_concat(self, args):
        if not args:
            return ''
        parts = [self.generate(arg) for arg in args]
        return '(' + ' + '.join(parts) + ')'
    
    def _gen_print(self, args):
        if not args:
            return 'print()'
        return 'print(' + ', '.join(self.generate(arg) for arg in args) + ')'
    
    def _gen_len(self, args):
        if not args:
            return 'len()'
        return f"len({self.generate(args[0])})"
    
    def _gen_op(self, op, args):
        if len(args) < 2:
            return ''
        left = self.generate(args[0])
        right = self.generate(args[1])
        python_op = self.OP_MAP.get(op, op)
        return f"({left} {python_op} {right})"
    
    def _gen_func_call(self, verb, args):
        if not args:
            return f"{verb}()"
        args_str = ', '.join(self.generate(arg) for arg in args)
        return f"{verb}({args_str})"
    
    def _gen_if(self, node):
        cond = self.generate(node[1][0])
        then_branch = self.generate(node[1][1])
        else_branch = node[1][2]
        
        if else_branch:
            else_code = self.generate(else_branch)
            return f"({then_branch} if {cond} else {else_code})"
        else:
            return f"({then_branch} if {cond} else None)"
    
    def _gen_while(self, node):
        cond = self.generate(node[1][0])
        body = self.generate(node[1][1])
        return f"while {cond}:\n    {body}"
    
    def _gen_python(self, node):
        return node[1]
