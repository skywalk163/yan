    def visitInfixExpr(self, ctx: YanParser.InfixExprContext):
        """处理中缀表达式"""
        # 获取第一个 atom
        left = self.visit(ctx.atom())
        
        # 处理中缀操作符
        if ctx.term():
            # 获取所有中缀操作符和右操作数
            # 注意：ANTLR 将它们放在两个列表中
            # 但我们需要成对处理
            # ctx.getChild(i) 会返回所有子节点
            
            children = list(ctx.getChildren())
            i = 1  # 跳过第一个 atom
            while i < len(children):
                # 获取操作符
                op_token = children[i]
                op_name = op_token.getText()
                
                # 获取右操作数
                i += 1
                right_ctx = children[i]
                right = self.visit(right_ctx)
                
                # 创建调用节点
                verb = Word(op_name)
                left = Call(verb, [left, right])
                
                i += 1
        
        return left
