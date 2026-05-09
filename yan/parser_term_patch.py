    def _parse_term(self) -> Node:
        """解析项"""
        # 条件语句
        if self._check_word('若'):
            return self._parse_if()

        # 遍历循环
        if self._check_word('遍历'):
            return self._parse_foreach()

        # 当循环
        if self._check_word('当'):
            return self._parse_while()

        # 副词开头
        if self._current().type == TokenType.WORD and self._current().value in self.ADVERBS:
            adverb_name = self._advance().value
            adverb = Word(adverb_name)
            next_call = self._parse_term()
            return Call(adverb, [next_call])

        # 用户定义的函数名（可能被包含在 token 中）
        # 例如："汉诺塔盘子数减" 包含用户定义的 "汉诺塔"
        if self._current().type == TokenType.WORD and self.use_global_verbs:
            matched_name = self._try_match_user_verb()
            if matched_name:
                func = Word(matched_name)
                args = self._collect_call_args()
                return Call(func, args)

        # 动词开头（必须是已知动词）
        if self._current().type == TokenType.WORD and self._is_verb(self._current().value):
            verb_name = self._advance().value
            verb = Word(verb_name)
            args = []

            while not self._is_at_end():
                tok = self._current()

                if tok.type in {TokenType.DOT, TokenType.SEMI, TokenType.COMMA,
                                TokenType.EQUALS, TokenType.COLON}:
                    break

                # 遇到条件关键字，停止
                if tok.type == TokenType.WORD and tok.value in {'若', '则', '否则'}:
                    break

                # 副词：停止
                if tok.type == TokenType.WORD and tok.value in self.ADVERBS:
                    break

                # 其他动词
                if tok.type == TokenType.WORD and self._is_verb(tok.value):
                    # 可变参数动词：停止
                    if verb_name in self.VARARGS:
                        break
                    # 高阶函数（归、皆、只）：动词作为参数传递（只取动词名，不解析参数）
                    if verb_name in {'归', '皆', '只'}:
                        args.append(Word(self._advance().value))
                        # 继续收集后续参数（如初始值）
                        continue
                    # 普通动词：吞噬
                    arg = self._parse_term()
                    args.append(arg)
                    break

                # 原子 + 可能的中缀动词
                arg = self._parse_atom()

                # 中缀动词
                while (self._current().type == TokenType.WORD and
                       self._is_verb(self._current().value) and
                       self._current().value not in self.ADVERBS):
                    infix_verb = self._advance().value
                    right = self._parse_atom()
                    arg = Call(Word(infix_verb), [arg, right])

                args.append(arg)

            return Call(verb, args)

        # 普通原子
        return self._parse_atom()
