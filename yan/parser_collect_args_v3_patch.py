    def _collect_call_args(self) -> List[Node]:
        """收集函数调用的参数"""
        args = []
        while not self._is_at_end():
            tok = self._current()
            if tok.type in {TokenType.DOT, TokenType.SEMI, TokenType.COMMA,
                            TokenType.EQUALS, TokenType.COLON}:
                break
            if tok.type == TokenType.WORD and tok.value in {'若', '则', '否则'}:
                break
            # 只有在遇到前缀动词时才停止
            # 中缀动词（如 "减"）应该作为参数的一部分
            if tok.type == TokenType.WORD and self._is_verb(tok.value):
                # 检查是否是前缀动词（动词调用）
                # 如果下一个 token 不是原子，说明这是动词调用，应该停止
                if self.pos + 1 < len(self.tokens):
                    next_tok = self.tokens[self.pos + 1]
                    # 如果下一个 token 是原子（NUM, STR, WORD），说明这是中缀动词，继续解析
                    if next_tok.type in {TokenType.NUM, TokenType.STR, TokenType.WORD}:
                        # 这是中缀动词，继续解析
                        pass
                    else:
                        # 这是前缀动词调用，停止
                        break
                else:
                    break
            
            # 解析原子 + 可能的中缀动词
            arg = self._parse_atom()
            
            # 中缀动词
            while (self._current().type == TokenType.WORD and
                   self._is_verb(self._current().value) and
                   self._current().value not in self.ADVERBS):
                infix_verb = self._advance().value
                right = self._parse_atom()
                arg = Call(Word(infix_verb), [arg, right])
            
            args.append(arg)
        return args
