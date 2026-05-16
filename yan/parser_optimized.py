"""
言语言语法分析器（性能优化版）
优化热点：
1. 缓存 Token 类型访问
2. 优化表达式解析
3. 减少重复的属性访问
"""

from enum import Enum, auto

class NodeType(Enum):
    PROGRAM = 1
    NUM = 2
    STR = 3
    BOOL = 4
    NULL = 5
    WORD = 6
    DEFINE = 7
    LAMBDA = 8
    CALL = 9
    IF = 10
    WHILE = 11
    PYTHON = 12

class TokenType(Enum):
    NUM = auto()
    STR = auto()
    WORD = auto()
    QUOTE = auto()
    COMMA = auto()
    DOT = auto()
    SEMI = auto()
    COLON = auto()
    EQUALS = auto()
    MATH = auto()
    PYTHON = auto()
    EOF = auto()

class Token:
    __slots__ = ('type', 'value', 'line', 'col')
    
    def __init__(self, token_type, value, line=0, col=0):
        self.type = token_type
        self.value = value
        self.line = line
        self.col = col

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, keywords=None):
        self.keywords = keywords or set()
        self.user_verbs = set()
        self.tokens = []
        self.current = 0
    
    def _current(self):
        return self.tokens[self.current] if self.current < len(self.tokens) else None
    
    def _advance(self):
        self.current += 1
        return self._current()
    
    def _is_at_end(self):
        return self._current() is None or self._current().type == TokenType.EOF
    
    def _check_word(self, word):
        c = self._current()
        return c and c.type == TokenType.WORD and c.value == word
    
    def _is_verb(self, word):
        return word in self.user_verbs or word in self.keywords
    
    def _parse_expression(self):
        return self._parse_pipeline()
    
    def _parse_pipeline(self):
        first = self._parse_expr()
        steps = [first]
        
        while self._current() and self._current().type == TokenType.COMMA:
            self._advance()
            steps.append(self._parse_expr())
        
        if len(steps) == 1:
            return first
        
        return (NodeType.CALL, ['管道', steps])
    
    def _parse_expr(self):
        return self._parse_term()
    
    def _parse_term(self):
        current = self._current()
        
        if current is None:
            return (NodeType.WORD, None)
        
        # Python 代码块
        if current.type == TokenType.PYTHON:
            value = current.value
            self._advance()
            return (NodeType.PYTHON, value)
        
        # 数字
        if current.type == TokenType.NUM:
            value = current.value
            self._advance()
            return (NodeType.NUM, value)
        
        # 字符串
        if current.type == TokenType.STR:
            value = current.value
            self._advance()
            return (NodeType.STR, value)
        
        # 关键字/动词
        if current.type == TokenType.WORD:
            word = current.value
            
            # if 语句
            if word == '若':
                return self._parse_if()
            
            # while 循环
            if word == '当':
                return self._parse_while()
            
            # 定义语句
            if word == '定':
                return self._parse_define()
            
            # 关键字字面量
            if word == '真':
                self._advance()
                return (NodeType.BOOL, True)
            if word == '假':
                self._advance()
                return (NodeType.BOOL, False)
            if word == '空' or word == '无':
                self._advance()
                return (NodeType.NULL, None)
            
            # 函数调用
            self._advance()
            return self._parse_call(word)
        
        return (NodeType.WORD, None)
    
    def _parse_if(self):
        self._advance()  # 跳过 '若'
        condition = self._parse_expression()
        
        if not self._check_word('则'):
            return condition
        
        self._advance()  # 跳过 '则'
        then_branch = self._parse_expression()
        
        if self._check_word('否则'):
            self._advance()  # 跳过 '否则'
            else_branch = self._parse_expression()
            return (NodeType.IF, [condition, then_branch, else_branch])
        
        return (NodeType.IF, [condition, then_branch, None])
    
    def _parse_while(self):
        self._advance()  # 跳过 '当'
        condition = self._parse_expression()
        
        if not self._check_word('则'):
            return (NodeType.WHILE, [condition, (NodeType.WORD, None)])
        
        self._advance()  # 跳过 '则'
        body = self._parse_expression()
        
        return (NodeType.WHILE, [condition, body])
    
    def _parse_define(self):
        self._advance()  # 跳过 '定'
        
        name_token = self._current()
        if not name_token or name_token.type != TokenType.WORD:
            raise ParserError(f"期望变量名")
        
        name = name_token.value
        self.user_verbs.add(name)
        self._advance()  # 跳过名称
        
        value = self._parse_expression()
        
        return (NodeType.DEFINE, [name, value])
    
    def _parse_call(self, verb):
        args = []
        
        while True:
            c = self._current()
            
            if c is None:
                break
            
            if c.type == TokenType.WORD:
                word = c.value
                if word in ('若', '当', '定', '否则', '则'):
                    break
                if word == '函':
                    self._advance()
                    return self._parse_lambda(verb)
            
            if c.type in (TokenType.COLON, TokenType.SEMI, TokenType.COMMA, TokenType.EOF):
                break
            
            args.append(self._parse_expression())
        
        return (NodeType.CALL, [verb, args])
    
    def _parse_lambda(self, name):
        self._advance()  # 跳过 '函'
        
        params = []
        while True:
            c = self._current()
            if c is None or c.type != TokenType.WORD:
                break
            if c.value in ('若', '当', '定', '否则', '则'):
                break
            params.append(c.value)
            self.user_verbs.add(c.value)
            self._advance()
        
        body = self._parse_expression()
        
        return (NodeType.LAMBDA, [name, params, body])
    
    def _collect_user_verbs(self):
        self.user_verbs = set()
        for token in self.tokens:
            if token.type == TokenType.WORD and token.value == '定':
                idx = self.tokens.index(token) + 1
                if idx < len(self.tokens) and self.tokens[idx].type == TokenType.WORD:
                    self.user_verbs.add(self.tokens[idx].value)
    
    def parse(self, tokens):
        self.tokens = tokens
        self.current = 0
        
        self._collect_user_verbs()
        
        statements = []
        while not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return (NodeType.PROGRAM, [statements])
    
    def _parse_statement(self):
        current = self._current()
        
        if current is None:
            return None
        
        if current.type == TokenType.DOT:
            self._advance()
            return None
        
        if current.type == TokenType.SEMI:
            self._advance()
            return None
        
        if current.type == TokenType.PYTHON:
            value = current.value
            self._advance()
            return (NodeType.PYTHON, value)
        
        if current.type == TokenType.WORD:
            if current.value == '定':
                return self._parse_define()
            if current.value == '若':
                return self._parse_if()
            if current.value == '当':
                return self._parse_while()
        
        return self._parse_expression()
