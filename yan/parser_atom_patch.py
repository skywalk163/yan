    def _parse_atom(self) -> Node:
        """解析原子"""
        # 引用：'expr
        if self._current().type == TokenType.QUOTE:
            self._advance()  # 跳过 '
            expr = self._parse_expression()
            return Quote(expr)

        if self._check_word('若'):
            return self._parse_if()

        if self._current().type == TokenType.NUM:
            return Num(self._advance().value)

        if self._current().type == TokenType.STR:
            return Str(self._advance().value)

        # 数学表达式
        if self._current().type == TokenType.MATH:
            return MathExpr(self._advance().value)

        # Python 代码块
        if self._current().type == TokenType.PYTHON:
            return PythonCode(self._advance().value)

        if self._check_word('真'):
            self._advance()
            return Bool(True)
        if self._check_word('假'):
            self._advance()
            return Bool(False)
        if self._check_word('空'):
            self._advance()
            return Nil()

        # 条件关键字不是原子
        if self._current().type == TokenType.WORD and self._current().value in {'则', '否则'}:
            raise ParserError(f"意外的关键字: {self._current().value}",
                             self._current().line, self._current().col)

        # 普通标识符（变量名）
        if self._current().type == TokenType.WORD:
            return Word(self._advance().value)

        raise ParserError(f"意外的 token: {self._current()}",
                         self._current().line, self._current().col)

