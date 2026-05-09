    def _parse_if(self) -> If:
        """解析条件语句：若 条件 则：分支。否则：分支。"""
        self._advance()  # 消耗 '若'

        # 解析条件（单个 term，可能是中缀表达式）
        # 不使用 _parse_expr_until，因为它会调用 _parse_term，导致循环
        # 直接解析原子和中缀动词
        cond = self._parse_atom()
        
        # 处理中缀动词
        while (self._current().type == TokenType.WORD and
               self._is_verb(self._current().value) and
               self._current().value not in self.ADVERBS and
               self._current().value != '则'):
            infix_verb = self._advance().value
            right = self._parse_atom()
            cond = Call(Word(infix_verb), [cond, right])

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
