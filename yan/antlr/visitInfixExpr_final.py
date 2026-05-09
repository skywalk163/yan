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
