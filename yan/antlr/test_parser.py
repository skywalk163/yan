#!/usr/bin/env python3
"""
测试 ANTLR 解析器
"""

import sys
sys.path.insert(0, 'generated')

from antlr4 import *
from YanLexer import YanLexer
from YanParser import YanParser
from YanVisitor import YanVisitor

# 测试代码
code = """
定距离=函a b：
  定差=减a b。
  若差小0则负差否则差。
。
印距离3 7。
"""

# 创建词法分析器
input_stream = InputStream(code)
lexer = YanLexer(input_stream)
token_stream = CommonTokenStream(lexer)

# 创建语法分析器
parser = YanParser(token_stream)

# 解析程序
tree = parser.program()

# 打印解析树
print("=== 解析树 ===")
print(tree.toStringTree(recog=parser))
print()

# 打印所有 token
print("=== Token 列表 ===")
lexer.reset()
for token in lexer.getAllTokens():
    token_name = YanLexer.symbolicNames[token.type] if token.type < len(YanLexer.symbolicNames) else "UNKNOWN"
    print(f"{token.tokenIndex:3d}: {token_name:15s} '{token.text}'")
print()

# 自定义访问者
class PrintVisitor(YanVisitor):
    def visitDefineWithKeyword(self, ctx):
        name = ctx.ID().getText()
        print(f"定义 (带关键字): {name}")
        return self.visitChildren(ctx)
    
    def visitDefineWithoutKeyword(self, ctx):
        name = ctx.ID().getText()
        print(f"定义 (省略关键字): {name}")
        return self.visitChildren(ctx)
    
    def visitFunctionCall(self, ctx):
        func_name = ctx.ID().getText()
        print(f"函数调用: {func_name}")
        return self.visitChildren(ctx)

# 使用访问者
print("=== AST 遍历 ===")
visitor = PrintVisitor()
visitor.visit(tree)
