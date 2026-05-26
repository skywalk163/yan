"""
言语言 Python 代码生成器
"""

from typing import Dict, Tuple, Any, Optional
from nodes import *
from runtime import ALL_BUILTINS as BUILTINS

# 导入新模块节点类
try:
    from module_system import ImportNode, ExportNode
except ImportError:
    ImportNode = None
    ExportNode = None

# 导入优化器模块
try:
    from optimizer import ASTOptimizer, OptimizerConfig
except ImportError:
    # 如果优化器模块不可用，使用内置的简化版本
    ASTOptimizer = None
    OptimizerConfig = None


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
            return node.code.strip()
        elif isinstance(node, Continue):
            return 'continue'
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
        elif isinstance(node, Import):
            return self._gen_import(node)
        elif isinstance(node, Export):
            return self._gen_export(node)
        elif ImportNode and isinstance(node, ImportNode):
            return self._gen_import_node(node)
        elif ExportNode and isinstance(node, ExportNode):
            return self._gen_export_node(node)
        elif isinstance(node, StructDef):
            return self._gen_struct_def(node)
        elif isinstance(node, StructInit):
            return self._gen_struct_init(node)
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

        # 处理成员访问：obj.attr -> obj.attr
        if verb_name == '.':
            if len(node.args) >= 2:
                obj = self.generate(node.args[0])
                attr = self.generate(node.args[1])
                # 如果是 Word，直接用点访问；否则需要特殊处理
                if isinstance(node.args[1], Word):
                    return f'{obj}.{attr}'
                else:
                    return f'{obj}[{attr}]'
            return verb_name

        # 处理返回语句：返回 value -> return value
        if verb_name == '返回':
            if node.args:
                return f'return {self.generate(node.args[0])}'
            return 'return None'

        # 查找动词：用户定义优先于内置函数
        if verb_name in self.user_defined:
            py_func_name = verb_name
            arity = self.user_defined[verb_name]
        elif verb_name in BUILTINS:
            py_func, arity = BUILTINS[verb_name]
            py_func_name = py_func.__name__ if hasattr(py_func, '__name__') else str(py_func)
        else:
            # 假设是用户定义的函数
            py_func_name = verb_name
            arity = -1

        # 生成参数
        args = [self.generate(a) for a in node.args]

        # 只(列表, 谓词) -> _filter(谓词, 列表) 参数交换
        if verb_name == '只' and len(args) == 2:
            args = [args[1], args[0]]

        # 如果有管道参数，插入到参数列表首位
        if pipeline_arg is not None:
            args.insert(0, pipeline_arg)

        # 如果没有参数且不是动词，可能是变量引用
        if len(args) == 0 and verb_name not in BUILTINS and verb_name not in self.user_defined and pipeline_arg is None:
            return py_func_name

        # 对于 Python 代码块（arity=-1）且无参数调用，按变量引用处理
        if len(args) == 0 and verb_name in self.user_defined and self.user_defined[verb_name] == -1 and pipeline_arg is None:
            return py_func_name

        # 可变参数动词（arity=-1）：直接调用，不柯里化
        if arity == -1:
            return f'{py_func_name}({", ".join(args)})'

        # 柯里化：参数不足时生成 lambda
        # 规则：已有参数绑定到右侧，管道值（或新生成的参数）绑定到左侧
        if arity > 0 and len(args) < arity and pipeline_arg is None:
            missing = arity - len(args)
            # 新参数在左侧，已有参数在右侧
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
                if verb_name == '皆':
                    # 皆(func, lst) - 管道值是 lst
                    # 如果有多个参数，第一个是动词，其余是柯里化参数
                    if len(args) == 1:
                        result = f'{py_func_name}({args[0]}, {result})'
                    elif len(args) >= 2 and isinstance(step.args[0], Word):
                        # 柯里化：乘2 -> lambda x: _mul(x, 2)
                        inner_verb = step.args[0].name
                        if inner_verb in BUILTINS:
                            inner_py_func, _ = BUILTINS[inner_verb]
                            inner_func_name = inner_py_func.__name__ if hasattr(inner_py_func, '__name__') else str(inner_py_func)
                            curried_args = ', '.join(args[1:])
                            result = f'{py_func_name}((lambda _x: {inner_func_name}(_x, {curried_args})), {result})'
                        else:
                            result = f'{py_func_name}({args[0]}, {", ".join(args[1:])}, {result})'
                    else:
                        result = f'{py_func_name}({", ".join(args)}, {result})'
                elif verb_name == '只':
                    # 只(pred, lst) - 管道值是 lst
                    if len(args) == 1:
                        result = f'{py_func_name}({args[0]}, {result})'
                    elif len(args) >= 2 and isinstance(step.args[0], Word):
                        # 柯里化：大2 -> lambda x: _gt(x, 2)
                        inner_verb = step.args[0].name
                        if inner_verb in BUILTINS:
                            inner_py_func, _ = BUILTINS[inner_verb]
                            inner_func_name = inner_py_func.__name__ if hasattr(inner_py_func, '__name__') else str(inner_py_func)
                            curried_args = ', '.join(args[1:])
                            result = f'{py_func_name}((lambda _x: {inner_func_name}(_x, {curried_args})), {result})'
                        else:
                            result = f'{py_func_name}({args[0]}, {", ".join(args[1:])}, {result})'
                    else:
                        result = f'{py_func_name}({", ".join(args)}, {result})'
                elif verb_name == '归':
                    # 归(func, init, lst) - 管道值是 lst
                    # args[0] 可能是柯里化的函数，需要提取原始函数
                    if len(step.args) >= 1:
                        # 检查 args[0] 是否是 Call（副词吞噬的动词调用）
                        if isinstance(step.args[0], Call):
                            inner_verb = step.args[0].verb.name
                            if inner_verb in BUILTINS:
                                inner_py_func, _ = BUILTINS[inner_verb]
                                inner_func_name = inner_py_func.__name__ if hasattr(inner_py_func, '__name__') else str(inner_py_func)
                                # 使用原始函数名
                                # init 从 step.args[1] 获取，而不是从 args 获取
                                init_val = self.generate(step.args[1]) if len(step.args) > 1 else '0'
                                result = f'_reduce({inner_func_name}, {init_val}, {result})'
                            else:
                                result = f'{py_func_name}({args[0]}, {", ".join(args[1:])}, {result})'
                        # 检查 args[0] 是否是 Word（动词引用）
                        elif isinstance(step.args[0], Word):
                            inner_verb = step.args[0].name
                            if inner_verb in BUILTINS:
                                inner_py_func, _ = BUILTINS[inner_verb]
                                inner_func_name = inner_py_func.__name__ if hasattr(inner_py_func, '__name__') else str(inner_py_func)
                                init_val = self.generate(step.args[1]) if len(step.args) > 1 else '0'
                                result = f'_reduce({inner_func_name}, {init_val}, {result})'
                            else:
                                result = f'{py_func_name}({args[0]}, {", ".join(args[1:])}, {result})'
                        else:
                            result = f'{py_func_name}({", ".join(args)}, {result})'
                    else:
                        result = f'{py_func_name}({result})'
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
            # 如果是多行代码，最后一行应该是返回值的表达式
            if '\n' in code:
                lines = code.split('\n')
                # 最后一行作为返回值
                return f'''{code}
{name} = {lines[-1].strip()}'''
            else:
                return f'{name} = {code}'

        # Lambda with Block body: generate def function instead of lambda
        if isinstance(node.value, Lambda):
            # 检查是否是尾递归函数，需要特殊处理
            if hasattr(node.value, 'is_tail_recursive') and node.value.is_tail_recursive:
                return self._gen_tail_recursive_function(name, node.value)
            # 检查是否需要生成 def 函数
            if isinstance(node.value.body, Block):
                return self._gen_def_function(name, node.value)
            # 检查 body 是否会生成多行代码（如 if-else 语句）
            # 先生成代码，然后检查是否是多行
            body_code = self.generate(node.value.body)
            if '\n' in body_code:
                return self._gen_def_function_from_code(name, node.value.params, body_code)

        value = self.generate(node.value)
        return f'{name} = {value}'

    def _gen_tail_recursive_function(self, name: str, node: Lambda) -> str:
        """生成尾递归优化的函数（转换为循环）"""
        params_list = node.params
        params_str = ', '.join(params_list) if params_list else '_'
        
        # 生成循环体
        loop_body = self._convert_tail_recursion_to_loop(node.body, name, params_list)
        
        return f'''def {name}({params_str}):
    while True:
{loop_body}'''

    def _convert_tail_recursion_to_loop(self, node: Node, func_name: str, params: list) -> str:
        """将尾递归转换为循环体"""
        if isinstance(node, Call) and node.verb.name == func_name:
            # 尾递归调用，转换为参数更新和 continue
            updates = []
            for i in range(min(len(node.args), len(params))):
                arg_code = self.generate(node.args[i])
                updates.append(f'{params[i]} = {arg_code}')
            indented_updates = '\n'.join(f'        {u}' for u in updates)
            return f'{indented_updates}\n        continue'
        elif isinstance(node, If):
            # 条件语句
            cond = self.generate(node.cond)
            then_body = self._convert_tail_recursion_to_loop(node.then_branch, func_name, params)
            else_body = ''
            if node.else_branch:
                else_code = self._convert_tail_recursion_to_loop(node.else_branch, func_name, params)
                else_body = f'\n        else:\n{else_code}'
            return f'        if {cond}:\n{then_body}{else_body}'
        elif isinstance(node, Block):
            lines = []
            for i, stmt in enumerate(node.statements):
                if i == len(node.statements) - 1:
                    lines.append(self._convert_tail_recursion_to_loop(stmt, func_name, params))
                else:
                    code = self.generate(stmt)
                    indented_lines = [f'        {l}' for l in code.split('\n') if l.strip()]
                    lines.extend(indented_lines)
            return '\n'.join(lines)
        else:
            # 基例，返回值
            return f'        return {self.generate(node)}'

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
                if i == len(node.body.statements) - 1:
                    # 最后一个语句，检查是否已经是 return 语句
                    if code.startswith('return '):
                        # 如果已经是 return，不再添加 return
                        lines.append(f'    {code}')
                    else:
                        # 否则添加 return
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
        # 处理 varargs
        if node.varargs:
            if node.params:
                params = ', '.join(node.params) + ', *args'
            else:
                params = '*args'
        else:
            params = ', '.join(node.params) if node.params else '_'
        
        # 如果函数体是 Block，需要特殊处理
        if isinstance(node.body, Block):
            lines = []
            for i, stmt in enumerate(node.body.statements):
                code = self.generate(stmt)
                if '\n' in code:
                    code_lines = code.split('\n')
                    for line in code_lines:
                        if line.strip():
                            lines.append(f'    {line}')
                else:
                    if i == len(node.body.statements) - 1:
                        lines.append(f'    return {code}')
                    else:
                        lines.append(f'    {code}')
            body_code = '\n'.join(lines)
            # Lambda 不支持多行代码，使用 def 代替
            return f'__temp_func_{id(node)}\n# 不支持的 Lambda 块，使用 def\n# 实际代码将生成到 _gen_define'
        
        body = self.generate(node.body)
        return f'(lambda {params}: {body})'

    def _gen_block(self, node: Block) -> str:
        """生成代码块"""
        lines = []
        for stmt in node.statements:
            code = self.generate(stmt)
            # 处理多行代码
            code_lines = code.split('\n')
            lines.extend(code_lines)
        return '\n'.join(lines)

    def _gen_if(self, node: If) -> str:
        """生成条件表达式"""
        cond = self.generate(node.cond)
        
        # 检查 then_branch 是否是 Block
        if isinstance(node.then_branch, Block):
            lines = []
            then_lines = []
            for i, stmt in enumerate(node.then_branch.statements):
                code = self.generate(stmt)
                is_last = (i == len(node.then_branch.statements) - 1)
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
                    for i, stmt in enumerate(node.else_branch.statements):
                        code = self.generate(stmt)
                        is_last = (i == len(node.else_branch.statements) - 1)
                        if '\n' in code:
                            code_lines = code.split('\n')
                            for line in code_lines:
                                if line.strip():
                                    lines.append(f'    {line}')
                        else:
                            lines.append(f'    {code}')
                else:
                    else_code = self.generate(node.else_branch)
                    lines.append('else:')
                    lines.append(f'    {else_code}')
            
            return '\n'.join(lines)
        
        # 单行 then 分支，else 是 Block
        then_code = self.generate(node.then_branch)
        
        if node.else_branch and isinstance(node.else_branch, Block):
            lines = []
            lines.append(f'if {cond}:')
            lines.append(f'    return {then_code}')
            lines.append('else:')
            for i, stmt in enumerate(node.else_branch.statements):
                code = self.generate(stmt)
                is_last = (i == len(node.else_branch.statements) - 1)
                if '\n' in code:
                    code_lines = code.split('\n')
                    for line in code_lines:
                        if line.strip():
                            lines.append(f'    {line}')
                elif is_last:
                    lines.append(f'    return {code}')
                else:
                    lines.append(f'    {code}')
            return '\n'.join(lines)
        
        # 简单的三元表达式
        then_code = self.generate(node.then_branch)
        
        # 如果 then_code 是 return 语句，不能作为三元表达式
        # 需要转换为 if 语句
        if then_code.startswith('return '):
            lines = []
            lines.append(f'if {cond}:')
            lines.append(f'    {then_code}')
            if node.else_branch:
                else_code = self.generate(node.else_branch)
                lines.append('else:')
                lines.append(f'    {else_code}')
            return '\n'.join(lines)
        
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
            for stmt in node.body.statements:
                code = self.generate(stmt)
                # 处理多行代码，每行都需要缩进
                code_lines = code.split('\n')
                for line in code_lines:
                    lines.append(f'    {line}')
            body_code = '\n'.join(lines)
        else:
            code = self.generate(node.body)
            # 处理多行代码，每行都需要缩进
            code_lines = code.split('\n')
            indented_lines = [f'    {line}' for line in code_lines]
            body_code = '\n'.join(indented_lines)
        
        return f'for {var} in {iterable}:\n{body_code}'

    def _gen_while(self, node: While) -> str:
        """生成当循环"""
        cond = self.generate(node.cond)
        
        # 生成循环体
        if isinstance(node.body, Block):
            lines = []
            for stmt in node.body.statements:
                code = self.generate(stmt)
                # 处理多行代码，每行都需要缩进
                code_lines = code.split('\n')
                for line in code_lines:
                    lines.append(f'    {line}')
            body_code = '\n'.join(lines)
        else:
            code = self.generate(node.body)
            # 处理多行代码，每行都需要缩进
            code_lines = code.split('\n')
            indented_lines = [f'    {line}' for line in code_lines]
            body_code = '\n'.join(indented_lines)
        
        return f'while {cond}:\n{body_code}'
    
    def _gen_import(self, node: Import) -> str:
        """生成导入语句的 Python 代码"""
        if node.names:
            # 导入特定名称：from module import name1, name2
            names_str = ', '.join(node.names)
            return f'from {node.module_name} import {names_str}'
        else:
            # 导入整个模块
            return f'import {node.module_name}'
    
    def _gen_export(self, node: Export) -> str:
        """生成导出语句的 Python 代码"""
        # Python 使用 __all__ 来控制导出
        names_str = ', '.join(f"'{name}'" for name in node.names)
        return f'__all__ = [{names_str}]'
    
    def _gen_import_node(self, node: 'ImportNode') -> str:
        """生成 ImportNode 节点的 Python 代码生成"""
        # 处理不同的导入语法
        module_name = node.path
        
        # 如果是相对路径，转换为模块名
        if module_name.startswith('./') or module_name.startswith('../'):
            # 简化处理：使用文件名 -> 文件名
            module_name = module_name.replace('/', '.').replace('\\', '.')
            if module_name.endswith('.yan'):
                module_name = module_name[:-4]
        
        if node.selective:
            # 选择性导入：取 name1, name2
            names_str = ', '.join(node.selective)
            if node.alias:
                # 选择性导入 + 别名
                return f'from {module_name} import {names_str} as {node.alias}'
            else:
                return f'from {module_name} import {names_str}'
        elif node.alias:
            # 别名导入
            return f'import {module_name} as {node.alias}'
        else:
            # 普通导入
            return f'import {module_name}'
    
    def _gen_export_node(self, node: 'ExportNode') -> str:
        """生成 ExportNode 节点的 Python 代码生成"""
        lines = []
        
        # 先生成内部的定义
        for defn in node.definitions:
            if hasattr(defn, 'name'):
                code = self.generate(defn)
                lines.append(code)
        
        # 然后添加 __all__ 导出列表
        if node.names:
            names_str = ', '.join(f"'{name}'" for name in node.names)
            lines.append(f'__all__ = [{names_str}]')
        
        return '\n'.join(lines)
    
    def _gen_struct_def(self, node: StructDef) -> str:
        """生成结构体定义的 Python 代码"""
        lines = [f'class {node.name}:']
        
        if node.fields:
            # 生成 __init__ 方法
            params = ', '.join(f'{name}=None' for name, _ in node.fields)
            lines.append(f'    def __init__(self, {params}):')
            for name, _ in node.fields:
                lines.append(f'        self.{name} = {name}')
        else:
            lines.append('    pass')
        
        return '\n'.join(lines)
    
    def _gen_struct_init(self, node: StructInit) -> str:
        """生成结构体实例化的 Python 代码"""
        args = ', '.join(f'{name}={self.generate(value)}' 
                        for name, value in node.field_values.items())
        return f'{node.struct_name}({args})'


