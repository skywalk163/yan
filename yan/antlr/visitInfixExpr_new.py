    def visitInfixExpr(self, ctx: YanParser.InfixExprContext):
        left = self.visit(ctx.atom())
        
        # 如果 left 已经是一个中缀动词调用，直接返回
        # （因为 ID 已经被拆分为 Call(verb, [arg])）
        if isinstance(left, Call):
            verb_name = left.verb.name
            infix_verbs = ['加', '减', '乘', '除', '模', '幂', '绝对', '负',
                          '大', '小', '等', '不等', '且', '或', '非',
                          '首', '余', '入', '长', '连', '含',
                          '皆', '只', '归']
            if verb_name in infix_verbs:
                # 如果有后续的中缀操作符，将它们作为参数添加
                children = list(ctx.getChildren())
                if len(children) > 1:
                    # 有中缀操作符，需要将右操作数添加到参数列表
                    i = 1
                    while i < len(children):
                        op_token = children[i]
                        op_name = op_token.getText()
                        i += 1
                        right_ctx = children[i]
                        right = self.visit(right_ctx)
                        # 将右操作数添加到 left 的参数列表
                        left.args.append(right)
                        i += 1
                return left
        
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
