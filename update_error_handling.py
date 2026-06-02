import re

def update_error_handling():
    content = '''
    def _generate_node(self, node: ASTNode) -> str:
        try:
            if isinstance(node, Program):
                return self._generate_program(node)
            elif isinstance(node, Statement):
                return self._generate_statement(node)
            elif isinstance(node, Expression):
                return self._generate_expression(node)
            elif isinstance(node, Number):
                return self._generate_number(node)
            elif isinstance(node, StringLiteral):
                return self._generate_literal(node)
            elif isinstance(node, Boolean):
                return self._generate_boolean(node)
            elif isinstance(node, NoneLiteral):
                return 'None'
            elif isinstance(node, Identifier):
                return self._generate_identifier(node)
            elif isinstance(node, BinaryOp):
                return self._generate_binary_op(node)
            elif isinstance(node, UnaryOp):
                return self._generate_unary_op(node)
            elif isinstance(node, FunctionCall):
                return self._generate_function_call(node)
            elif isinstance(node, AttributeAccess):
                return self._generate_attribute_access(node)
            elif isinstance(node, ListLiteral):
                return self._generate_list(node)
            elif isinstance(node, DictLiteral):
                return self._generate_dict(node)
            elif isinstance(node, TupleLiteral):
                return self._generate_tuple(node)
            elif isinstance(node, IfExpression):
                return self._generate_if_expression(node)
            elif isinstance(node, ForLoop):
                return self._generate_for_loop(node)
            elif isinstance(node, WhileLoop):
                return self._generate_while_loop(node)
            elif isinstance(node, Assignment):
                return self._generate_assignment(node)
            elif isinstance(node, VariableDeclaration):
                return self._generate_variable_declaration(node)
            elif isinstance(node, FunctionDefinition):
                return self._generate_function_definition(node)
            elif isinstance(node, ClassDefinition):
                return self._generate_class_definition(node)
            elif isinstance(node, ReturnStatement):
                return self._generate_return(node)
            elif isinstance(node, BreakStatement):
                return 'break'
            elif isinstance(node, ContinueStatement):
                return 'continue'
            elif isinstance(node, TryExcept):
                return self._generate_try_except(node)
            elif isinstance(node, ImportStatement):
                return self._generate_import(node)
            elif isinstance(node, Lambda):
                return self._generate_lambda(node)
            elif isinstance(node, Ternary):
                return self._generate_ternary(node)
            elif isinstance(node, ListComprehension):
                return self._generate_list_comprehension(node)
            else:
                raise NotImplementedError(f"未知的AST节点类型: {type(node).__name__}")
        except Exception as e:
            raise CodeGenError(f"代码生成错误: {e}", node)

    def _generate_identifier(self, node: Identifier) -> str:
        name = node.name
        
        if name in self.builtin_map:
            return self.builtin_map[name]
        
        if name in self.STANDARD_MODULES:
            return name
        
        if re.match(r'^[\u4e00-\u9fa5]+$', name):
            return f'__{name}'
        
        return name
'''

    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/codegen.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    old_method = '''    def _generate_node(self, node: ASTNode) -> str:
        if isinstance(node, Program):
            return self._generate_program(node)
        elif isinstance(node, Statement):
            return self._generate_statement(node)
        elif isinstance(node, Expression):
            return self._generate_expression(node)
        elif isinstance(node, Number):
            return self._generate_number(node)
        elif isinstance(node, StringLiteral):
            return self._generate_literal(node)
        elif isinstance(node, Boolean):
            return self._generate_boolean(node)
        elif isinstance(node, NoneLiteral):
            return 'None'
        elif isinstance(node, Identifier):
            return self._generate_identifier(node)
        elif isinstance(node, BinaryOp):
            return self._generate_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self._generate_unary_op(node)
        elif isinstance(node, FunctionCall):
            return self._generate_function_call(node)
        elif isinstance(node, AttributeAccess):
            return self._generate_attribute_access(node)
        elif isinstance(node, ListLiteral):
            return self._generate_list(node)
        elif isinstance(node, DictLiteral):
            return self._generate_dict(node)
        elif isinstance(node, TupleLiteral):
            return self._generate_tuple(node)
        elif isinstance(node, IfExpression):
            return self._generate_if_expression(node)
        elif isinstance(node, ForLoop):
            return self._generate_for_loop(node)
        elif isinstance(node, WhileLoop):
            return self._generate_while_loop(node)
        elif isinstance(node, Assignment):
            return self._generate_assignment(node)
        elif isinstance(node, VariableDeclaration):
            return self._generate_variable_declaration(node)
        elif isinstance(node, FunctionDefinition):
            return self._generate_function_definition(node)
        elif isinstance(node, ClassDefinition):
            return self._generate_class_definition(node)
        elif isinstance(node, ReturnStatement):
            return self._generate_return(node)
        elif isinstance(node, BreakStatement):
            return 'break'
        elif isinstance(node, ContinueStatement):
            return 'continue'
        elif isinstance(node, TryExcept):
            return self._generate_try_except(node)
        elif isinstance(node, ImportStatement):
            return self._generate_import(node)
        elif isinstance(node, Lambda):
            return self._generate_lambda(node)
        elif isinstance(node, Ternary):
            return self._generate_ternary(node)
        elif isinstance(node, ListComprehension):
            return self._generate_list_comprehension(node)
        else:
            raise NotImplementedError(f"未知的AST节点类型: {type(node).__name__}")'''

    code = code.replace(old_method, content)
    code = code.replace('raise NotImplementedError(f"未知的AST节点类型:', 'raise CodeGenError(f"未知的AST节点类型:')

    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/codegen.py', 'w', encoding='utf-8') as f:
        f.write(code)
    
    print("代码生成器错误处理优化完成")

if __name__ == "__main__":
    update_error_handling()
