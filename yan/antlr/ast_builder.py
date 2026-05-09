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

# 关键字列表（按优先级排序，双字关键字优先）
KEYWORDS = {
    '函': 'FUNC',
    '定': 'DEFINE',
    '等于': 'DENGYU',
    '若': 'IF',
    '则': 'THEN',
    '否则': 'ELSE',
    '遍历': 'FOREACH',
    '于': 'IN',
    '当': 'WHILE',
    '真': 'TRUE',
    '假': 'FALSE',
    '空': 'NIL',
    '加': 'ADD',
    '减': 'SUB',
    '乘': 'MUL',
    '除': 'DIV',
    '模': 'MOD',
    '幂': 'POW',
    '大': 'GT',
    '小': 'LT',
    '等': 'EQ',
    '不等': 'NE',
    '且': 'AND',
    '或': 'OR',
    '印': 'PRINT',
    '绝对': 'ABS',
    '负': 'NEG',
    '非': 'NOT',
    '首': 'HEAD',
    '余': 'TAIL',
    '入': 'APPEND',
    '长': 'LEN',
    '连': 'CONCAT',
    '含': 'CONTAINS',
    '皆': 'MAP',
    '只': 'FILTER',
    '归': 'REDUCE',
}

def split_id(id_text):
    """拆分包含关键字的 ID"""
    result = []
    i = 0

    while i < len(id_text):
        matched = False

        for keyword in sorted(KEYWORDS.keys(), key=len, reverse=True):
            if id_text[i:i+len(keyword)] == keyword:
                if result and result[-1][0] == 'ID':
                    result.append((KEYWORDS[keyword], keyword))
                else:
                    result.append((KEYWORDS[keyword], keyword))
                i += len(keyword)
                matched = True
                break

        if not matched:
            if result and result[-1][0] == 'ID':
                result[-1] = ('ID', result[-1][1] + id_text[i])
            else:
                result.append(('ID', id_text[i]))
            i += 1

    return result



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
        
        # 如果 left 是 Word，检查是否包含中缀动词
        if isinstance(left, Word):
            name = left.name
            infix_verbs = ['加', '减', '乘', '除', '模', '幂', '绝对', '负',
                          '大', '小', '等', '不等', '且', '或', '非',
                          '首', '余', '入', '长', '连', '含',
                          '皆', '只', '归']
            
            for verb in infix_verbs:
                if verb in name and not name.startswith(verb):
                    # 找到动词的位置
                    pos = name.find(verb)
                    left_part = name[:pos]
                    right_part = name[pos + len(verb):]
                    
                    # 创建中缀调用
                    verb_node = Word(verb)
                    left_node = Word(left_part)
                    
                    if right_part:
                        # 有右操作数
                        right_node = Word(right_part)
                        left = Call(verb_node, [left_node, right_node])
                    else:
                        # 没有右操作数（柯里化）
                        left = Call(verb_node, [left_node])
                    break
        
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
    
    def visitPythonAtom(self, ctx: YanParser.PythonAtomContext):
        text = ctx.PYTHON().getText()
        return PythonCode(text[2:-2])
    
    def visitQuoteAtom(self, ctx: YanParser.QuoteAtomContext):
        expr = self.visit(ctx.expr())
        return Quote(expr)
    
    def visitIdAtom(self, ctx: YanParser.IdAtomContext):
        name = ctx.ID().getText()

        # 检查是否以动词开头（前缀动词）
        verbs = ['印', '加', '减', '乘', '除', '模', '幂', '绝对', '负',
                 '大', '小', '等', '不等', '且', '或', '非',
                 '首', '余', '入', '长', '连', '含',
                 '皆', '只', '归']

        for verb in verbs:
            if name.startswith(verb) and len(name) > len(verb):
                verb_node = Word(verb)
                arg_node = Word(name[len(verb):])
                return Call(verb_node, [arg_node])

        return Word(name)
