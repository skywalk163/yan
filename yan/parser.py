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


# 全局用户动词集合（用于交互模式）
_global_user_verbs: Set[str] = set()


def get_global_user_verbs() -> Set[str]:
    """获取全局用户动词集合"""
    return _global_user_verbs


def add_global_user_verb(name: str):
    """添加全局用户动词"""
    _global_user_verbs.add(name)


def clear_global_user_verbs():
    """清空全局用户动词集合"""
    _global_user_verbs.clear()


class BlockStack:
    """块栈，用于跟踪当前块的状态"""

    def __init__(self):
        self._stack: List[dict] = []

    def push(self, block_type: str, indent_level: int):
        """压入新块"""
        self._stack.append({
            'type': block_type,
            'indent': indent_level
        })

    def pop(self) -> Optional[dict]:
        """弹出块，返回弹出的块信息，如果栈为空则返回 None"""
        if self.is_empty():
            return None
        return self._stack.pop()

    def current(self) -> Optional[dict]:
        """获取当前块，如果栈为空则返回 None"""
        if self.is_empty():
            return None
        return self._stack[-1]

    def depth(self) -> int:
        """获取栈深度"""
        return len(self._stack)

    def is_empty(self) -> bool:
        """检查栈是否为空"""
        return len(self._stack) == 0


