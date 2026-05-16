"""
言语言词法分析器（性能优化版）
优化热点：
1. 缓存 len(source) 调用
2. 优化字符类型判断
3. 减少 ord() 调用
"""

from enum import Enum, auto
from typing import List, Set, Any

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
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r})"

class Lexer:
    HAN_START = 0x4E00
    HAN_END = 0x9FFF
    
    def __init__(self, keywords=None, user_words=None):
        self.keywords = keywords or set()
        self.user_words = user_words or set()
        self.user_defs = set()
    
    def _is_digit(self, c):
        return '0' <= c <= '9'
    
    def _is_alpha(self, c):
        return ('a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '_')
    
    def _is_han(self, c):
        if not c:
            return False
        code = ord(c)
        return 0x4E00 <= code <= 0x9FFF
    
    def _is_ws(self, c):
        return c in ' \t\n\r'
    
    def _is_same_type(self, c, prev_c):
        if self._is_digit(c) and self._is_digit(prev_c):
            return True
        if (self._is_alpha(c) or self._is_han(c)) and \
           (self._is_alpha(prev_c) or self._is_han(prev_c)):
            return True
        return False
    
    def _scan_string(self, s, start):
        i = start + 1
        while i < len(s):
            if s[i] == '"':
                if s[i-1] != '\\':
                    return s[start+1:i], i + 1
            i += 1
        return s[start+1:i], i
    
    def _scan_python(self, s, start):
        i = start + 2
        while i < len(s):
            if s[i] == '}' and i + 1 < len(s) and s[i+1] == '}':
                return s[start+2:i], i + 2
            i += 1
        return s[start+2:i], i
    
    def tokenize(self, source):
        tokens = []
        i = 0
        n = len(source)  # 缓存长度
        
        while i < n:
            c = source[i]
            
            if c == ' ' or c == '\t':
                i += 1
                continue
            if c == '\n':
                i += 1
                continue
            if c == '\r':
                i += 1
                continue
            
            # Python 代码块
            if c == '{' and i + 1 < n and source[i+1] == '{':
                code, i = self._scan_python(source, i)
                tokens.append(Token(TokenType.PYTHON, code))
                continue
            
            # 字符串
            if c == '"':
                value, i = self._scan_string(source, i)
                tokens.append(Token(TokenType.STR, value))
                continue
            
            # 特殊字符
            if c == '，':
                tokens.append(Token(TokenType.COMMA, c))
                i += 1
                continue
            if c == '。':
                tokens.append(Token(TokenType.DOT, c))
                i += 1
                continue
            if c == '：':
                tokens.append(Token(TokenType.COLON, c))
                i += 1
                continue
            if c == '=':
                tokens.append(Token(TokenType.EQUALS, c))
                i += 1
                continue
            if c == '；':
                tokens.append(Token(TokenType.SEMI, c))
                i += 1
                continue
            if c == "'":
                tokens.append(Token(TokenType.QUOTE, c))
                i += 1
                continue
            
            # 数字
            if self._is_digit(c):
                j = i
                while j < n and self._is_digit(source[j]):
                    j += 1
                tokens.append(Token(TokenType.NUM, source[i:j]))
                i = j
                continue
            
            # 标识符（英文或中文）
            if self._is_alpha(c) or self._is_han(c):
                j = i
                while j < n and (self._is_alpha(source[j]) or 
                                self._is_han(source[j]) or 
                                self._is_digit(source[j])):
                    j += 1
                word = source[i:j]
                
                if word in self.keywords:
                    tokens.append(Token(TokenType.WORD, word))
                elif word in self.user_defs:
                    tokens.append(Token(TokenType.WORD, word))
                elif word in self.user_words:
                    tokens.append(Token(TokenType.WORD, word))
                else:
                    tokens.append(Token(TokenType.WORD, word))
                i = j
                continue
            
            # 注释
            if c == '-' and i + 1 < n and source[i+1] == '-':
                while i < n and source[i] != '\n':
                    i += 1
                continue
            
            # 跳过未知字符
            i += 1
        
        tokens.append(Token(TokenType.EOF, None))
        return tokens
    
    def _scan_user_defs(self, source):
        self.user_defs = set()
        tokens = self.tokenize(source)
        for i, token in enumerate(tokens):
            if token.type == TokenType.WORD and token.value == '定':
                if i + 1 < len(tokens) and tokens[i+1].type == TokenType.WORD:
                    self.user_defs.add(tokens[i+1].value)
