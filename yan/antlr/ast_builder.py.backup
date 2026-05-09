#!/usr/bin/env python3
"""
ANTLR AST 构建器
将 ANTLR 解析树转换为言语言 AST 节点
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generated.YanVisitor import YanVisitor
from generated.YanParser import YanParser
from nodes import *


class ASTBuilder(YanVisitor):
    """将 ANTLR 解析树转换为 AST"""
    
    def __init__(self):
        self.user_verbs = set()
    
    # ============ 程序和语句 ============
    
    def visitProgram(self, ctx: YanParser.ProgramContext):
        statements = []
        for stmt_ctx in ctx.statement():
            stmt = self.visit(stmt_ctx)
            if stmt:
                statements.append(stmt)
        return Program(statements)
    
    def visitStatement(self, ctx: YanParser.StatementContext):
        if ctx.defineStmt():
            return self.visit(ctx.defineStmt())
        elif ctx.exprStmt():
            return self.visit(ctx.exprStmt())
        elif ctx.DOT() or ctx.SEMI():
            return None
        return None
    
    # ============ 定义语句 ============
    
    def visitDefineWithKeyword(self, ctx: YanParser.DefineWithKeywordContext):
        name = ctx.ID().getText()
        if name.startswith('定') and len(name) > 1:
            name = name[1:]
        value = self.visit(ctx.value())
        if isinstance(value, Lambda):
            self.user_verbs.add(name)
        return Define(name, value)
    
    def visitDefineWithoutKeyword(self, ctx: YanParser.DefineWithoutKeywordContext):
        name = ctx.ID().getText()
        if name.startswith('定') and len(name) > 1:
            name = name[1:]
        value = self.visit(ctx.value())
        if isinstance(value, Lambda):
            self.user_verbs.add(name)
        return Define(name, value)
    
    def visitDefineWithDengyu(self, ctx: YanParser.DefineWithDengyuContext):
        name = ctx.ID().getText()
        value = self.visit(ctx.value())
        if isinstance(value, Lambda):
            self.user_verbs.add(name)
        return Define(name, value)
    
    # ============ Lambda 表达式 ============
    
    def visitLambdaWithBlock(self, ctx: YanParser.LambdaWithBlockContext):
        params = [id_node.getText() for id_node in ctx.ID()] if ctx.ID() else []
        if params and params[0].startswith('函') and len(params[0]) > 1:
            params[0] = params[0][1:]
        body = self.visit(ctx.block())
        return Lambda(params, body)
    
    def visitLambdaWithExpr(self, ctx: YanParser.LambdaWithExprContext):
        params = [id_node.getText() for id_node in ctx.ID()] if ctx.ID() else []
        if params and params[0].startswith('函') and len(params[0]) > 1:
            params[0] = params[0][1:]
        body = self.visit(ctx.expression())
        return Lambda(params, body)
    
    def visitLambdaIdWithBlock(self, ctx: YanParser.LambdaIdWithBlockContext):
        ids = [id_node.getText() for id_node in ctx.ID()]
        if ids and ids[0].startswith('函'):
            first_id = ids[0]
            params = [first_id[1:]] if len(first_id) > 1 else []
            params.extend(ids[1:])
        else:
            raise SyntaxError(f"Lambda 表达式必须以'函'开头，但得到: {ids[0] if ids else '空'}")
        body = self.visit(ctx.block())
        return Lambda(params, body)
    
    def visitLambdaIdWithExpr(self, ctx: YanParser.LambdaIdWithExprContext):
        ids = [id_node.getText() for id_node in ctx.ID()]
        if ids and ids[0].startswith('函'):
            first_id = ids[0]
            params = [first_id[1:]] if len(first_id) > 1 else []
            params.extend(ids[1:])
        else:
            raise SyntaxError(f"Lambda 表达式必须以'函'开头，但得到: {ids[0] if ids else '空'}")
        body = self.visit(ctx.expression())
        return Lambda(params, body)
    
    # ============ 代码块 ============
    
    def visitBlock(self, ctx: YanParser.BlockContext):
        statements = []
        for stmt_ctx in ctx.statement():
            stmt = self.visit(stmt_ctx)
            if stmt:
                statements.append(stmt)
        if len(statements) == 0:
            return Nil()
        elif len(statements) == 1:
            return statements[0]
        else:
            return Block(statements)
    
    # ============ 表达式 ============
    
    def visitExprStmt(self, ctx: YanParser.ExprStmtContext):
        return self.visit(ctx.expression())
    
    def visitIfExpr(self, ctx: YanParser.IfExprContext):
        cond = self.visit(ctx.expr())
        then_branch = self.visit(ctx.thenBranch())
        else_branch = self.visit(ctx.elseBranch()) if ctx.elseBranch() else None
        return If(cond, then_branch, else_branch)
    
    def visitThenBranch(self, ctx: YanParser.ThenBranchContext):
        if ctx.block():
            return self.visit(ctx.block())
        return self.visit(ctx.expr())
    
    def visitElseBranch(self, ctx: YanParser.ElseBranchContext):
        if ctx.block():
            return self.visit(ctx.block())
        return self.visit(ctx.expr())
    
    def visitForeachExpr(self, ctx: YanParser.ForeachExprContext):
        var = ctx.ID().getText()
        iterable = self.visit(ctx.expr())
        body = self.visit(ctx.block())
        return ForEach(var, iterable, body)
    
    def visitWhileExpr(self, ctx: YanParser.WhileExprContext):
        cond = self.visit(ctx.expr())
        body = self.visit(ctx.block())
        return While(cond, body)
    
    def visitPipelineExpr(self, ctx: YanParser.PipelineExprContext):
        terms = [self.visit(term) for term in ctx.pipeline().expr()]
        if len(terms) == 1:
            return terms[0]
        else:
            return Pipeline(terms)
    
    # ============ 表达式类型 ============
    
    def visitVerbCallExpr(self, ctx: YanParser.VerbCallExprContext):
        return self.visit(ctx.verbCall())
    
    def visitInfixExprAlt(self, ctx: YanParser.InfixExprAltContext):
        return self.visit(ctx.infixExpr())
    
    # ============ 动词调用 ============
    
    def visitVerbCall(self, ctx: YanParser.VerbCallContext):
        # 获取动词名
        for attr in ['PRINT', 'ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'POW', 'ABS', 'NEG', 
                     'GT', 'LT', 'EQ', 'NE', 'AND', 'OR', 'NOT', 'HEAD', 'TAIL', 
                     'APPEND', 'LEN', 'CONCAT', 'CONTAINS', 'MAP', 'FILTER', 'REDUCE']:
            token = getattr(ctx, attr)()
            if token:
                verb_name = token.getText()
                break
        else:
            verb_name = ctx.getText()
        
        verb = Word(verb_name)
        
        # 收集参数
        args = []
        if ctx.expr():
            for expr_ctx in ctx.expr():
                args.append(self.visit(expr_ctx))
        
        return Call(verb, args)
    
    # ============ 中缀表达式 ============
    
    def visitInfixExpr(self, ctx: YanParser.InfixExprContext):
        left = self.visit(ctx.atom())
        
        # 处理中缀操作符
        children = list(ctx.getChildren())
        i = 1
        while i < len(children):
            op_token = children[i]
            op_name = op_token.getText()
            i += 1
            right_ctx = children[i]
            right = self.visit(right_ctx)
            verb = Word(op_name)
            left = Call(verb, [left, right])
            i += 1
        
        return left
    
    # ============ 原子值 ============
    
    def visitNumberAtom(self, ctx: YanParser.NumberAtomContext):
        text = ctx.NUMBER().getText()
        if '.' in text:
            return Num(float(text))
        else:
            return Num(int(text))
    
    def visitStringAtom(self, ctx: YanParser.StringAtomContext):
        text = ctx.STRING().getText()
        return Str(text[1:-1])
    
    def visitTrueAtom(self, ctx: YanParser.TrueAtomContext):
        return Bool(True)
    
    def visitFalseAtom(self, ctx: YanParser.FalseAtomContext):
        return Bool(False)
    
    def visitNilAtom(self, ctx: YanParser.NilAtomContext):
        return Nil()
    
    def visitMathAtom(self, ctx: YanParser.MathAtomContext):
        text = ctx.MATH().getText()
        return MathExpr(text[2:-1])
    
    def visitPythonAtom