class Parser:
    """语法分析器"""

    ADVERBS = {'潜'}  # 潜 is the only true adverb that modifies verbs
    VARARGS = {'列', '典', '序'}
    BUILTIN_VERBS = {
        '加', '减', '乘', '除', '模', '幂', '绝对', '负',
        '大', '小', '等', '不等',
        '且', '或', '非',
        '首', '余', '入', '长', '添', '连', '含', '空',
        '皆', '只', '归', '潜',
        '印', '读', '写', '行',
        '若', '则', '否则', '定', '函',
        '遍历', '于', '当',
        '列', '典', '序', '范围',
        # 字符串库
        '长度', '连接', '分割', '替换', '截取', '小写', '大写',
        '查找', '包含', '去空', '开头是', '结尾是',
        # 数学库
        '正弦', '余弦', '正切', '反正弦', '反余弦', '反正切',
        '指数', '对数', '对数10', '开方', '取整', '进位', '四舍五入',
        '随机', '随机整数', '圆周率', '自然常数',
        # 类型检查
        '是数', '是串', '是表', '是函', '是真', '是空', '类型',
    }

    def __init__(self, use_global_verbs: bool = False):
        self.tokens: List[Token] = []
        self.pos: int = 0
        self.user_verbs: Set[str] = set()
        self.use_global_verbs = use_global_verbs
        self.block_stack = BlockStack()

    @property
    def VERBS(self) -> Set[str]:
        """合并内置动词和用户定义动词"""
        if self.use_global_verbs:
            return self.BUILTIN_VERBS | _global_user_verbs | self.user_verbs
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
                                if self.use_global_verbs:
                                    _global_user_verbs.add(name_tok.value)
                            # 定 名称 = {{...}} (Python 代码块，可能是函数)
                            elif next_tok.type == TokenType.PYTHON:
                                self.user_verbs.add(name_tok.value)
                                if self.use_global_verbs:
                                    _global_user_verbs.add(name_tok.value)
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

    def _parse_statement(self) -> Optional[Node]:
        if self._match(TokenType.DOT, TokenType.SEMI):
            return None

        if self._check_word('定'):
            return self._parse_define()

        expr = self._parse_expression()
        self._match(TokenType.DOT, TokenType.SEMI)

        return expr

    def _parse_define(self) -> Define:
        self._advance()  # 消耗 '定'
        
        # 收集连续的 WORD 作为名称（直到遇到 '='）
        name_parts = []
        while self._current().type == TokenType.WORD:
            # 检查下一个是否是 '='
            next_tok = self._peek(1)
            if next_tok.type == TokenType.EQUALS:
                # 这是名称的最后一部分
                name_parts.append(self._advance().value)
                break
            name_parts.append(self._advance().value)
        
        if not name_parts:
            raise ParserError("期望标识符", self._current().line, self._current().col)
        
        name = ''.join(name_parts)
        self._expect(TokenType.EQUALS, "期望 '='")

        if self._check_word('函'):
            value = self._parse_lambda()
            # 添加到全局用户动词集合
            if self.use_global_verbs:
                _global_user_verbs.add(name)
        else:
            value = self._parse_expression()

        return Define(name, value)

    def _parse_lambda(self) -> Lambda:
        self._advance()  # 消耗 '函'

        params = []
        # 收集参数（非动词、非关键字的标识符）
        # 参数必须连续，遇到其他类型则停止
        while (self._current().type == TokenType.WORD and
                self._current().value not in self.VERBS and
                self._current().value not in {'若', '则', '否则', '真', '假', '空'} and
                self._current().value not in {'定', '函'}):
            # 如果下一个 token 是动词或条件关键字，当前可能是函数体的开始
            next_tok = self._peek(1)
            if next_tok.type == TokenType.DOT or next_tok.type == TokenType.COLON:
                # 当前 token 是最后一个参数
                params.append(self._advance().value)
                break
            if next_tok.type == TokenType.WORD and next_tok.value in {'若', '则', '否则'}:
                # 下一个是条件关键字，停止收集参数
                params.append(self._advance().value)
                break
            if next_tok.type == TokenType.WORD and next_tok.value not in self.VERBS:
                # 下一个也是非动词，继续收集
                params.append(self._advance().value)
            elif next_tok.type == TokenType.WORD and self._is_verb(next_tok.value):
                # 下一个是动词，当前 token 可能是参数，也可能是函数体
                if len(params) == 0:
                    params.append(self._advance().value)
                break
            else:
                params.append(self._advance().value)

        # 检查是否有块（冒号或句号后换行）
        if self._current().type == TokenType.COLON:
            self._advance()  # 消耗 '：'
            body = self._parse_block()
        else:
            body = self._parse_expression()
        return Lambda(params, body)

    def _parse_block(self) -> Node:
        """解析代码块，智能推断结束"""
        statements = []
        block_start_indent = self._get_current_indent()
        
        # 压入块栈
        self.block_stack.push('BLOCK', block_start_indent)
        
        while not self._is_at_end():
            # 跳过句号
            if self._current().type == TokenType.DOT:
                self._advance()
                
                # 检查是否应该结束块
                if self._should_end_block(block_start_indent):
                    # 特殊情况：在块内部遇到控制流关键字（若、遍历、当等）不应结束块
                    # 这些关键字在块内部是合法语句
                    if self._current().type == TokenType.WORD:
                        word = self._current().value
                        if word in {'若', '遍历', '当', '测', '套'}:
                            # 在块内部，控制流关键字是合法语句，继续解析
                            pass  # 继续解析
                        elif word == '定':
                            # 在块内部，'定' 是局部变量定义，继续解析
                            pass  # 继续解析
                        else:
                            break
                    else:
                        break
                continue
            
            # 块结束条件
            if self._is_block_end():
                break
            
            # 解析语句
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        # 弹出块栈
        self.block_stack.pop()
        
        if len(statements) == 0:
            return Nil()
        elif len(statements) == 1:
            return statements[0]
        else:
            return Block(statements)
    
    def _get_current_indent(self) -> int:
        """获取当前缩进级别（简化实现）"""
        # 简化实现：返回 0
        # 完整实现需要从 lexer 获取缩进信息
        return 0
    
    def _should_end_block(self, block_start_indent: int) -> bool:
        """
        判断是否应该结束当前块
        
        参数：
            block_start_indent: 块开始时的缩进级别
        
        返回：
            True 如果应该结束块，False 否则
        """
        # 情况 1：文件结束
        if self._is_at_end():
            return True
        
        # 情况 2：遇到新的定义
        if self._check_word('定'):
            return True
        
        # 情况 3：遇到同层级关键字
        if self._current().type == TokenType.WORD:
            word = self._current().value
            # 这些关键字表示新的块开始，应该结束当前块
            if word in {'若', '遍历', '当', '测', '套'}:
                return True
        
        # 情况 4：缩进减少（如果实现了缩进跟踪）
        # next_indent = self._peek_next_line_indent()
        # if next_indent < block_start_indent:
        #     return True
        
        return False

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
            # always_block=True 确保即使只有一个语句也返回 Block
            then_branch = self._parse_block_until({'否则'}, always_block=True)
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
                # always_block=True 确保即使只有一个语句也返回 Block
                else_branch = self._parse_block_until(set(), always_block=True)
            else:
                else_branch = self._parse_expr_until(set())

        return If(cond, then_branch, else_branch)

    def _parse_block_until(self, stop_words: Set[str], always_block: bool = False) -> Node:
        """解析块，直到遇到指定的停止词
        
        参数：
            stop_words: 停止词集合
            always_block: 如果为 True，即使只有一个语句也返回 Block
        """
        statements = []
        while not self._is_at_end():
            if self._current().type == TokenType.DOT:
                # 检查是否是块的结束（两个句号）
                if self._peek(1).type == TokenType.DOT or self._peek(1).type == TokenType.EOF:
                    break
                # 单个句号，跳过
                self._advance()
                continue
            if self._current().type == TokenType.WORD and self._current().value in stop_words:
                break
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        if len(statements) == 0:
            return Nil()
        elif len(statements) == 1 and not always_block:
            return statements[0]
        else:
            return Block(statements)
    def _parse_foreach(self) -> ForEach:
        """解析遍历循环：遍历 变量 于 列表：循环体。"""
        self._advance()  # 消耗 '遍历'
        
        # 解析变量名
        if self._current().type != TokenType.WORD:
            raise ParserError("期望变量名", self._current().line, self._current().col)
        var = self._advance().value
        
        # 期望 '于'
        if not self._check_word('于'):
            raise ParserError("期望 '于'", self._current().line, self._current().col)
        self._advance()  # 消耗 '于'
        
        # 解析可迭代对象
        iterable = self._parse_term()
        
        # 期望 '：'（块开始）
        if self._current().type != TokenType.COLON:
            raise ParserError("期望 '：' 开始循环体", self._current().line, self._current().col)
        self._advance()  # 消耗 '：'
        
        # 解析循环体
        body = self._parse_block()
        
        return ForEach(var, iterable, body)

    def _parse_while(self) -> While:
        """解析当循环：当 条件：循环体。"""
        self._advance()  # 消耗 '当'
        
        # 解析条件（单个 term，可能是中缀表达式）
        cond = self._parse_atom()
        
        # 处理中缀动词
        while (self._current().type == TokenType.WORD and
               self._is_verb(self._current().value) and
               self._current().value not in self.ADVERBS):
            # 遇到冒号时停止
            if self._current().type == TokenType.COLON:
                break
            infix_verb = self._advance().value
            right = self._parse_atom()
            cond = Call(Word(infix_verb), [cond, right])
        
        # 期望 '：'（块开始）
        if self._current().type != TokenType.COLON:
            raise ParserError("期望 '：' 开始循环体", self._current().line, self._current().col)
        self._advance()  # 消耗 '：'
        
        # 解析循环体
        body = self._parse_block()
        
        return While(cond, body)

    def _parse_expr_until(self, stop_words: Set[str]) -> Node:
        """解析表达式，直到遇到指定的停止词"""
        # 收集所有 term 直到遇到停止词
        terms = []
        while not self._is_at_end():
            if self._current().type == TokenType.DOT:
                break
            if self._current().type == TokenType.WORD and self._current().value in stop_words:
                break
            if self._current().type == TokenType.WORD and self._current().value in {'若', '则', '否则'}:
                # 如果是嵌套的条件语句
                if self._current().value == '若':
                    terms.append(self._parse_if())
                else:
                    break
            else:
                terms.append(self._parse_term())

        if len(terms) == 0:
            return Nil()
        elif len(terms) == 1:
            return terms[0]
        else:
            # 多个 term 组成管道
            return Pipeline(terms)


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
