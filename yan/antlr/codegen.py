#!/usr/bin/env python3
"""
言语言代码生成器
将 AST 转换为 Python 代码
"""

import sys
import os

# 添加父目录到路径，以便导入 nodes 和 runtime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict
from nodes import *
from runtime import ALL_BUILTINS as BUILTINS


class CodeGenError(Exception):
    pass


class PythonCodeGen:
    """Python 代码生成器"""

    def __init__(self):
        # 用户定义的函数/变量：名称 -> 元数
        self.user_defined: Dict[str, int] = {}

    def generate(self, node: Node) -> str:
        """生成 Python 代码"""
        if isinstance(node, Program):
            return self._gen_program(node)
        elif isinstance(node, Num):
            return repr(node.value)
        elif isinstance(node, Str):
            return repr(node.value)
        elif isinstance(node, Bool):
            return 'True' if node.value else 'False'
        elif isinstance(node, Nil):
            return 'None'
        elif isinstance(node, MathExpr):
            return f'({node.expr})'
        elif isinstance(node, PythonCode):
            return node.code
        elif isinstance(node, ListLiteral):
            return self._gen_list(node)
        elif isinstance(node, Word):
            return node.name
        elif isinstance(node, Call):
            return self._gen_call(node)
        elif isinstance(node, Pipeline):
            return self._gen_pipeline(node)
        elif isinstance(node, Quote):
            return self._gen_quote(node)
        elif isinstance(node, Define):
            return self._gen_define(node)
        elif isinstance(node, Lambda):
            return self._gen_lambda(node)
        elif isinstance(node, Block):
            return self._gen_block(node)
        elif isinstance(node, If):
            return self._gen_if(node)
        elif isinstance(node, ForEach):
            return self._gen_foreach(node)
        elif isinstance(node, While):
            return self._gen_while(node)
        else:
            raise CodeGenError(f"未知节点类型: {type(node)}")

    def _gen_program(self, node: Program) -> str:
        """生成程序"""
        lines = []
        for stmt in node.statements:
            code = self.generate(stmt)
            if code:
                lines.append(code)
        return '\n'.join(lines)

    def _gen_list(self, node: ListLiteral) -> str:
        """生成列表"""
        elements = ', '.join(self.generate(e) for e in node.elements)
        return f'[{elements}]'

    def _gen_call(self, node: Call, pipeline_arg: str = None) -> str:
        """生成函数调用"""
        verb_name = node.verb.name

        # 查找动词
        if verb_name in BUILTINS:
            py_func, arity = BUILTINS[verb_name]
            py_func_name = py_func.__name__ if hasattr(py_func, '__name__') else str(py_func)
        elif verb_name in self.user_defined:
            py_func_name = verb_name
            arity = self.user_defined[verb_name]
        else:
            # 假设是用户定义的函数
            py_func_name = verb_name
            arity = -1

        # 生成参数
        args = [self.generate(a) for a in node.args]

        # 如果有管道参数，插入到参数列表首位
        if pipeline_arg is not None:
            args.insert(0, pipeline_arg)

        # 如果没有参数且不是内置动词，可能是变量引用
        if len(args) == 0 and verb_name not in BUILTINS and pipeline_arg is None:
            return py_func_name

        # 柯里化：参数不足时生成 lambda
        if arity > 0 and len(args) < arity and pipeline_arg is None:
            missing = arity - len(args)
            new_params = [f'_p{i}' for i in range(missing)]
            all_args = new_params + args
            params = ', '.join(new_params)
            return f'(lambda {params}: {py_func_name}({", ".join(all_args)}))'

        # 正常调用
        return f'{py_func_name}({", ".join(args)})'

    def _gen_pipeline(self, node: Pipeline) -> str:
        """生成管道"""
        if len(node.steps) == 1:
            return self.generate(node.steps[0])

        # 第一步的结果作为后续步骤的输入
        result = self.generate(node.steps[0])

        for step in node.steps[1:]:
            if isinstance(step, Call):
                verb_name = step.verb.name

                # 查找动词信息
                if verb_name in BUILTINS:
                    py_func, arity = BUILTINS[verb_name]
                    py_func_name = py_func.__name__ if hasattr(py_func, '__name__') else str(py_func)
                elif verb_name in self.user_defined:
                    py_func_name = verb_name
                    arity = self.user_defined[verb_name]
                else:
                    py_func_name = verb_name
                    arity = -1

                # 生成参数
                args = [self.generate(a) for a in step.args]

                # 特殊处理高阶函数
                if verb_name in {'皆', '只', '归'}:
                    # 高阶函数：管道值作为最后一个参数
                    args.append(result)
                    result = f'{py_func_name}({", ".join(args)})'
                else:
                    # 普通动词：管道值作为第一个参数
                    args.insert(0, result)
                    result = f'{py_func_name}({", ".join(args)})'
            else:
                result = f'{self.generate(step)}({result})'

        return result

    def _gen_quote(self, node: Quote) -> str:
        """生成引用（返回 AST 的 Python 表示）"""
        ast_dict = self._ast_to_dict(node.expr)
        return repr(ast_dict)

    def _ast_to_dict(self, node: Node) -> dict:
        """将 AST 节点转为字典"""
        if isinstance(node, Num):
            return {'type': 'num', 'value': node.value}
        elif isinstance(node, Str):
            return {'type': 'str', 'value': node.value}
        elif isinstance(node, Bool):
            return {'type': 'bool', 'value': node.value}
        elif isinstance(node, Nil):
            return {'type': 'nil'}
        elif isinstance(node, Word):
            return {'type': 'word', 'name': node.name}
        elif isinstance(node, Call):
            return {
                'type': 'call',
                'verb': self._ast_to_dict(node.verb),
                'args': [self._ast_to_dict(a) for a in node.args]
            }
        elif isinstance(node, Pipeline):
            return {
                'type': 'pipeline',
                'steps': [self._ast_to_dict(s) for s in node.steps]
            }
        elif isinstance(node, Quote):
            return {'type': 'quote', 'expr': self._ast_to_dict(node.expr)}
        elif isinstance(node, Lambda):
            return {
                'type': 'lambda',
                'params': node.params,
                'body': self._ast_to_dict(node.body)
            }
        elif isinstance(node, If):
            return {
                'type': 'if',
                'cond': self._ast_to_dict(node.cond),
                'then': self._ast_to_dict(node.then_branch),
                'else': self._ast_to_dict(node.else_branch) if node.else_branch else None
            }
        else:
            return {'type': 'unknown'}

    def _gen_define(self, node: Define) -> str:
        """生成定义语句"""
        name = node.name

        # 记录用户定义的元数
        if isinstance(node.value, Lambda):
            self.user_defined[name] = len(node.value.params)
        else:
            self.user_defined[name] = -1

        # Python 代码块需要特殊处理
        if isinstance(node.value, PythonCode):
            code = node.value.code.strip()
            if '\n' in code:
                lines = code.split('\n')
                return f'''{code}
{name} = {lines[-1].strip()}'''
            else:
                return f'{name} = {code}'

        # Lambda with Block body: generate def function instead of lambda
        if isinstance(node.value, Lambda):
            # 检查是否需要生成 def 函数
            if isinstance(node.value.body, Block):
                return self._gen_def_function(name, node.value)
            # 检查 body 是否会生成多行代码（如 if-else 语句）
            body_code = self.generate(node.value.body)
            if '\n' in body_code:
                return self._gen_def_function_from_code(name, node.value.params, body_code)

        value = self.generate(node.value)
        return f'{name} = {value}'

    def _gen_def_function(self, name: str, node: Lambda) -> str:
        """Generate a def function for Lambda with Block body"""
        params = ', '.join(node.params) if node.params else '_'
        lines = []
        
        for i, stmt in enumerate(node.body.statements):
            code = self.generate(stmt)
            # 如果语句是多行的（如 if-else），需要特殊处理缩进
            if '\n' in code:
                # 多行语句，需要调整缩进
                code_lines = code.split('\n')
                for line in code_lines:
                    if line.strip():
                        lines.append(f'    {line}')
            else:
                # 最后一个语句作为返回值
                if i == len(node.body.statements) - 1:
                    lines.append(f'    return {code}')
                else:
                    lines.append(f'    {code}')
        
        body_code = '\n'.join(lines)
        return f'def {name}({params}):\n{body_code}'
    
    def _gen_def_function_from_code(self, name: str, params: list, body_code: str) -> str:
        """Generate a def function from generated body code"""
        params_str = ', '.join(params) if params else '_'
        
        # 调整缩进
        lines = []
        code_lines = body_code.split('\n')
        for line in code_lines:
            if line.strip():
                lines.append(f'    {line}')
        
        indented_body = '\n'.join(lines)
        return f'def {name}({params_str}):\n{indented_body}'

    def _gen_lambda(self, node: Lambda) -> str:
        """生成匿名函数"""
        params = ', '.join(node.params) if node.params else '_'
        
        # 如果函数体是 Block，需要特殊处理
        if isinstance(node.body, Block):
            lines = []
            for i, stmt in enumerate(node.body.statements):
                code = self.generate(stmt)
                # 如果语句是多行的（如 if-else），需要特殊处理缩进
                if '\n' in code:
                    # 多行语句，需要调整缩进
                    code_lines = code.split('\n')
                    indented_lines = []
                    for line in code_lines:
                        if line.strip():
                            indented_lines.append(f'    {line}')
                    code = '\n'.join(indented_lines)
                    lines.append(code)
                else:
                    # 最后一个语句作为返回值
                    if i == len(node.body.statements) - 1:
                        lines.append(f'    return {code}')
                    else:
                        lines.append(f'    {code}')
            body_code = '\n'.join(lines)
            return f'(lambda {params}:\n{body_code}\n)'
        
        body = self.generate(node.body)
        return f'(lambda {params}: {body})'

    def _gen_block(self, node: Block) -> str:
        """生成代码块"""
        lines = []
        for stmt in node.statements:
            lines.append(self.generate(stmt))
        return '\n'.join(lines)

    def _gen_if(self, node: If) -> str:
        """生成条件表达式"""
        cond = self.generate(node.cond)
        
        # 检查 then_branch 是否是 Block
        if isinstance(node.then_branch, Block):
            # 生成完整的 if-else 语句
            lines = []
            then_lines = []
            for stmt in node.then_branch.statements:
                code = self.generate(stmt)
                # 如果语句是多行的，需要为每一行添加缩进
                if '\n' in code:
                    code_lines = code.split('\n')
                    for line in code_lines:
                        if line.strip():
                            then_lines.append(f'    {line}')
                else:
                    then_lines.append(f'    {code}')
            lines.append(f'if {cond}:')
            lines.extend(then_lines)
            
            if node.else_branch:
                if isinstance(node.else_branch, Block):
                    lines.append('else:')
                    for stmt in node.else_branch.statements:
                        code = self.generate(stmt)
                        # 如果语句是多行的，需要为每一行添加缩进
                        if '\n' in code:
                            code_lines = code.split('\n')
                            for line in code_lines:
                                if line.strip():
                                    lines.append(f'    {line}')
                        else:
                            lines.append(f'    {code}')
                else:
                    else_code = self.generate(node.else_branch)
                    lines.append(f'else:')
                    lines.append(f'    {else_code}')
            
            return '\n'.join(lines)
        
        # 单行 then 分支
        then_code = self.generate(node.then_branch)
        
        # 检查 else_branch 是否是 Block
        if node.else_branch and isinstance(node.else_branch, Block):
            lines = []
            lines.append(f'if {cond}:')
            # 如果 then_code 是多行的，需要为每一行添加缩进
            if '\n' in then_code:
                code_lines = then_code.split('\n')
                for line in code_lines:
                    if line.strip():
                        lines.append(f'    {line}')
            else:
                lines.append(f'    {then_code}')
            lines.append('else:')
            for stmt in node.else_branch.statements:
                code = self.generate(stmt)
                # 如果语句是多行的，需要为每一行添加缩进
                if '\n' in code:
                    code_lines = code.split('\n')
                    for line in code_lines:
                        if line.strip():
                            lines.append(f'    {line}')
                else:
                    lines.append(f'    {code}')
            return '\n'.join(lines)
        
        # 简单的三元表达式
        if node.else_branch:
            else_code = self.generate(node.else_branch)
            return f'({then_code} if {cond} else {else_code})'
        else:
            return f'({then_code} if {cond} else None)'

    def _gen_foreach(self, node: ForEach) -> str:
        """生成遍历循环"""
        iterable = self.generate(node.iterable)
        var = node.var
        
        # 生成循环体
        if isinstance(node.body, Block):
            lines = []
            for i, stmt in enumerate(node.body.statements):
                code = self.generate(stmt)
                # 最后一个语句作为返回值（如果需要的话）
                if i == len(node.body.statements) - 1:
                    lines.append(f'    {code}')
                else:
                    lines.append(f'    {code}')
            body_code = '\n'.join(lines)
        else:
            body_code = f'    {self.generate(node.body)}'
        
        return f'for {var} in {iterable}:\n{body_code}'

    def _gen_while(self, node: While) -> str:
        """生成当循环"""
        cond = self.generate(node.cond)
        
        # 生成循环体
        if isinstance(node.body, Block):
            lines = []
            for stmt in node.body.statements:
                code = self.generate(stmt)
                lines.append(f'    {code}')
            body_code = '\n'.join(lines)
        else:
            body_code = f'    {self.generate(node.body)}'
        
        return f'while {cond}:\n{body_code}'
