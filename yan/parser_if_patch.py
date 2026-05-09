    def _parse_if(self) -> If:
        """解析条件语句：若 条件 则：分支。否则：分支。"""
        self._advance()  # 消耗 '若'

        # 解析条件（单个 term）
        cond = self._parse_term()

        self._expect(TokenType.WORD, "期望 '则'")

        # 检查是否有 '：'（块开始标记）
        has_block = self._current().type == TokenType.COLON
        if has_block:
            self._advance()  # 消耗 '：'

        # 解析 then 分支
        if has_block:
            # 块结构：解析多个语句，直到遇到 '否则' 或 '。'
            then_branch = self._parse_block_until({'否则'})
        else:
            # 单行结构：解析单个表达式
            then_branch = self._parse_expr_until({'否则'})

        else_branch = None
        # 跳过可能的句号
        if self._current().type == TokenType.DOT:
            self._advance()
        if self._check_word('否则'):
            self._advance()
            # 检查是否有 '：'
            if self._current().type == TokenType.COLON:
                self._advance()  # 消耗 '：'
                else_branch = self._parse_block_until(set())
            else:
                else_branch = self._parse_expr_until(set())

        return If(cond, then_branch, else_branch)

    def _parse_block_until(self, stop_words: Set[str]) -> Node:
        """解析块，直到遇到指定的停止词"""
        statements = []
        while not self._is_at_end():
            if self._current().type == TokenType.DOT:
                # 检查是否是块的结束（两个句号）
                if self._peek(1).type == TokenType.DOT or self._peek(1).type == TokenType.EOF:
                    break
                # 单个句号，跳过
                self._advance()
                continue
            if self._current().type == TokenType.WORD and self._current().value in stop_words:
                break
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        if len(statements) == 0:
            return Nil()
        elif len(statements) == 1:
            return statements[0]
        else:
            return Block(statements)
