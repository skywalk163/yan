    def _try_match_user_verb(self) -> Optional[str]:
        """尝试匹配用户定义的函数名（可能被拆分为多个 WORD 或与其他汉字组合）"""
        if not self.use_global_verbs:
            return None
        
        # 收集当前位置开始的连续 WORD
        saved_pos = self.pos
        word_parts = []
        while self._current().type == TokenType.WORD:
            word_parts.append(self._current().value)
            self.pos += 1
        
        self.pos = saved_pos  # 恢复位置
        
        if not word_parts:
            return None
        
        # 尝试最长匹配（完整匹配）
        for length in range(len(word_parts), 0, -1):
            candidate = ''.join(word_parts[:length])
            if candidate in _global_user_verbs:
                # 消耗匹配的 tokens
                for _ in range(length):
                    self._advance()
                return candidate
        
        # 尝试前缀匹配：当前 token 可能包含用户定义的函数名
        # 例如："汉诺塔盘子数减" 可能包含 "汉诺塔"
        current_word = word_parts[0]
        for user_verb in _global_user_verbs:
            if current_word.startswith(user_verb):
                # 找到匹配的用户定义函数名
                # 消耗匹配的 token
                self._advance()
                # 将剩余部分放回 token 流（通过修改当前 token）
                remaining = current_word[len(user_verb):]
                if remaining:
                    # 创建新的 token 并插入到 token 流中
                    # 这需要修改 tokens 列表
                    new_token = Token(TokenType.WORD, remaining, 
                                     self._current().line, self._current().col)
                    self.tokens.insert(self.pos, new_token)
                return user_verb
        
        return None
