    def visitLambdaIdWithBlock(self, ctx: YanParser.LambdaIdWithBlockContext):
        """处理 ID ID* COLON block 的情况（"函参数..."被识别为ID）"""
        # 获取所有 ID
        ids = [id_node.getText() for id_node in ctx.ID()]
        
        # 检查第一个 ID 是否以"函"开头
        if ids and ids[0].startswith('函'):
            # 拆分"函"和第一个参数
            first_id = ids[0]
            params = [first_id[1:]] if len(first_id) > 1 else []
            # 添加其他参数
            params.extend(ids[1:])
        else:
            # 不是以"函"开头，这是错误的
            raise SyntaxError(f"Lambda 表达式必须以'函'开头，但得到: {ids[0] if ids else '空'}")
        
        body = self.visit(ctx.block())
        return Lambda(params, body)
    
    def visitLambdaIdWithExpr(self, ctx: YanParser.LambdaIdWithExprContext):
        """处理 ID ID* expression 的情况（"函参数..."被识别为ID）"""
        # 获取所有 ID
        ids = [id_node.getText() for id_node in ctx.ID()]
        
        # 检查第一个 ID 是否以"函"开头
        if ids and ids[0].startswith('函'):
            # 拆分"函"和第一个参数
            first_id = ids[0]
            params = [first_id[1:]] if len(first_id) > 1 else []
            # 添加其他参数
            params.extend(ids[1:])
        else:
            # 不是以"函"开头，这是错误的
            raise SyntaxError(f"Lambda 表达式必须以'函'开头，但得到: {ids[0] if ids else '空'}")
        
        body = self.visit(ctx.expression())
        return Lambda(params, body)
