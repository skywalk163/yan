"""
言语言语法分析器
"""

from typing import List, Optional, Set, Any, Tuple, Union
from lexer import Token, TokenType, Lexer
from nodes import *
from module_system import ImportNode, ExportNode
from error_formatter import ErrorFormatter, ErrorContext as FormattedErrorContext
from error_suggestions import ErrorSuggestionGenerator

# 全局用户动词集合
_global_user_verbs = set()


class ParserError(Exception):
    _formatter = ErrorFormatter(use_color=True)
    _suggester = ErrorSuggestionGenerator()
    
    def __init__(self, message: str, line: int, col: int, source: str = None, suggestion: str = None):
        self.message = message
        self.line = line
        self.col = col
        self.source = source
        self.suggestion = suggestion
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        source_lines = []
        if self.source:
            source_lines = self.source.split('\n')
        
        context = FormattedErrorContext(
            error_type="语法错误",
            file_path="未知文件",
            line=self.line,
            column=self.col,
            end_column=self.col + 1,
            source_lines=source_lines,
            message=self.message,
            suggestion=self.suggestion
        )
        
        return self._formatter.format(context)


class Parser:
    """语法分析器"""
    
    # 关键字
    VERBS = {
        # 算术运算
        '加', '减', '乘', '除', '模', '幂', '绝对', '负',
        # 比较运算
        '大', '小', '等', '不等',
        # 逻辑运算
        '且', '或', '非',
        # 列表操作
        '列', '典', '序', '对',
        '首', '余', '入', '长', '添', '连', '含', '空', '范围',
        # 高阶函数
        '皆', '只', '归', '潜',
        # IO
        '印', '读', '写',
        # 控制流
        '若', '则', '否则', '定', '函', '返回', '行', '无',
        '当', '遍历', '于',
        # 类型检查
        '是数', '是串', '是表', '是函', '是真', '是空', '类型',
        # 测试框架
        '套', '测',
    }
    
    ADVERBS = {'潜'}  # 潜 is the only true adverb that modifies verbs
    VARARGS = {'列', '典', '序'}
    INFIX_VERBS = {'加', '减', '乘', '除', '模', '幂',
                   '大', '小', '等', '不等',
                   '且', '或', '连', '含',
                   '包含', '开头是', '结尾是'}

    # 二元中缀动词：只接受2个参数
    BINARY_INFIX = {'加', '减', '乘', '除', '模', '幂', '大', '小', '等', '不等'}

    # 固定元数的前缀动词
    PREFIX_VERB_ARITY = {
        '加': 2, '减': 2, '乘': 2, '除': 2, '模': 2, '幂': 2,
        '绝对': 1, '负': 1,
        '大': 2, '小': 2, '等': 2, '不等': 2,
        '且': 2, '或': 2, '非': 1,
        '列': -1, '典': -1, '序': -1, '对': 2,
        '首': 1, '余': 1, '入': 2, '长': 1, '添': 2, '连': 2, '含': 2, '空': 1, '范围': 1,
        '皆': 2, '只': 2, '归': 2, '潜': 1,
        '印': -1, '读': 1, '写': 2,
        '返回': 1, '行': 1, '无': 0,
    }

    def __init__(self, use_global_verbs: bool = False):
        self.tokens: List[Token] = []
        self.pos: int = 0
        self.source: str = ""
        self.use_global_verbs = use_global_verbs
        
        # 用户定义动词的元数
        self.user_verb_arity: Dict[str, int] = {}
        
        # 块栈，用于跟踪当前块的状态
        self.block_stack = []

    def parse(self, tokens: List[Token], source: str = "") -> Program:
        """解析 token 流"""
        self.tokens = tokens
        self.pos = 0
        self.source = source
        
        statements = []
        while not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)

    def _current(self) -> Token:
        """获取当前 token"""
        return self.tokens[self.pos]

    def _peek(self, offset: int = 0) -> Token:
        """查看指定偏移的 token"""
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return Token(TokenType.EOF, None, 0, 0)
        return self.tokens[idx]

    def _is_at_end(self) -> bool:
        """是否到达末尾"""
        return self._current().type == TokenType.EOF

    def _advance(self) -> Token:
        """前进到下一个 token 并返回当前 token"""
        current = self._current()
        self.pos += 1
        return current

    def _match(self, *types: TokenType) -> bool:
        """匹配指定类型的 token"""
        for t in types:
            if self._current().type == t:
                self._advance()
                return True
        return False

    def _check_word(self, word: str) -> bool:
        """检查当前 token 是否是指定的词"""
        return self._current().type == TokenType.WORD and self._current().value == word

    def _expect(self, token_type: TokenType, message: str = ""):
        """期望特定类型的 token"""
        if self._current().type == token_type:
            return self._advance()
        raise self._create_error(message or f"期望 {token_type.name}")

    def _create_error(self, message: str, suggestion: str = None) -> ParserError:
        """创建语法错误"""
        return ParserError(message, self._current().line, self._current().col, self.source, suggestion)

    def _parse_statement(self, consume_dot: bool = True) -> Optional[Node]:
        if self._match(TokenType.DOT, TokenType.SEMI):
                return None

        # 模块语句
        if self._check_word('引'):
            stmt = self._parse_import_node()
            if consume_dot:
                self._match(TokenType.DOT, TokenType.SEMI)
            return stmt
        
        if self._check_word('出'):
            stmt = self._parse_export_node()
            if consume_dot:
                self._match(TokenType.DOT, TokenType.SEMI)
            return stmt
        
        if self._check_word('定'):
            result = self._parse_define()
            if consume_dot:
                self._match(TokenType.DOT, TokenType.SEMI)
            return result

        if self._check_word('测'):
            return self._parse_test()

        if self._check_word('套'):
            return self._parse_test_suite()

        # 表达式语句
        expr = self._parse_expression()
        if consume_dot:
            self._match(TokenType.DOT, TokenType.SEMI)
        return expr

    def _parse_import_node(self) -> ImportNode:
        """解析导入语句：引 "path" [为 alias] [取 name1, name2]"""
        self._advance()  # 消耗 '引'
        
        if self._current().type != TokenType.STR:
            raise self._create_error(
                "导入语句需要模块路径字符串",
                self._current().line, self._current().col
            )
        
        path = self._advance().value
        
        alias = None
        selective = []
        
        # 检查是否有 '为' 别名
        if self._check_word('为'):
            self._advance()
            if self._current().type != TokenType.WORD:
                raise self._create_error(
                    "别名需要是标识符",
                    self._current().line, self._current().col
                )
            alias = self._advance().value
        
        # 检查是否有 '取' 选择性导入
        if self._check_word('取'):
            self._advance()
            
            # 解析导入列表
            while not self._is_at_end():
                if self._current().type == TokenType.WORD:
                    selective.append(self._advance().value)
                elif self._current().type == TokenType.COMMA:
                    self._advance()
                elif self._current().type == TokenType.DOT or self._current().type == TokenType.SEMI:
                    break
                else:
                    raise self._create_error("导入列表语法错误")
        
        return ImportNode(path=path, alias=alias, selective=selective)

    def _parse_export_node(self) -> ExportNode:
        """解析导出语句：出 name1, name2, ..."""
        self._advance()  # 消耗 '出'
        
        names = []
        
        # 解析导出列表
        while not self._is_at_end():
            if self._current().type == TokenType.WORD:
                names.append(self._advance().value)
            elif self._current().type == TokenType.COMMA:
                self._advance()
            elif self._current().type == TokenType.DOT or self._current().type == TokenType.SEMI:
                break
            else:
                raise self._create_error("导出列表语法错误")
        
        return ExportNode(names=names)

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
            raise self._create_error("期望标识符")
        
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
        """解析 lambda 表达式：函 参数：体 或 函 参数 体。"""
        self._advance()  # 消耗 '函'
        
        # 收集参数（连续的 WORD，直到遇到 '：' 或其他动词）
        params = []
        has_varargs = False
        
        # 如果下一个 token 是冒号，则没有参数
        if self._current().type == TokenType.COLON:
            pass
        else:
            # 收集参数
            while self._current().type == TokenType.WORD or self._current().type == TokenType.ELLIPSIS:
                # 检查是否是省略号（可变参数）
                if self._current().type == TokenType.ELLIPSIS:
                    self._advance()  # 消耗 '...'
                    has_varargs = True
                    continue
                # 检查是否是关键字（可能是开始函数体的动词）
                if self._current().value in self.VERBS and self._current().value not in {'返回'}:
                    break
                params.append(self._advance().value)
        
        # 期望冒号或开始函数体
        if self._current().type == TokenType.COLON:
            self._advance()
            body = self._parse_block()
        else:
            # 单行函数体：解析一个表达式
            body = self._parse_expression()
        
        return Lambda(params, body, varargs=has_varargs)

    def _parse_block(self) -> Block:
        """解析代码块"""
        statements = []
        
        while not self._is_at_end():
            # 检查块结束条件
            if self._check_word('。') or self._check_word('；'):
                break
            if self._check_word('否则'):
                break
            if self._check_word('套'):
                break
            if self._check_word('定'):
                break
            if self._check_word('测'):
                break
            if self._check_word('当'):
                break
            if self._check_word('遍历'):
                break
            
            stmt = self._parse_statement(consume_dot=False)
            if stmt:
                statements.append(stmt)
        
        return Block(statements)

    def _parse_expression(self) -> Node:
        """解析表达式"""
        return self._parse_call()

    def _parse_call(self) -> Node:
        """解析函数调用"""
        # 先解析第一个原子
        verb = self._parse_atom()
        
        # 如果不是动词，返回原子
        if not isinstance(verb, Word):
            return verb
        
        verb_name = verb.name
        
        # 检查是否是关键字动词
        if verb_name not in self.VERBS and verb_name not in self.user_verb_arity:
            # 不是动词，作为变量引用返回
            return verb
        
        # 收集参数
        args = []
        
        while not self._is_at_end():
            # 检查结束条件
            if self._current().type == TokenType.DOT:
                break
            if self._current().type == TokenType.SEMI:
                break
            if self._current().type == TokenType.COLON:
                # 块开始标记，可能是条件语句或循环
                break
            if self._check_word('否则'):
                break
            
            # 原子 + 可能的中缀动词
            arg = self._parse_atom()

            # 中缀动词延续：仅当参数是裸原子且外层动词不是固定参数的内置动词时
            # （如余/首等有固定元数的内置动词，参数不应参与中缀延续，
            #  否则会抢夺后续参数的位置）
            # 对于已知元数的用户定义动词，仅在当前参数是最后一个参数时允许中缀延续
            # 这样 "阶乘 n 减 1" 中 n 能延续中缀得到 阶乘(n-1)，
            # 而 "扩展 新带 加 头 1" 中新带不会延续中缀，加作为第二个参数
            if (isinstance(arg, (Num, Str, Word)) and
                verb_name not in self.PREFIX_VERB_ARITY and
                (verb_name not in self.user_verb_arity or
                 len(args) + 1 >= self.user_verb_arity[verb_name])):
                while (self._current().type == TokenType.WORD and
                       self._current().value in self.INFIX_VERBS):
                    infix_verb = self._advance().value
                    right = self._parse_term()
                    arg = Call(Word(infix_verb), [arg, right])

            args.append(arg)

            # 对于已知元数的前缀动词，达到元数后停止收集
            # 注意：-1 表示可变参数，需要特殊处理
            if verb_name in self.PREFIX_VERB_ARITY:
                arity = self.PREFIX_VERB_ARITY[verb_name]
                if arity > 0 and len(args) >= arity:
                    break
                # arity == -1 表示可变参数，不停止收集

            # 对于已知元数的用户定义函数，达到元数后停止收集
            if verb_name in self.user_verb_arity and len(args) >= self.user_verb_arity[verb_name]:
                break

        # 处理特殊动词
        if verb_name == '定':
            # 变量定义：定 名称 = 值
            if len(args) >= 2 and args[1] == '=':
                name = args[0].name if isinstance(args[0], Word) else str(args[0])
                value = args[2] if len(args) > 2 else None
                return Define(name, value)
        
        # 如果没有参数，返回动词本身（可能是变量引用）
        if len(args) == 0:
            return verb
        
        return Call(verb, args)

    def _parse_term(self) -> Node:
        """解析项"""
        # 导入语句
        if self._check_word('导入'):
            return self._parse_import_statement()
        
        # 导出语句
        if self._check_word('导出'):
            return self._parse_export_statement()
        
        # 条件语句
        if self._check_word('若'):
            return self._parse_if()
        
        # 循环语句
        if self._check_word('遍历'):
            return self._parse_foreach()
        
        if self._check_word('当'):
            return self._parse_while()
        
        # 函数定义
        if self._check_word('函'):
            return self._parse_lambda()
        
        # 测试框架
        if self._check_word('测'):
            return self._parse_test()
        
        if self._check_word('套'):
            return self._parse_test_suite()
        
        # 其他：解析原子
        return self._parse_atom()

    def _parse_atom(self) -> Node:
        """解析原子（数字、字符串、变量、列表字面量）"""
        token = self._current()
        
        if token.type == TokenType.NUM:
            self._advance()
            return Num(token.value)
        
        if token.type == TokenType.STR:
            self._advance()
            return Str(token.value)
        
        if token.type == TokenType.WORD:
            word = token.value
            self._advance()
            
            # 处理布尔值和空值
            if word == '真':
                return Bool(True)
            if word == '假':
                return Bool(False)
            if word == '空':
                return Nil()
            
            return Word(word)
        
        if token.type == TokenType.QUOTE:
            self._advance()
            quoted = self._parse_expression()
            return Quote(quoted)
        
        # 列表字面量：列 元素1 元素2 ...
        if self._check_word('列'):
            self._advance()
            elements = []
            while not self._is_at_end():
                if self._current().type == TokenType.DOT:
                    break
                if self._current().type == TokenType.SEMI:
                    break
                if self._check_word('。'):
                    break
                elements.append(self._parse_expression())
            return ListLiteral(elements)
        
        # 字典字面量：典 键1 值1 键2 值2 ...
        if self._check_word('典'):
            self._advance()
            elements = []
            while not self._is_at_end():
                if self._current().type == TokenType.DOT:
                    break
                if self._current().type == TokenType.SEMI:
                    break
                if self._check_word('。'):
                    break
                elements.append(self._parse_expression())
            return DictLiteral(elements)
        
        # 数学表达式
        if token.type == TokenType.MATH:
            self._advance()
            return MathExpr(token.value)
        
        # Python 代码块
        if token.type == TokenType.PYTHON:
            self._advance()
            return PythonCode(token.value)
        
        raise self._create_error(f"无法解析: {token}")

    def _parse_if(self) -> If:
        """解析条件语句：若 条件 则：分支。否则：分支。"""
        line = self._current().line
        col = self._current().col
        self._advance()  # 消耗 '若'

        # 解析条件：使用 _parse_expr_until 可以处理函数调用和中缀表达式
        cond = self._parse_expr_until({'则'})

        # 期望 '则'（检查值和类型）
        if (self._current().type != TokenType.WORD or 
            self._current().value != '则'):
            raise self._create_error("期望 '则'")
        self._advance()  # 消耗 '则'

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
        # 跳过可能的句号（仅在后面跟着 否则 时才消耗，否则留给外层块处理）
        if self._current().type == TokenType.DOT:
            peek = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if peek and peek.type == TokenType.WORD and peek.value == '否则':
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

    def _parse_while(self) -> While:
        """解析当循环：当 条件 则：循环体 或 当 条件：循环体。"""
        self._advance()  # 消耗 '当'

        # 解析条件（单个 term，可能是中缀表达式）
        cond = self._parse_atom()

        # 处理中缀动词
        while (self._current().type == TokenType.WORD and
               self._current().value in self.INFIX_VERBS):
            # 遇到冒号或'则'时停止
            if self._current().type == TokenType.COLON:
                break
            if self._current().type == TokenType.WORD and self._current().value == '则':
                break
            infix_verb = self._advance().value
            right = self._parse_atom()
            cond = Call(Word(infix_verb), [cond, right])

        # 期望 '：' 或 '则'（块开始）
        if self._current().type == TokenType.WORD and self._current().value == '则':
            self._advance()  # 消耗 '则'
            # 期望 '：'
            if self._current().type != TokenType.COLON:
                raise self._create_error("期望 '：' 开始循环体")
        elif self._current().type != TokenType.COLON:
            raise self._create_error("期望 '：' 或 '则' 开始循环体")
        self._advance()  # 消耗 '：'

        # 解析循环体
        body = self._parse_block()

        return While(cond, body)

    def _parse_foreach(self) -> ForEach:
        """解析遍历循环：遍历 变量 于 列表：循环体。"""
        self._advance()  # 消耗 '遍历'
        
        # 解析变量名
        if self._current().type != TokenType.WORD:
            raise self._create_error("期望变量名")
        var = self._advance().value
        
        # 期望 '于'
        if not self._check_word('于'):
            raise self._create_error("期望 '于'")
        self._advance()  # 消耗 '于'
        
        # 解析列表表达式
        iterable = self._parse_expression()
        
        # 期望 '：'
        if self._current().type != TokenType.COLON:
            raise self._create_error("期望 '：'")
        self._advance()  # 消耗 '：'
        
        # 解析循环体
        body = self._parse_block()
        
        return ForEach(var, iterable, body)

    def _parse_test(self) -> Test:
        """解析测试用例：测 "名称"：测试代码。"""
        self._advance()  # 消耗 '测'
        
        # 解析测试名称（字符串）
        if self._current().type != TokenType.STR:
            raise self._create_error("期望测试名称（字符串）")
        name = self._advance().value
        
        # 期望冒号
        if self._current().type != TokenType.COLON:
            raise self._create_error("期望 '：'")
        self._advance()
        
        # 解析测试体（多个语句）
        body = []
        while not self._is_at_end():
            if self._current().type == TokenType.DOT:
                break
            stmt = self._parse_statement(consume_dot=False)
            if stmt:
                body.append(stmt)
        
        return Test(name, body)

    def _parse_test_suite(self) -> TestSuite:
        """解析测试套件：套 "名称"：测试用例。"""
        self._advance()  # 消耗 '套'
        
        # 解析套件名称（字符串）
        if self._current().type != TokenType.STR:
            raise self._create_error("期望套件名称（字符串）")
        name = self._advance().value
        
        # 期望冒号
        if self._current().type != TokenType.COLON:
            raise self._create_error("期望 '：'")
        self._advance()
        
        # 解析测试用例和设置/清理代码
        tests = []
        setup = None
        teardown = None
        
        while not self._is_at_end():
            if self._current().type == TokenType.DOT:
                break
            if self._check_word('测'):
                tests.append(self._parse_test())
                # 跳过测试后的句号
                if self._current().type == TokenType.DOT:
                    self._advance()
            elif self._check_word('设置'):
                # 设置代码
                self._advance()
                if self._current().type == TokenType.COLON:
                    self._advance()
                setup = self._parse_block()
            elif self._check_word('清理'):
                # 清理代码
                self._advance()
                if self._current().type == TokenType.COLON:
                    self._advance()
                teardown = self._parse_block()
            elif self._check_word('套'):
                break

            # 其他语句，跳过
            self._advance()

        return TestSuite(name, tests, setup, teardown)

    def _parse_expr_until(self, stop_words: Set[str]) -> Node:
        """解析表达式，直到遇到指定的停止词"""
        # 收集所有 term 直到遇到停止词
        terms = []
        while not self._is_at_end():
            if self._current().type == TokenType.DOT:
                break
            if self._current().type == TokenType.WORD and self._current().value in stop_words:
                break
            
            term = self._parse_term()
            terms.append(term)
        
        # 如果只有一个 term，直接返回
        if len(terms) == 1:
            return terms[0]
        
        # 否则尝试构建调用表达式
        # 这是一个简化的处理，实际应该处理中缀表达式
        if len(terms) >= 3 and isinstance(terms[1], Word):
            # 可能是中缀表达式：左 动词 右
            return Call(terms[1], [terms[0], terms[2]])
        
        # 默认返回第一个 term
        return terms[0] if terms else Nil()

    def _parse_block_until(self, stop_words: Set[str], always_block: bool = False) -> Node:
        """解析块，直到遇到指定的停止词"""
        statements = []
        while not self._is_at_end():
            if self._current().type == TokenType.DOT:
                self._advance()
                break
            if self._current().type == TokenType.WORD and self._current().value in stop_words:
                break
            
            stmt = self._parse_statement(consume_dot=False)
            if stmt:
                statements.append(stmt)
        
        # 如果只有一个语句且不是块，且不要求总是块，则返回单个表达式
        if len(statements) == 1 and not always_block:
            return statements[0]
        
        return Block(statements)

    def _parse_import_statement(self) -> Import:
        """解析导入语句：导入 模块名 或 导入 名称1 名称2 于 模块名"""
        self._advance()  # 消耗 '导入'
        
        # 收集导入的名称
        names = []
        while (not self._is_at_end() and 
               self._current().type == TokenType.WORD and
               not self._check_word('于') and
               not self._check_word('。') and
               not self._check_word('；')):
            names.append(self._advance().value)
        
        # 检查是否有 '于' 关键字
        module_name = None
        if self._check_word('于'):
            self._advance()  # 消耗 '于'
            module_name = self._advance().value
        else:
            # 简单导入：导入 模块名
            module_name = names[0] if names else ''
            names = None
        
        # 消耗句号或分号
        if self._check_word('。'):
            self._advance()
        elif self._check_word('；'):
            self._advance()
        
        return Import(module_name=module_name, names=names)
    
    def _parse_export_statement(self) -> Export:
        """解析导出语句：导出 名称1 名称2 ..."""
        self._advance()  # 消耗 '导出'
        
        names = []
        while (not self._is_at_end() and 
               self._current().type == TokenType.WORD and
               not self._check_word('。') and
               not self._check_word('；')):
            names.append(self._advance().value)
        
        # 消耗句号或分号
        if self._check_word('。'):
            self._advance()
        elif self._check_word('；'):
            self._advance()
        
        return Export(names=names)


# =====================================
# 副词处理
# =====================================

def process_adverbs(ast: Program) -> Program:
    """处理副词（如 潜）"""
    return ast


def add_global_user_verb(name: str):
    """添加全局用户动词"""
    _global_user_verbs.add(name)


if __name__ == "__main__":
    # 简单测试
    lexer = Lexer()
    source = "定平方=函x乘x x。"
    tokens = lexer.tokenize(source)
    parser = Parser()
    ast = parser.parse(tokens, source)
    print(f"AST: {ast}")
