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
                # 将剩余部分放回 token 流
                remaining = current_word[len(user_verb):]
                if remaining:
                    # 检查剩余部分是否以动词开头
                    # 如果是，需要拆分成多个 token
                    tokens_to_insert = []
                    
                    # 尝试从剩余部分中提取动词
                    # 例如："盘子数减" -> "盘子数" + "减"
                    for verb in sorted(self.VERBS, key=len, reverse=True):
                        if remaining.endswith(verb):
                            # 找到动词在末尾
                            before_verb = remaining[:-len(verb)]
                            if before_verb:
                                tokens_to_insert.append(Token(TokenType.WORD, before_verb,
                                                            self._current().line, self._current().col))
                            tokens_to_insert.append(Token(TokenType.WORD, verb,
                                                        self._current().line, self._current().col))
                            remaining = remaining[:-len(verb)]
                            break
                    else:
                        # 没有找到动词，直接插入剩余部分
                        tokens_to_insert.append(Token(TokenType.WORD, remaining,
                                                    self._current().line, self._current().col))
                    
                    # 插入 tokens（逆序插入，因为 insert 在当前位置插入）
                    for token in reversed(tokens_to_insert):
                        self.tokens.insert(self.pos, token)
                
                return user_verb
        
        return None
