"""
言语言语法分析器 - 最终版
"""

from typing import List, Optional, Set
from lexer import Token, TokenType
from nodes import *


class ParserError(Exception):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"语法错误 (行{line}, 列{col}): {message}")


class Parser:
    """语法分析器"""

    ADVERBS = {'皆', '只', '归', '潜'}
    VARARGS = {'列', '典', '序'}
    BUILTIN_VERBS = {
        '加', '减', '乘', '除', '模', '幂', '绝对', '负',
        '大', '小', '等', '不等',
        '且', '或', '非',
        '首', '余', '入', '长', '添', '连', '含', '空',
        '皆', '只', '归', '潜',
        '印', '读', '写', '行',
        '若', '则', '否则', '定', '函',
        '列', '典', '序', '范围',
    }

    def __init__(self):
        self.tokens: List[Token] = []
        self.pos: int = 0
        self.user_verbs: Set[str] = set()  # 用户定义的函数名

    @property
    def VERBS(self) -> Set[str]:
        """合并内置动词和用户定义动词"""
        return self.BUILTIN_VERBS | self.user_verbs

    def parse(self, tokens: List[Token]) -> Program:
        self.tokens = tokens
        self.pos = 0
        self.user_verbs = set()

        # 第一遍：收集用户定义的函数名
        self._collect_user_verbs()

        # 第二遍：正常解析
        self.pos = 0
        statements = []

        while not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        return Program(statements)

    def _collect_user_verbs(self):
        """第一遍扫描：收集所有用户定义的函数名"""
        pos = 0
        while pos < len(self.tokens):
            tok = self.tokens[pos]
            # 查找 "定 名称 = 函" 或 "定 名称 = {{...}}" 模式
            if tok.type == TokenType.WORD and tok.value == '定':
                if pos + 2 < len(self.tokens):
                    name_tok = self.tokens[pos + 1]
                    eq_tok = self.tokens[pos + 2]
                    if name_tok.type == TokenType.WORD and eq_tok.type == TokenType.EQUALS:
                        # 检查是否是函数定义
                        if pos + 3 < len(self.tokens):
                            next_tok = self.tokens[pos + 3]
                            # 定 名称 = 函 ...
                            if next_tok.type == TokenType.WORD and next_tok.value == '函':
                                self.user_verbs.add(name_tok.value)
                            # 定 名称 = {{...}} (Python 代码块，可能是函数)
                            elif next_tok.type == TokenType.PYTHON:
                                self.user_verbs.add(name_tok.value)
            pos += 1

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def _is_at_end(self) -> bool:
        return self._current().type == TokenType.EOF

    def _advance(self) -> Token:
        tok = self._current()
        if not self._is_at_end():
            self.pos += 1
        return tok

    def _match(self, *types: TokenType) -> bool:
        if self._current().type in types:
            self._advance()
            return True
        return False

    def _expect(self, token_type: TokenType, message: str) -> Token:
        if self._current().type == token_type:
            return self._advance()
        raise ParserError(message, self._current().line, self._current().col)

    def _check_word(self, value: str) -> bool:
        return (self._current().type == TokenType.WORD and
                self._current().value == value)

    def _is_verb(self, name: str) -> bool:
        return name in self.VERBS or name in self.ADVERBS

    def _parse_statement(self) -> Optional[Node]:
        if self._match(TokenType.DOT, TokenType.SEMI):
            return None

        if self._check_word('定'):
            return self._parse_define()

        expr = self._parse_expression()
        self._match(TokenType.DOT, TokenType.SEMI)

        return expr

    def _parse_define(self) -> Define:
        self._advance()
        name_tok = self._expect(TokenType.WORD, "期望标识符")
        name = name_tok.value
        self._expect(TokenType.EQUALS, "期望 '='")

        if self._check_word('函'):
            value = self._parse_lambda()
        else:
            value = self._parse_expression()

        return Define(name, value)

    def _parse_lambda(self) -> Lambda:
        self._advance()  # 消耗 '函'

        params = []
        # 收集参数（非动词、非关键字的标识符）
        while (self._current().type == TokenType.WORD and
               self._current().value not in self.VERBS and
               self._current().value not in {'若', '则', '否则', '真', '假', '空'} and
               self._current().value not in {'定', '函'}):
            params.append(self._advance().value)

        # 检查是否有块（冒号或句号后换行）
        if self._current().type == TokenType.COLON:
            self._advance()  # 消耗 '：'
            body = self._parse_block()
        else:
            body = self._parse_expression()
        return Lambda(params, body)

    def _parse_block(self) -> Node:
        """解析代码块"""
        statements = []
        
        while not self._is_at_end():
            # 块结束条件：遇到句号后跟非缩进内容
            if self._is_block_end():
                break
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            
            # 如果刚解析完一个语句（遇到句号），检查下一个token
            # 如果是 印 或其他顶层操作，块结束
            if self._current().type == TokenType.WORD:
                if self._current().value in {'印'}:
                    break
        
        if len(statements) == 0:
            return Nil()
        elif len(statements) == 1:
            return statements[0]
        else:
            return Block(statements)
    
    def _is_block_end(self) -> bool:
        """检查是否到达块结束"""
        tok = self._current()
        
        # 文件结束
        if tok.type == TokenType.EOF:
            return True
        
        # 只有遇到新的函数定义才结束块
        # 注意：块内可以有 定 定义局部变量
        if tok.type == TokenType.WORD and tok.value in {'函'}:
            return True
        
        return False

    def _parse_expression(self) -> Node:
        return self._parse_pipeline()

    def _parse_pipeline(self) -> Node:
        steps = [self._parse_expr()]

        while self._match(TokenType.COMMA):
            steps.append(self._parse_expr())

        if len(steps) == 1:
            return steps[0]
        return Pipeline(steps)

    def _parse_expr(self) -> Node:
        """解析表达式：动词 数据* (副词 动词 数据*)*"""
        first = self._parse_term()

        # 处理副词链
        while self._current().type == TokenType.WORD and self._current().value in self.ADVERBS:
            adverb_name = self._advance().value
            adverb = Word(adverb_name)
            next_call = self._parse_term()
            first = Call(adverb, [first, next_call])

        return first

    def _parse_term(self) -> Node:
        """解析项"""
        # 条件语句
        if self._check_word('若'):
            return self._parse_if()

        # 副词开头
        if self._current().type == TokenType.WORD and self._current().value in self.ADVERBS:
            adverb_name = self._advance().value
            adverb = Word(adverb_name)
            next_call = self._parse_term()
            return Call(adverb, [next_call])

        # 动词开头（必须是已知动词）
        if self._current().type == TokenType.WORD and self._is_verb(self._current().value):
            verb_name = self._advance().value
            verb = Word(verb_name)
            args = []

            while not self._is_at_end():
                tok = self._current()

                if tok.type in {TokenType.DOT, TokenType.SEMI, TokenType.COMMA,
                                TokenType.RPAREN, TokenType.EQUALS}:
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
                    # 普通动词：吞噬
                    arg = self._parse_term()
                    args.append(arg)
                    break

                # 原子 + 可能的中缀动词
                arg = self._parse_atom()

                # 中缀动词
                while (self._current().type == TokenType.WORD and
                       self._is_verb(self._current().value) and
                       self._current().value not in self.ADVERBS and
                       self._current().value not in {'若', '则', '否则'}):
                    infix_name = self._advance().value
                    infix = Word(infix_name)
                    right = self._parse_term()  # 改为 _parse_term() 以支持动词作为右操作数
                    arg = Call(infix, [arg, right])

                args.append(arg)

            return Call(verb, args)

        # 数据开头（数字、字符串、标识符）
        left = self._parse_atom()

        # 中缀动词（不能是条件关键字）
        while (self._current().type == TokenType.WORD and
               self._is_verb(self._current().value) and
               self._current().value not in self.ADVERBS and
               self._current().value not in {'若', '则', '否则'}):
            verb_name = self._advance().value
            verb = Word(verb_name)
            right = self._parse_term()  # 改为 _parse_term() 以支持动词作为右操作数
            left = Call(verb, [left, right])

        return left

    def _parse_atom(self) -> Node:
        """解析原子"""
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN, "期望 '」'")
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

    def _parse_if(self) -> If:
        """解析条件语句：若 条件 则 分支 否则 分支"""
        self._advance()  # 消耗 '若'

        # 解析条件（单个 term）
        cond = self._parse_term()

        self._expect(TokenType.WORD, "期望 '则'")

        # 解析 then 分支（单个 term）
        then_branch = self._parse_term()

        else_branch = None
        if self._check_word('否则'):
            self._advance()
            else_branch = self._parse_term()

        return If(cond, then_branch, else_branch)


def process_adverbs(node: Node, adverbs: Set[str] = None) -> Node:
    if adverbs is None:
        adverbs = Parser.ADVERBS

    if isinstance(node, Pipeline):
        new_steps = []
        i = 0
        steps = node.steps

        while i < len(steps):
            step = steps[i]

            if isinstance(step, Call) and step.verb.name in adverbs:
                if i + 1 < len(steps):
                    right = steps[i + 1]
                    step = Call(step.verb, [right], step.is_partial)
                    new_steps.append(step)
                    i += 2
                    continue

            if isinstance(step, Call):
                step = Call(
                    step.verb,
                    [process_adverbs(a, adverbs) for a in step.args],
                    step.is_partial
                )
            elif isinstance(step, Pipeline):
                step = process_adverbs(step, adverbs)

            new_steps.append(step)
            i += 1

        return Pipeline(new_steps)

    if isinstance(node, Call):
        return Call(
            node.verb,
            [process_adverbs(a, adverbs) for a in node.args],
            node.is_partial
        )

    return node