# 扩展 PythonCodeGen 以支持优化
class OptimizedPythonCodeGen(PythonCodeGen):
    """带优化的 Python 代码生成器"""

    def __init__(self, config: Optional[OptimizerConfig] = None):
        super().__init__()
        if ASTOptimizer is not None:
            self.optimizer = ASTOptimizer(config)
            self._optimizations_enabled = True
        else:
            # 如果优化器模块不可用，设置空优化器
            self.optimizer = None
            self._optimizations_enabled = False

    def generate(self, node: Node) -> str:
        """生成优化后的 Python 代码"""
        if self._optimizations_enabled and self.optimizer:
            optimized_node = self.optimizer.optimize(node)
            return super().generate(optimized_node)
        else:
            return super().generate(node)

    def get_optimization_stats(self) -> dict:
        """获取优化统计信息"""
        if self._optimizations_enabled and self.optimizer:
            return {
                'optimizations_count': self.optimizer.optimized_count,
                'config': {
                    'constant_folding': self.optimizer.config.constant_folding,
                    'dead_code_elimination': self.optimizer.config.dead_code_elimination,
                    'expression_simplification': self.optimizer.config.expression_simplification,
                    'tail_recursion_optimization': self.optimizer.config.tail_recursion_optimization,
                    'level': self.optimizer.config.optimization_level
                }
            }
        else:
            return {
                'optimizations_count': 0,
                'config': {
                    'error': 'Optimizer module not available'
                }
            }
