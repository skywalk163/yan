# Generated from Yan.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .YanParser import YanParser
else:
    from YanParser import YanParser

# This class defines a complete generic visitor for a parse tree produced by YanParser.

class YanVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by YanParser#program.
    def visitProgram(self, ctx:YanParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#statement.
    def visitStatement(self, ctx:YanParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#DefineWithKeyword.
    def visitDefineWithKeyword(self, ctx:YanParser.DefineWithKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#DefineWithoutKeyword.
    def visitDefineWithoutKeyword(self, ctx:YanParser.DefineWithoutKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#DefineWithDengyu.
    def visitDefineWithDengyu(self, ctx:YanParser.DefineWithDengyuContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#value.
    def visitValue(self, ctx:YanParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#LambdaWithBlock.
    def visitLambdaWithBlock(self, ctx:YanParser.LambdaWithBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#LambdaWithExpr.
    def visitLambdaWithExpr(self, ctx:YanParser.LambdaWithExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#LambdaIdWithBlock.
    def visitLambdaIdWithBlock(self, ctx:YanParser.LambdaIdWithBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#LambdaIdWithExpr.
    def visitLambdaIdWithExpr(self, ctx:YanParser.LambdaIdWithExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#block.
    def visitBlock(self, ctx:YanParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#exprStmt.
    def visitExprStmt(self, ctx:YanParser.ExprStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#IfExpr.
    def visitIfExpr(self, ctx:YanParser.IfExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#ForeachExpr.
    def visitForeachExpr(self, ctx:YanParser.ForeachExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#WhileExpr.
    def visitWhileExpr(self, ctx:YanParser.WhileExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#PipelineExpr.
    def visitPipelineExpr(self, ctx:YanParser.PipelineExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#thenBranch.
    def visitThenBranch(self, ctx:YanParser.ThenBranchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#elseBranch.
    def visitElseBranch(self, ctx:YanParser.ElseBranchContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#pipeline.
    def visitPipeline(self, ctx:YanParser.PipelineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#VerbCallExpr.
    def visitVerbCallExpr(self, ctx:YanParser.VerbCallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#InfixExprAlt.
    def visitInfixExprAlt(self, ctx:YanParser.InfixExprAltContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#verbCall.
    def visitVerbCall(self, ctx:YanParser.VerbCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#infixExpr.
    def visitInfixExpr(self, ctx:YanParser.InfixExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#NumberAtom.
    def visitNumberAtom(self, ctx:YanParser.NumberAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#StringAtom.
    def visitStringAtom(self, ctx:YanParser.StringAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#TrueAtom.
    def visitTrueAtom(self, ctx:YanParser.TrueAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#FalseAtom.
    def visitFalseAtom(self, ctx:YanParser.FalseAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#NilAtom.
    def visitNilAtom(self, ctx:YanParser.NilAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#MathAtom.
    def visitMathAtom(self, ctx:YanParser.MathAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#PythonAtom.
    def visitPythonAtom(self, ctx:YanParser.PythonAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#QuoteAtom.
    def visitQuoteAtom(self, ctx:YanParser.QuoteAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by YanParser#IdAtom.
    def visitIdAtom(self, ctx:YanParser.IdAtomContext):
        return self.visitChildren(ctx)



del YanParser