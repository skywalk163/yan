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
            if tok.type == TokenType.WORD and self._is_verb(tok.value):
                break
            # 使用 _parse_term 而不是 _parse_atom，以支持中缀动词
            arg = self._parse_term()
            args.append(arg)
        return args
