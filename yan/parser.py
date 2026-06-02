"""
言语言语法分析器 - 最终版
"""

from typing import Dict, List, Optional, Set
try:
    from .tokens import Token, TokenType
    from .nodes import *
except ImportError:
    from tokens import Token, TokenType
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
    
    def current_indent(self) -> int:
        """获取当前缩进级别"""
        if self.is_empty():
            return 0
        return self._stack[-1]['indent']


class Parser:
    """语法分析器"""

    # 优化：使用 frozenset 提高查找性能
    ADVERBS = frozenset({'潜'})  # 潜 is the only true adverb that modifies verbs
    VARARGS = frozenset({'列', '列表', '典', '序'})
    INFIX_VERBS = frozenset({
        '加', '减', '乘', '除',
        '大', '小',
        '相加', '相减', '相乘', '相除', '取余', '幂',
        '大于', '小于', '等于', '不等',
        '并且', '或者', '连', '含',
        '包含', '开头是', '结尾是'
    })

    # 二元中缀动词：只接受2个参数
    BINARY_INFIX = frozenset({'加', '减', '乘', '除', '大', '小', '大于', '大等于', '小于', '小等于', '等于', '不等于', '不等', '并且', '或者'})
    
    # 条件关键字集合
    CONDITION_KEYWORDS = frozenset({'如果', '那么', '否则', '真', '假', '空', '定义', '函数'})
    
    # 块开始关键字
    BLOCK_START_KEYWORDS = frozenset({'如果', '遍历', '当满足', '当时', '测', '套'})
    
    BUILTIN_VERBS = frozenset({
        '加', '减', '乘', '除', '相加', '相减', '相乘', '相除', '取余', '幂', '绝对', '负',
        '大于', '大于', '大等于', '小于', '小于', '小等于', '等于', '不等于', '不等',
        '并且', '或者', '非也',
        '首个', '其余', '入', '取', '设', '长', '添', '连', '含', '空',
        '映射', '过滤', '归约', '皆', '只', '归', '潜',
        '输出', '读', '写', '行', '读行', '印', '印数', '印浮',
        '如果', '那么', '否则', '若', '定义', '函数', '返回',
        '遍历', '于', '当满足', '当时',
        '列表', '列', '典', '序', '范围',
        # 字符串库
        '长度', '连接', '分割', '替换', '截取', '小写', '大写',
        '查找', '包含', '去空', '开头是', '结尾是',
        # 数学库
        '正弦', '余弦', '正切', '反正弦', '反余弦', '反正切',
        '指数', '对数', '对数10', '开方', '取整', '进位', '四舍五入',
        '随机', '随机整数', '圆周率', '自然常数',
        # 时间库
        '当前时间', '日期', '时间', '日期时间', '格式化时间', '睡眠',
        # 文件库
        '读文件', '写文件', '追加文件', '存在', '是文件', '是目录',
        '列目录', '建目录', '删文件', '删目录', '当前目录',
        '文件名', '目录名', '扩展名',
        # 类型检查
        '是数', '是串', '是表', '是函数', '是真', '是空', '类型',
        # 新增列表操作
        '反转', '排序', '最大', '最小', '求和', '计数',
        # 新增字典操作
        '典', '键', '值', '项', '删键',
        # 正则表达式
        '匹配',
        # 表达式求值
        '求值',
        # 模块系统
        '导入', '模块', '导出', '从',
        # 结构体系统
        '结构', '类型', '字段',
    })

    # 前缀动词的元数：指定需要收集的参数数量
    # 超出元数的非动词 token 不会被作为当前动词的参数
    PREFIX_VERB_ARITY = {
        '入': 2,   # 入 collection index
        '取': 2,   # 取 list index
        '设': 3,   # 设 list index value
        '首个': 1,   # 首个 list -> first
        '其余': 1,   # 其余 list -> rest
        '长': 1,   # 长 list -> length
        '非也': 1,   # 非也 bool -> not
        '空': 1,   # 空 list -> is_empty
        '负': 1,   # 负 num -> negate
        '绝对': 1,
        '正弦': 1, '余弦': 1, '正切': 1,
        '反正弦': 1, '反余弦': 1, '反正切': 1,
        '指数': 1, '对数': 1, '对数10': 1, '开方': 1,
        '取整': 1, '进位': 1, '四舍五入': 1,
        '随机': 0, '随机整数': 2,
        '圆周率': 0, '自然常数': 0,
        '是数': 1, '是串': 1, '是表': 1, '是函数': 1, '是真': 1, '是空': 1, '类型': 1,
        '长度': 1, '小写': 1, '大写': 1, '去空': 1,
        '返回': 1,  # 返回 value
        # 新增列表操作
        '反转': 1, '排序': 1, '最大': 1, '最小': 1, '求和': 1, '计数': 2,
        # 新增字典操作
        '键': 1, '值': 2, '项': 1, '删键': 2,
        # 表达式求值
        '求值': 1,
        # 字符串拼接
        '连': 2,
    }

    def __init__(self, use_global_verbs: bool = False, syntax_version: int = 2):
        self.tokens: List[Token] = []
        self.pos: int = 0
        self.user_verbs: Set[str] = set()
        self.user_verb_arity: Dict[str, int] = {}
        self.use_global_verbs = use_global_verbs
        self.block_stack = BlockStack()
        self.syntax_version = syntax_version
        # 优化：缓存动词集合以提高查找性能
        self._verbs_cache = None

    @property
    def VERBS(self) -> Set[str]:
        """合并内置动词和用户定义动词"""
        if self._verbs_cache is None:
            if self.use_global_verbs:
                self._verbs_cache = self.BUILTIN_VERBS | _global_user_verbs | self.user_verbs
            else:
                self._verbs_cache = self.BUILTIN_VERBS | self.user_verbs
        return self._verbs_cache

    def _reset_verbs_cache(self):
        """重置动词缓存（在收集新用户动词后调用）"""
        self._verbs_cache = None

    def parse(self, tokens: List[Token]) -> Program:
        """解析源码，根据语法版本选择解析方法"""
        if self.syntax_version >= 2:
            return self.parse_v2(tokens)
        else:
            return self.parse_v1(tokens)

    def parse_v1(self, tokens: List[Token]) -> Program:
        """v1 语法解析：传统语法，支持句号结束语句"""
        self.tokens = tokens
        self.pos = 0
        self.user_verbs = set()
        self.use_global_verbs = True  # v1 语法支持全局用户定义函数
        self._reset_verbs_cache()  # 重置缓存

        # 第一遍：收集用户定义的函数名
        self._collect_user_verbs()
        self._reset_verbs_cache()  # 收集完成后重置，下次访问 VERBS 时重建

        # 第二遍：正常解析
        self.pos = 0
        statements = []

        while not self._is_at_end():
            # 跳过 DEDENT tokens（它们是块结束的标记）
            while self._current().type == TokenType.DEDENT:
                self._advance()
            if self._is_at_end():
                break
            stmt = self._parse_statement_v2()  # 使用 v2 的语句解析
            if stmt:
                statements.append(stmt)
            # v1 语法：跳过语句后的句号
            if not self._is_at_end() and self._current().type == TokenType.DOT:
                self._advance()

        return Program(statements)

    def parse_v2(self, tokens: List[Token]) -> Program:
        """v2 语法解析：支持无句号代码块，代码块通过缩进结束"""
        self.tokens = tokens
        self.pos = 0
        self.user_verbs = set()
        self._reset_verbs_cache()

        # 第一遍：收集用户定义的函数名
        self._collect_user_verbs()
        self._reset_verbs_cache()

        # 第二遍：正常解析
        self.pos = 0
        self.current_indent = 0
        self.indent_stack = [0]
        statements = []

        while not self._is_at_end():
            # 跳过空行和 DEDENT
            while self._current().type in {TokenType.DEDENT, TokenType.DOT}:
                self._advance()
            if self._is_at_end():
                break

            # 检测缩进变化
            current_indent = self._get_indent_level()

            if current_indent < self.indent_stack[-1]:
                # 缩进减少：代码块结束，调整缩进栈但不退出循环
                while self.indent_stack and self.indent_stack[-1] > current_indent:
                    self.indent_stack.pop()
                continue  # 继续处理下一个 token，不要 break

            # 解析语句
            stmt = self._parse_statement_v2()
            if stmt:
                statements.append(stmt)

        return Program(statements)

    def _get_indent_level(self) -> int:
        """获取当前行的缩进级别"""
        if self._current().type == TokenType.INDENT:
            return int(self._current().value)
        return 0

    def _is_empty_line(self) -> bool:
        """检查当前是否为空行"""
        tok = self._current()
        return tok.type in {TokenType.DOT, TokenType.SEMI}

    def _parse_statement_v2(self) -> Optional[Node]:
        """解析 v2 语法的语句"""
        # 跳过 INDENT tokens
        while self._current().type == TokenType.INDENT:
            self._advance()

        if self._is_at_end():
            return None

        token = self._current()

        if self._check_word('如果') or self._check_word('当') or self._check_word('若'):
            return self._parse_if_v2()

        if self._check_word('遍历'):
            return self._parse_foreach_v2()

        if self._check_word('当满足') or self._check_word('当时'):
            return self._parse_while_v2()

        if token.type == TokenType.WORD and (token.value.startswith('定义') or token.value == '定'):
            return self._parse_define_v2()

        if self._check_word('测'):
            return self._parse_test_v2()

        if self._check_word('套'):
            return self._parse_test_suite_v2()

        if self._check_word('导入'):
            return self._parse_import()

        if self._check_word('导出'):
            return self._parse_export()

        if self._check_word('结构'):
            return self._parse_struct_def()

        # 跳过 INDENT token（在代码块内部，缩进已由块解析器处理）
        if self._current().type == TokenType.INDENT:
            self._advance()
            return self._parse_statement_v2()

        expr = self._parse_expression()
        # v2 语法：语句后不需要句号
        return expr

    def _parse_if_v2(self) -> If:
        """解析 v2 语法的 if 语句"""
        # 检查是否以 '如果' 开头（如 "如果真那么1"）
        if self._check_word('如果'):
            self._advance()  # 消耗 '如果'
        elif self._check_word('当'):
            self._advance()  # 消耗 '当'
        elif self._check_word('若'):
            # v1 语法的条件表达式
            return self._parse_if()  # 使用 v1 的条件解析逻辑

        # 解析条件，遇到冒号或换行时停止
        cond = self._parse_expression({TokenType.COLON})

        # 消耗冒号（如果有）
        if self._current().type == TokenType.COLON:
            self._advance()

        # 解析 then 分支
        then_block = self._parse_block_v2()

        # 检查 else
        elif_clauses = []
        else_block = None

        while not self._is_at_end():
            # 跳过空行
            if self._is_empty_line():
                self._advance()
                continue
            if self._current().type == TokenType.INDENT:
                self._advance()
                continue

            if self._check_word('否则当') or (self._current().type == TokenType.WORD and
                                               self._current().value == '否则' and
                                               self._peek(1).type == TokenType.WORD and
                                               self._peek(1).value == '当'):
                # 否则当
                self._advance()  # 消耗 '否则'
                self._advance()  # 消耗 '当'
                elif_cond = self._parse_expression()
                elif_body = self._parse_block_v2()
                elif_clauses.append({'condition': elif_cond, 'body': elif_body})
            elif self._check_word('否则'):
                # 否则
                self._advance()  # 消耗 '否则'
                else_block = self._parse_block_v2()
                break
            else:
                break

        return If(cond, then_block, else_block)

    def _parse_block_v2(self, stop_tokens: Optional[Set[TokenType]] = None) -> Node:
        """解析 v2 语法的代码块（通过缩进判断结束）
        
        Args:
            stop_tokens: 可选的停止 token 类型集合，遇到这些 token 时停止解析
        """
        statements = []

        # 获取块开始时的缩进
        block_indent = self._get_indent_level()
        
        # 消耗 COLON（如果存在）
        if self._current().type == TokenType.COLON:
            self._advance()
        
        # 消耗 INDENT token
        if self._current().type == TokenType.INDENT:
            self._advance()

        # 维护当前缩进级别
        current_indent = block_indent

        while not self._is_at_end():
            # 检查是否遇到停止 token（如括号内的 lambda 表达式）
            if stop_tokens and self._current().type in stop_tokens:
                break
                
            # 处理缩进变化
            if self._current().type == TokenType.INDENT:
                current_indent += int(self._current().value)
                self._advance()
                continue
            
            if self._current().type == TokenType.DEDENT:
                current_indent -= int(self._current().value)
                self._advance()
                
                # 检查是否退出当前块
                if current_indent < block_indent:
                    break
                continue

            # 跳过空行（只有句号的行）
            if self._is_empty_line():
                self._advance()
                continue

            # 解析语句
            stmt = self._parse_statement_v2()
            if stmt:
                statements.append(stmt)

        if len(statements) == 0:
            return Nil()
        elif len(statements) == 1:
            return statements[0]
        else:
            return Block(statements)

    def _is_at_block_end_v2(self, block_indent: int) -> bool:
        """检查是否到达 v2 代码块结束"""
        if self._is_at_end():
            return True

        # 处理 DEDENT token
        if self._current().type == TokenType.DEDENT:
            self._advance()  # 消耗 DEDENT
            # DEDENT 后需要重新检查
            return self._is_at_block_end_v2(block_indent)

        # 跳过空行
        if self._is_empty_line():
            self._advance()
            return False

        # 如果 block_indent 为 0（顶层代码块），只有文件结束才结束
        if block_indent == 0:
            return False

        current_indent = self._get_indent_level()
        return current_indent <= block_indent

    def _parse_foreach_v2(self) -> ForEach:
        """解析 v2 语法的遍历循环"""
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
        iterable = self._parse_iterable()

        # 消耗冒号（如果有）
        if self._current().type == TokenType.COLON:
            self._advance()

        # 解析循环体
        body = self._parse_block_v2()

        return ForEach(var, iterable, body)

    def _parse_while_v2(self) -> While:
        """解析 v2 语法的当循环"""
        self._advance()  # 消耗 '当满足' 或 '当时'

        # 解析条件表达式
        cond = self._parse_expression()

        # 消耗冒号（如果有）
        if self._current().type == TokenType.COLON:
            self._advance()

        # 解析循环体
        body = self._parse_block_v2()

        return While(cond, body)

    def _parse_define_v2(self) -> Define:
        """解析 v2 语法的定义语句"""
        # 消耗 '定义' 关键字（可能与变量名合并，如 "定义阶乘"）
        first_tok = self._advance()

        # 提取变量名
        if first_tok.value.startswith('定义') and len(first_tok.value) > 2:
            var_name = first_tok.value[2:]
        else:
            var_name = None

        # 收集连续的 WORD 作为名称
        name_parts = [] if var_name is None else [var_name]

        while self._current().type == TokenType.WORD:
            if self._current().value == '定义':
                break
            next_tok = self._peek(1)
            if next_tok.type == TokenType.EQUALS:
                name_parts.append(self._advance().value)
                break
            name_parts.append(self._advance().value)

        if not name_parts:
            raise ParserError("期望标识符", self._current().line, self._current().col)

        name = ''.join(name_parts)
        self._expect(TokenType.EQUALS, "期望 '='")

        if self._check_word('函数') or self._check_word('函'):
            value = self._parse_lambda_v2(stop_tokens={TokenType.DOT})
            if self.use_global_verbs:
                _global_user_verbs.add(name)
        else:
            value = self._parse_expression()

        return Define(name, value)

    def _parse_lambda_v2(self, stop_tokens: Optional[Set[TokenType]] = None) -> Lambda:
        """解析 v2 语法的 lambda 表达式
        
        Args:
            stop_tokens: 可选的停止 token 类型集合，遇到这些 token 时停止解析（用于括号内的 lambda）
        """
        self._advance()  # 消耗 '函数' 或 '函'

        params = []
        while (self._current().type == TokenType.WORD and
                # 如果下一个 token 是 COLON，即使当前是动词也作为参数
                (self._current().value not in self.VERBS or 
                 self._peek(1).type == TokenType.COLON) and
                self._current().value not in {'如果', '那么', '否则', '真', '假', '空', '定义', '函数'}):
            params.append(self._advance().value)

        # 检查并消耗冒号
        if self._current().type == TokenType.COLON:
            self._advance()

        # 检查是否是单行 lambda
        # 单行 lambda 的情况：
        # 1. 当前 token 是 INDENT（块开始），不是单行
        # 2. 当前 token 是 RPAREN（括号结束），是单行（空 body）
        # 3. 当前 token 是 COMMA 或 DOT，是单行
        # 4. 否则检查后续是否有 RPAREN、COMMA、DOT（可能跳过一些 token）
        has_stop = False
        if self._current().type == TokenType.INDENT:
            # 块结构的 lambda
            body = self._parse_block_v2(stop_tokens)
        elif self._current().type in {TokenType.RPAREN, TokenType.COMMA, TokenType.DOT}:
            # 单行 lambda，空 body 或简单表达式
            if stop_tokens and self._current().type in stop_tokens:
                body = Block([])
            else:
                body = self._parse_expression(stop_tokens)
                if body is None:
                    body = Block([])
        else:
            # 检查后续是否会遇到停止 token
            # 向前查找几个 token，看看是否有 RPAREN、COMMA、DOT
            for i in range(1, 10):  # 最多向前看 10 个 token
                peek_tok = self._peek(i)
                if peek_tok:
                    if peek_tok.type in {TokenType.RPAREN, TokenType.COMMA, TokenType.DOT}:
                        has_stop = True
                        break
                    # 如果遇到 INDENT，说明是块结构
                    if peek_tok.type == TokenType.INDENT:
                        break
            
            if has_stop:
                # 单行 lambda
                # 检查当前 token 是否已经是停止 token
                if stop_tokens and self._current().type in stop_tokens:
                    # 空 body
                    body = Block([])
                else:
                    body = self._parse_expression(stop_tokens)
                    # 如果返回 None，使用空 body
                    if body is None:
                        body = Block([])
            else:
                # 块结构的 lambda
                body = self._parse_block_v2(stop_tokens)
        
        return Lambda(params, body)

    def _parse_test_v2(self) -> Test:
        """解析 v2 语法的测试"""
        self._advance()  # 消耗 '测'

        if self._current().type != TokenType.STR:
            raise self._error("期望测试名称（字符串）")
        name = self._advance().value

        # 解析测试体
        body = self._parse_block_v2()

        return Test(name, body)

    def _parse_test_suite_v2(self) -> TestSuite:
        """解析 v2 语法的测试套件"""
        self._advance()  # 消耗 '套'

        if self._current().type != TokenType.STR:
            raise self._error("期望套件名称（字符串）")
        name = self._advance().value

        # 解析测试列表
        tests = []
        setup = None
        teardown = None

        while not self._is_at_end():
            if self._is_empty_line():
                self._advance()
                continue

            if self._check_word('前'):
                self._advance()
                setup = self._parse_block_v2()
                continue

            if self._check_word('后'):
                self._advance()
                teardown = self._parse_block_v2()
                continue

            if self._check_word('测'):
                test = self._parse_test_v2()
                tests.append(test)
                continue

            if self._check_word('套'):
                break

            self._advance()

        return TestSuite(name, tests, setup, teardown)

    def _collect_user_verbs(self):
        """第一遍扫描：收集所有用户定义的函数名及其参数数量"""
        pos = 0
        while pos < len(self.tokens):
            tok = self.tokens[pos]
            # 查找 "定 名称 = 函" 或 "定 名称 = {{...}}" 模式
            if tok.type == TokenType.WORD and tok.value in {'定义', '定'}:
                if pos + 2 < len(self.tokens):
                    name_tok = self.tokens[pos + 1]
                    eq_tok = self.tokens[pos + 2]
                    if name_tok.type == TokenType.WORD and eq_tok.type == TokenType.EQUALS:
                        # 检查是否是函数定义
                        if pos + 3 < len(self.tokens):
                            next_tok = self.tokens[pos + 3]
                            # 定 名称 = 函 或 定 名称 = 函数
                            if next_tok.type == TokenType.WORD and next_tok.value in {'函数', '函'}:
                                self.user_verbs.add(name_tok.value)
                                if self.use_global_verbs:
                                    _global_user_verbs.add(name_tok.value)
                                # 收集参数数量
                                arity = 0
                                p = pos + 4
                                while p < len(self.tokens):
                                    t = self.tokens[p]
                                    if t.type != TokenType.WORD:
                                        break
                                    if t.value in {'如果', '那么', '否则'}:
                                        break
                                    arity += 1
                                    p += 1
                                self.user_verb_arity[name_tok.value] = arity
                            # 定 名称 = {{...}} (Python 代码块)
                            # 注意：Python 代码块不一定是函数，可能是表达式
                            # 不应该自动添加到 user_verbs
                            # elif next_tok.type == TokenType.PYTHON:
                            #     self.user_verbs.add(name_tok.value)
                            #     if self.use_global_verbs:
                            #         _global_user_verbs.add(name_tok.value)
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
        """优化：直接使用集合查找"""
        return name in self.BUILTIN_VERBS or name in self.ADVERBS or name in self.user_verbs

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
                            TokenType.EQUALS, TokenType.COLON, TokenType.RPAREN}:
                break
            if tok.type == TokenType.WORD and tok.value in {'如果', '那么', '否则'}:
                break
            if tok.type == TokenType.WORD and tok.value in self.ADVERBS:
                break
            arg = self._parse_term()
            args.append(arg)
        return args

    def _parse_statement(self, consume_dot: bool = True) -> Optional[Node]:
        # 跳过 INDENT tokens（它们是块结构的标记，不是语句的一部分）
        while self._current().type == TokenType.INDENT:
            self._advance()
        
        # 如果遇到 DEDENT，返回 None（由调用者决定是否结束块）
        # 注意：不要消耗 DEDENT，让调用者处理
        if self._current().type == TokenType.DEDENT:
            return None
        
        if self._match(TokenType.DOT, TokenType.SEMI):
                return None

        # 检查是否以 '定义' 或 '定' 开头（处理 "定xxx" 或 "定义xxx" 形式的变量名）
        if (self._current().type == TokenType.WORD and 
            (self._current().value.startswith('定义') or self._current().value == '定')):
            result = self._parse_define()
            if consume_dot:
                self._match(TokenType.DOT, TokenType.SEMI)
            return result

        if self._check_word('测'):
            return self._parse_test()

        if self._check_word('套'):
            return self._parse_test_suite()

        expr = self._parse_expression()
        if consume_dot:
            self._match(TokenType.DOT, TokenType.SEMI)

        return expr

    def _parse_define(self) -> Define:
        # 消耗 '定义' 关键字（可能与变量名合并，如 "定义阶乘"）
        first_tok = self._advance()
        
        # 提取变量名：如果第一个 token 以 '定义' 开头，分离出变量名部分
        if first_tok.value.startswith('定义') and len(first_tok.value) > 2:
            var_name = first_tok.value[2:]  # 去掉 '定义' 前缀（两个字符）
        else:
            var_name = None
        
        # 收集连续的 WORD 作为名称（直到遇到 '='）
        name_parts = [] if var_name is None else [var_name]
        
        while self._current().type == TokenType.WORD:
            # 遇到关键字 '定义'，停止收集
            if self._current().value == '定义':
                break
            
            # 检查下一个是否是 '='
            next_tok = self._peek(1)
            if next_tok.type == TokenType.EQUALS:
                # 这是名称的最后一部分，消耗当前 token 并停止
                name_parts.append(self._advance().value)
                # 循环外会期望 '='
                break
            name_parts.append(self._advance().value)
        
        if not name_parts:
            raise ParserError("期望标识符", self._current().line, self._current().col)
        
        name = ''.join(name_parts)
        self._expect(TokenType.EQUALS, "期望 '='")

        if self._check_word('函数') or self._check_word('函'):
            value = self._parse_lambda()
            # 添加到全局用户动词集合
            if self.use_global_verbs:
                _global_user_verbs.add(name)
        else:
            value = self._parse_expression()

        return Define(name, value)

    def _parse_lambda(self) -> Lambda:
        self._advance()  # 消耗 '函数'

        params = []
        # 收集参数（非动词、非关键字的标识符）
        # 参数必须连续，遇到其他类型则停止
        while (self._current().type == TokenType.WORD and
                self._current().value not in self.VERBS and
                self._current().value not in {'如果', '那么', '否则', '真', '假', '空'} and
                self._current().value not in {'定义', '函数'}):
            # 如果下一个 token 是动词或条件关键字，当前可能是函数体的开始
            next_tok = self._peek(1)
            if next_tok.type == TokenType.DOT or next_tok.type == TokenType.COLON or next_tok.type == TokenType.INDENT:
                # 当前 token 是最后一个参数，但可能被拆分了
                current_word = self._advance().value
                # 检查下一个 token 是否是被拆分的标识符的一部分
                if next_tok.type == TokenType.WORD:
                    # 尝试组合
                    params.append(current_word + next_tok.value)
                    self._advance()
                else:
                    params.append(current_word)
                break
            if next_tok.type == TokenType.WORD and next_tok.value in {'如果', '那么', '否则'}:
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

        # 检查是否有块（冒号、句号后换行或缩进）
        if self._current().type == TokenType.COLON:
            self._advance()  # '：'
            body = self._parse_block()
        elif self._current().type == TokenType.INDENT:
            body = self._parse_block()
        else:
            body = self._parse_expression()
        return Lambda(params, body)

    def _parse_block(self) -> Node:
        """解析代码块（支持缩进语法）"""
        statements = []
        
        # 获取块开始时的缩进
        initial_indent = 0
        if self._current().type == TokenType.INDENT:
            initial_indent = int(self._current().value)
            self._advance()  # 消耗 INDENT token
        
        # 压入块栈
        self.block_stack.push('BLOCK', initial_indent)
        
        while not self._is_at_end():
            # 检测块结束标记（双句号，向后兼容）
            if self._current().type == TokenType.DOT:
                peek = self._peek(1)
                if peek and peek.type == TokenType.DOT:
                    self._advance()
                    self._advance()
                    break
                # 单个句号：跳过，继续解析下一个语句
                self._advance()
                continue
            
            # 检测 DEDENT（块结束的条件）
            # 关键：只有当 DEDENT 小于块的初始缩进时才结束块
            # DEDENT 等于初始缩进意味着嵌套块结束了，我们仍在当前块内
            if self._current().type == TokenType.DEDENT:
                current_dedent = int(self._current().value)
                # 如果 DEDENT 的级别严格小于块开始时的缩进，说明块结束
                if current_dedent < initial_indent:
                    # 不消耗 DEDENT，让上层处理
                    break
                # DEDENT 等于初始缩进 = 嵌套块结束，继续解析
                elif current_dedent == initial_indent:
                    self._advance()  # 消耗这个 DEDENT
                    continue
            
            # 块结束条件（其他情况）
            if self._is_block_end():
                break
            
            stmt = self._parse_statement(consume_dot=False)
            if stmt:
                statements.append(stmt)
            
            # 语句后处理 DOT
            if self._current().type == TokenType.DOT:
                peek = self._peek(1)
                if peek and peek.type == TokenType.DOT:
                    self._advance()
                    self._advance()
                    break
                self._advance()
        
        self.block_stack.pop()
        
        if len(statements) == 0:
            return Nil()
        elif len(statements) == 1:
            return Block([statements[0]])
        else:
            return Block(statements)
    
    def _get_current_indent(self) -> int:
        """获取当前缩进级别"""
        return self.block_stack.current_indent()
    
    def _get_peek_indent(self) -> int:
        """查看下一个缩进级别（通过查看 INDENT/DEDENT token）"""
        pos = self.pos
        while pos < len(self.tokens):
            tok = self.tokens[pos]
            if tok.type == TokenType.INDENT:
                return int(tok.value)
            elif tok.type == TokenType.DEDENT:
                return int(tok.value)
            elif tok.type not in {TokenType.DOT, TokenType.SEMI}:
                # 非结构符，说明当前行没有缩进变化
                return self._get_current_indent()
            pos += 1
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
        
        # 情况 2：遇到新的顶层定义
        if self._check_word('定义'):
            # 只有在顶层（块栈深度为0）时才认为是边界
            if self.block_stack.depth() == 0:
                return True
        
        # 情况 3：遇到同层级关键字
        if self._current().type == TokenType.WORD:
            word = self._current().value
            # 这些关键字表示新的块开始，应该结束当前块
            # 但在嵌套块内（块栈深度 > 1），这些是嵌套结构，不应作为边界
            if word in {'如果', '遍历', '当满足', '当时', '测', '套'}:
                if self.block_stack.depth() <= 1:
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
        
        # 新函数定义：定 NAME = 函 ...（只有函数定义才结束块，局部 定 不结束）
        if tok.type == TokenType.WORD and tok.value == '定义':
            if (self._peek(1).type == TokenType.WORD and 
                self._peek(2).type == TokenType.EQUALS and
                self._peek(3).type == TokenType.WORD and self._peek(3).value == '函数'):
                return True
        
        # 只有遇到新的函数定义才结束块
        # 注意：块内可以有 定 定义局部变量
        if tok.type == TokenType.WORD and tok.value in {'函数'}:
            return True
        
        # 测试块结束：遇到新的测试或测试套件
        if tok.type == TokenType.WORD and tok.value in {'测', '套'}:
            return True
        
        # 对于嵌套块（块栈深度 > 1），不应该在这里结束，应该由块内部的逻辑处理
        # 比如双句号或其他块结束标记
        # 这里返回 False，让解析继续
        return False

    def _parse_expression(self, stop_tokens: Optional[Set[TokenType]] = None) -> Node:
        return self._parse_pipeline(stop_tokens)

    def _parse_pipeline(self, stop_tokens: Optional[Set[TokenType]] = None) -> Node:
        step = self._parse_expr(stop_tokens)
        
        # 如果 _parse_expr 返回 None（遇到停止 token），返回 None
        if step is None:
            return None
            
        steps = [step]

        while self._match(TokenType.COMMA):
            steps.append(self._parse_expr(stop_tokens))

        if len(steps) == 1:
            return steps[0]
        return Pipeline(steps)

    def _parse_expr(self, stop_tokens: Optional[Set[TokenType]] = None) -> Node:
        """解析表达式：动词 数据* (副词 动词 数据*)*"""
        first = self._parse_term(stop_tokens)
        
        # 如果 _parse_term 返回 None（遇到停止 token），返回 None
        if first is None:
            return None

        # 处理副词链和高阶函数管道
        # 遇到右括号时停止（用于括号表达式）
        while self._current().type == TokenType.WORD and self._current().type != TokenType.RPAREN:
            # 检查是否遇到停止 token
            if stop_tokens and self._current().type in stop_tokens:
                break
            
            word = self._current().value
            
            # 如果遇到语句开始关键字，说明表达式结束了
            # 这些关键字不应该被当作表达式的一部分
            if word in {'定义', '如果', '那么', '否则', '遍历', '当满足', '当时', '函数', '返回', '输出', '引', '导'}:
                break
            
            # 处理副词（如 潜）
            if word in self.ADVERBS:
                adverb_name = self._advance().value
                adverb = Word(adverb_name)
                next_call = self._parse_term()
                first = Call(adverb, [first, next_call])
            # 处理高阶函数（归、皆、只）作为管道操作
            elif word in {'归约', '映射', '过滤'}:
                # 将前面的结果作为高阶函数的最后一个参数
                func_name = self._advance().value
                func = Word(func_name)
                args = []
                
                # 收集高阶函数的参数
                while not self._is_at_end():
                    tok = self._current()
                    if tok.type in {TokenType.DOT, TokenType.SEMI, TokenType.COMMA,
                                    TokenType.EQUALS, TokenType.COLON}:
                        break
                    if tok.type == TokenType.WORD and tok.value in {'如果', '那么', '否则', '定义', '函数', '归约', '映射', '过滤'}:
                        break
                    
                    arg = self._parse_term()
                    args.append(arg)
                
                # 将前面的结果作为最后一个参数（列表参数）
                args.append(first)
                first = Call(func, args)
            else:
                # 检查是否是动词，如果是且前面是动词调用，则可能是管道操作
                # 例如：印 结果 -> 结果作为印的参数
                # 但这里需要谨慎处理，避免破坏正常的动词调用
                break

        return first

    def _parse_term(self, stop_tokens: Optional[Set[TokenType]] = None) -> Node:
        """解析项"""
        # 检查是否遇到停止 token
        if stop_tokens and self._current().type in stop_tokens:
            return None
        
        # 导入语句
        if self._check_word('导入'):
            return self._parse_import()
        
        # 导出语句
        if self._check_word('导出'):
            return self._parse_export()
        
        # 结构体定义
        if self._check_word('结构'):
            return self._parse_struct_def()
        
        # 条件语句（仅在不在条件解析的上下文中时处理）
        if self._check_word('如果') or self._check_word('若'):
            # 检查是否在条件解析的上下文中
            # 通过检查 stop_tokens 来判断
            if stop_tokens and TokenType.INDENT in stop_tokens:
                # 在条件解析的上下文中，不处理嵌套的 '若'
                pass
            else:
                return self._parse_if()

        # Lambda 表达式（支持在表达式中使用）
        if self._check_word('函') or self._check_word('函数'):
            return self._parse_lambda_v2(stop_tokens)

        # 遍历循环
        if self._check_word('遍历'):
            return self._parse_foreach()

        # 当循环
        if self._check_word('当满足') or self._check_word('当时'):
            return self._parse_while()

        # 继续语句
        if self._check_word('继续'):
            self._advance()
            return Continue()

        # 副词开头
        if self._current().type == TokenType.WORD and self._current().value in self.ADVERBS:
            adverb_name = self._advance().value
            adverb = Word(adverb_name)
            next_call = self._parse_term(stop_tokens)
            return Call(adverb, [next_call])

        # 动词开头（必须是已知动词）
        if self._current().type == TokenType.WORD and self._is_verb(self._current().value):
            verb_name = self._advance().value
            verb = Word(verb_name)
            args = []

            while not self._is_at_end():
                tok = self._current()

                # 检查是否遇到停止 token
                if stop_tokens and tok.type in stop_tokens:
                    break

                # 遇到缩进变化，停止收集参数
                if tok.type in {TokenType.INDENT, TokenType.DEDENT}:
                    break

                if tok.type in {TokenType.DOT, TokenType.SEMI, TokenType.COMMA,
                                TokenType.EQUALS, TokenType.COLON, TokenType.RPAREN}:
                    break

                # 遇到条件关键字，停止（但允许若/如果作为参数的一部分）
                if tok.type == TokenType.WORD and tok.value in {'如果', '那么', '则', '否则', '定义'}:
                    break

                # 高阶函数（归/归约、皆/映射、只/过滤）：作为管道操作处理
                if tok.type == TokenType.WORD and tok.value in {'归', '皆', '只', '归约', '映射', '过滤'}:
                    # 将前面的结果作为高阶函数的输入，构建管道操作
                    # 例如：列1 2 3皆乘2 -> 皆(乘, 2, 列(1,2,3))
                    
                    # 解析高阶函数调用
                    func_name = self._advance().value
                    func = Word(func_name)
                    pipe_args = []
                    
                    # 对于 '归约' 和 '归'，需要收集两个参数（函数和初始值）
                    # 对于 '映射'/'皆' 和 '过滤'/'只'，只需要收集一个参数（函数）
                    full_func_name = func_name
                    if func_name == '归':
                        full_func_name = '归约'
                    elif func_name == '皆':
                        full_func_name = '映射'
                    elif func_name == '只':
                        full_func_name = '过滤'
                    
                    expected_args = 2 if full_func_name == '归约' else 1
                    
                    while not self._is_at_end() and len(pipe_args) < expected_args:
                        t2 = self._current()
                        if t2.type in {TokenType.DOT, TokenType.SEMI, TokenType.COMMA,
                                       TokenType.EQUALS, TokenType.COLON}:
                            break
                        if t2.type == TokenType.WORD and t2.value in {'如果', '那么', '否则', '定义', '函数', '函'}:
                            break
                        if t2.type == TokenType.WORD and t2.value in {'归', '皆', '只', '归约', '映射', '过滤'}:
                            break
                        
                        # 对于 '归约'/'归' 的第一个参数（函数），只取动词名，不解析参数
                        if full_func_name == '归约' and len(pipe_args) == 0:
                            # 第一个参数是函数名
                            pipe_arg = Word(t2.value)
                            self._advance()
                        else:
                            pipe_arg = self._parse_term()
                        pipe_args.append(pipe_arg)
                    
                    # 将前面收集的参数作为列表参数
                    # 创建一个列表调用作为输入
                    list_call = Call(verb, args)
                    
                    # 创建管道调用
                    # 参数处理：
                    # - 只(列表, 谓词)
                    # - 皆(函数, 参数..., 列表)
                    # - 归(函数, 初始值, 列表)
                    if func_name == '过滤':
                        # 只(列表, 谓词)
                        pipe_args.insert(0, list_call)
                    elif func_name == '归约':
                        # 归(函数, 初始值, 列表)
                        # pipe_args 已经包含 [函数, 初始值]
                        pipe_args.append(list_call)
                    else:
                        # 皆(函数, 参数..., 列表)
                        pipe_args.append(list_call)
                    
                    pipe_call = Call(func, pipe_args)
                    
                    # 返回管道调用作为结果
                    return pipe_call

                # 其他动词
                if tok.type == TokenType.WORD and self._is_verb(tok.value):
                    # 特殊处理：当 BINARY_INFIX 动词遇到单参数动词时
                    # 防止单参数动词吞噬后续的中缀动词（如 且 非 已用过 等 z 尾）
                    if (verb_name in self.BINARY_INFIX and 
                        tok.value in self.PREFIX_VERB_ARITY and 
                        self.PREFIX_VERB_ARITY[tok.value] == 1):
                        # 对于单参数动词，只解析一个原子参数，防止它吞噬中缀动词
                        inner_verb = self._advance().value
                        inner_args = []
                        if not self._is_at_end():
                            inner_args.append(self._parse_atom(stop_tokens))
                        arg = Call(Word(inner_verb), inner_args)
                        args.append(arg)
                        continue
                    # 条件关键字（若/如果）作为参数的一部分，需要解析整个条件表达式
                    if tok.value in {'若', '如果'}:
                        arg = self._parse_term(stop_tokens)
                        args.append(arg)
                        continue
                    # 普通动词遇到中缀动词：停止收集参数，让前面的参数与中缀动词形成中缀表达式
                    if tok.value in self.INFIX_VERBS:
                        # 如果已经有参数，让最后一个参数与中缀动词形成中缀表达式
                        if args:
                            last_arg = args.pop()
                            # 构建中缀表达式：last_arg 中缀动词 ...
                            infix_verb = self._advance().value
                            right = self._parse_term()
                            infix_expr = Call(Word(infix_verb), [last_arg, right])
                            args.append(infix_expr)
                            # 中缀表达式构建完成，停止收集参数
                            break
                        else:
                            # 没有参数，中缀动词作为普通动词处理
                            arg = self._parse_term(stop_tokens)
                            args.append(arg)
                            continue
                    # VARARGS 动词（列/列表/典/序）作为参数：解析为独立调用
                    if tok.value in self.VARARGS:
                        inner_verb = self._advance().value
                        inner_args = []
                        while not self._is_at_end():
                            t2 = self._current()
                            if t2.type in {TokenType.DOT, TokenType.SEMI, TokenType.COMMA,
                                           TokenType.EQUALS, TokenType.COLON}:
                                break
                            if t2.type == TokenType.WORD:
                                if t2.value in self.VARARGS or t2.value in self.INFIX_VERBS:
                                    break
                                if t2.value in {'如果', '那么', '否则', '定义', '函数'}:
                                    break
                                if t2.value in self.BINARY_INFIX:
                                    break
                                if self._is_verb(t2.value):
                                    inner_args.append(self._parse_term(stop_tokens))
                                    break
                            inner_args.append(self._parse_atom(stop_tokens))
                        arg = Call(Word(inner_verb), inner_args)
                        args.append(arg)
                        continue
                    # 可变参数动词（列/列表/典/序）：前缀动词可作为参数，中缀/结构动词停止
                    if verb_name in self.VARARGS:
                        if tok.value in self.INFIX_VERBS or tok.value in {'如果', '那么', '否则', '定义', '函数'}:
                            break
                        # VARARGS 动词嵌套：解析为独立调用，避免递归消耗后续 VARARGS
                        if tok.value in self.VARARGS:
                            inner_verb = self._advance().value
                            inner_args = []
                            while not self._is_at_end():
                                t2 = self._current()
                                if t2.type in {TokenType.DOT, TokenType.SEMI, TokenType.COMMA,
                                               TokenType.EQUALS, TokenType.COLON}:
                                    break
                                if t2.type == TokenType.WORD:
                                    if t2.value in self.VARARGS or t2.value in self.INFIX_VERBS:
                                        break
                                    if t2.value in {'如果', '那么', '否则', '定义', '函数'}:
                                        break
                                    # 单参数动词遇到中缀动词时停止，留给外层处理
                                    if t2.value in self.BINARY_INFIX:
                                        break
                                    if self._is_verb(t2.value):
                                        inner_args.append(self._parse_term(stop_tokens))
                                        break
                                inner_args.append(self._parse_atom(stop_tokens))
                            arg = Call(Word(inner_verb), inner_args)
                        else:
                            arg = self._parse_term(stop_tokens)
                        args.append(arg)
                        continue
                    # 高阶函数（归、皆、只）：动词作为参数传递（只取动词名，不解析参数）
                    if verb_name in {'归约', '映射', '过滤'}:
                        if tok.value == '函数' or tok.value == '函':
                            # 函开头的是匿名函数，解析 lambda
                            lambda_node = self._parse_lambda_v2(stop_tokens)
                            args.append(lambda_node)
                            # 块风格的 lambda 已消费块结束标记，参数收集结束
                            if isinstance(lambda_node.body, Block):
                                break
                        else:
                            args.append(Word(self._advance().value))
                        # 继续收集后续参数（如初始值）
                        continue
                    # 普通动词：吞噬
                    arg = self._parse_term(stop_tokens)
                    
                    # 如果 _parse_term 返回 None（遇到停止 token），停止收集参数
                    if arg is None:
                        break
                    
                    args.append(arg)
                    # 对于已知元数的前缀动词，达到元数后停止
                    if verb_name in self.PREFIX_VERB_ARITY:
                        if len(args) >= self.PREFIX_VERB_ARITY[verb_name]:
                            break
                    # 对于已知元数的用户定义函数，达到元数后停止
                    if verb_name in self.user_verb_arity and len(args) >= self.user_verb_arity[verb_name]:
                        break
                    continue

                # 原子 + 可能的中缀动词
                arg = self._parse_atom(stop_tokens)
                
                # 如果 _parse_atom 返回 None（遇到停止 token），返回 None
                if arg is None:
                    return None

                # 中缀动词延续：当参数是裸原子时允许中缀延续
                # 对于二元中缀运算符，中缀延续会在下面统一处理
                # 这里只需要把 arg 添加到 args 中
                args.append(arg)

                # 对于已知元数的前缀动词，达到元数后停止收集
                if verb_name in self.PREFIX_VERB_ARITY and len(args) >= self.PREFIX_VERB_ARITY[verb_name]:
                    break

                # 对于已知元数的用户定义函数，达到元数后停止收集
                if verb_name in self.user_verb_arity and len(args) >= self.user_verb_arity[verb_name]:
                    break

                # 对于二元中缀动词，达到2个参数后停止
                if verb_name in self.BINARY_INFIX and len(args) >= 2:
                    break

            # 构建动词调用
            result = Call(verb, args)

            # 中缀动词延续：动词调用后可能跟着中缀动词
            # 对于二元中缀运算符（如 且、等），中缀延续会收集两个参数
            while (self._current().type == TokenType.WORD and
                   self._current().value in self.INFIX_VERBS):
                infix_verb = self._advance().value
                right = self._parse_term()
                result = Call(Word(infix_verb), [result, right])
                # 对于二元中缀运算符，中缀延续后不要再继续
                if infix_verb in self.BINARY_INFIX:
                    break

            return result

        # 普通原子
        node = self._parse_atom(stop_tokens)
        
        # 如果 _parse_atom 返回 None（遇到 INDENT/DEDENT），返回 None 让上层处理
        if node is None:
            return None

        # 用户定义的函数名（可能被包含在 token 中）
        # 例如："汉诺塔盘子数减" 包含用户定义的 "汉诺塔"
        # 当原子是 Word 且不在已知动词中时，尝试匹配用户定义函数名
        if isinstance(node, Word) and self.use_global_verbs and not self._is_verb(node.name):
            matched_name = self._try_match_user_verb()
            if matched_name:
                func = Word(matched_name)
                args = self._collect_call_args()
                return Call(func, args)

        # 中缀动词延续：原子后可能跟着中缀动词
        while (self._current().type == TokenType.WORD and
               self._current().value in self.INFIX_VERBS):
            infix_verb = self._advance().value
            right = self._parse_term()
            node = Call(Word(infix_verb), [node, right])

        return node
    def _parse_atom(self, stop_tokens: Optional[Set[TokenType]] = None) -> Node:
        """解析原子"""
        # 检查是否遇到停止 token
        if stop_tokens and self._current().type in stop_tokens:
            return None
        
        # 缩进 tokens 不是原子，返回 None 让上层处理
        if self._current().type in {TokenType.INDENT, TokenType.DEDENT}:
            return None
        
        # 引用：'expr
        if self._current().type == TokenType.QUOTE:
            self._advance()  # 跳过 '
            expr = self._parse_expression(stop_tokens)
            return Quote(expr)

        # 括号表达式：(expr)
        if self._current().type == TokenType.LPAREN:
            self._advance()  # 跳过 '('
            expr = self._parse_expression({TokenType.RPAREN})
            if self._current().type != TokenType.RPAREN:
                raise ParserError("期望 ')'", self._current().line, self._current().col)
            self._advance()  # 跳过 ')'
            return expr

        if self._check_word('如果') or self._check_word('若'):
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
        if self._check_word('无'):
            self._advance()
            return Nil()

        # 条件关键字不是原子
        if self._current().type == TokenType.WORD and self._current().value in {'那么', '否则'}:
            raise ParserError(f"意外的关键字: {self._current().value}",
                             self._current().line, self._current().col)

        # 普通标识符（变量名或函数名）
        if self._current().type == TokenType.WORD:
            # 先检查是否是用户定义的函数
            if self.use_global_verbs:
                matched_name = self._try_match_user_verb()
                if matched_name:
                    func = Word(matched_name)
                    args = self._collect_call_args()
                    return Call(func, args)
            
            # 普通变量引用
            node = Word(self._advance().value)
            
            # 检查是否是成员访问：标识符.标识符（仅英文句号）
            # 注意：成员名不能是关键字，避免干扰控制流
            while (not self._is_at_end() and 
                   self._current().type == TokenType.DOT_EN and
                   self._peek(1).type == TokenType.WORD):
                # 检查下一个词是否是关键字，如果是则不进行成员访问
                next_word = self._peek(1).value
                if next_word in {'如果', '那么', '否则', '定义', '函数', '返回', '遍历', '当满足', '当时', '真', '假', '空', '无', '输出', '读', '写', '行', '映射', '过滤', '归约', '潜', '相加', '相减', '相乘', '相除', '取余', '幂', '大于', '小于', '等于', '不等', '并且', '或者', '非也', '首个', '其余', '入', '长', '添', '连', '含', '空', '范围', '引', '出'}:
                    break
                self._advance()  # 消耗 '.'
                member_name = self._advance().value
                # 创建成员访问表达式
                node = Call(Word('.'), [node, Word(member_name)])
            
            return node

        raise ParserError(f"意外的 token: {self._current()}",
                         self._current().line, self._current().col)


    def _parse_if(self) -> If:
        """解析条件语句：若 条件 [则]：分支。否则：分支。
        
        支持两种语法：
        1. 若 条件 则：分支。否则：分支。（传统语法）
        2. 若 条件：分支。否则：分支。（省略则，更简洁）
        3. 若 条件 换行缩进 分支（新缩进语法）
        """
        line = self._current().line
        col = self._current().col
        
        # 检查当前 token 是否以 '如果' 开头（如 "如果真那么1"）
        if (self._current().type == TokenType.WORD and 
            self._current().value.startswith('如果') and 
            len(self._current().value) > 2):
            # 将 "如果xxx" 拆分为 "如果" 和 "xxx"
            full = self._current().value
            rest = full[2:]  # 去掉 '如果' 前缀（两个字符）
            self._advance()  # 消耗 "如果xxx"
            # 将剩余部分作为条件表达式的开始
            # 需要将 rest 作为一个新的 token 放回队列
            self.pos -= 1  # 后退一步
            self.tokens[self.pos] = Token(TokenType.WORD, rest, line, col + 2)
        else:
            # 消耗 '如果' 或 '若'
            self._advance()

        # 解析条件：使用 _parse_expr_until 可以处理函数调用和中缀表达式
        # 停止词包括 '则'、'：'（块开始标记）和 INDENT（缩进开始）
        cond = self._parse_expr_until({'则', '：', 'INDENT'})

        # 可选的 '则' 关键字
        if self._check_word('则'):
            self._advance()  # 消耗 '则'

        # 可选的 '那么' 或 '则' 关键字
        if self._check_word('那么') or self._check_word('则'):
            self._advance()  # 消耗 '那么' 或 '则'

        # 检查是否有 '：'（块开始标记）或 INDENT（缩进开始）
        has_block = self._current().type == TokenType.COLON or self._current().type == TokenType.INDENT
        if self._current().type == TokenType.COLON:
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
        # 处理 then 分支后的结束标记
        # 如果遇到 DEDENT，跳过它（块结束了）
        if self._current().type == TokenType.DEDENT:
            self._advance()  # 跳过 DEDENT
        
        # 跳过可能的句号（仅在后面跟着 否则 时才消耗，否则留给外层块处理）
        if self._current().type == TokenType.DOT:
            peek = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if peek and peek.type == TokenType.WORD and peek.value == '否则':
                self._advance()
        if self._check_word('否则'):
            self._advance()
            # 检查是否有 '：' 或 INDENT
            has_else_block = self._current().type == TokenType.COLON or self._current().type == TokenType.INDENT
            if self._current().type == TokenType.COLON:
                self._advance()  # 消耗 '：'
            if has_else_block:
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
        
        # 获取当前的缩进级别（如果当前是 INDENT token）
        block_start_indent = 0
        if self._current().type == TokenType.INDENT:
            block_start_indent = int(self._current().value)
            self._advance()  # 消耗 INDENT token
        
        # 压入块栈
        self.block_stack.push('BLOCK_UNTIL', block_start_indent)
        initial_depth = self.block_stack.depth()
        
        while not self._is_at_end():
            # 如果遇到 DEDENT，检查是否应该结束当前块
            if self._current().type == TokenType.DEDENT:
                current_dedent = int(self._current().value)
                # 如果 DEDENT 的级别严格小于块开始时的缩进，说明块结束
                if current_dedent < block_start_indent:
                    break
                # 如果 DEDENT 的级别等于块开始时的缩进，说明嵌套块结束了，继续解析
                elif current_dedent == block_start_indent:
                    self._advance()  # 消耗这个 DEDENT
                    continue
            
            if self._current().type == TokenType.DOT:
                peek = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if peek and peek.type == TokenType.DOT:
                    # 双句号：块结束，消耗这两个句号
                    self._advance()
                    self._advance()
                    break
                # 单个句号：检查是否应该结束当前块
                # 如果 stop_words 为空，单个句号结束当前块
                if not stop_words:
                    self._advance()
                    # 检查下一个 token 是否是 DEDENT
                    if self._current().type == TokenType.DEDENT:
                        current_dedent = int(self._current().value)
                        if current_dedent < block_start_indent:
                            break
                        elif current_dedent == block_start_indent:
                            self._advance()
                            continue
                    break
                # 否则跳过句号，继续解析下一个语句
                self._advance()
                continue
            if self._current().type == TokenType.WORD and self._current().value in stop_words:
                break
            # 检查是否到达块结束（用于嵌套块的正确处理）
            if self._is_block_end():
                break
            stmt = self._parse_statement(consume_dot=False)
            if stmt:
                statements.append(stmt)
        
        # 弹出块栈
        self.block_stack.pop()
        
        if len(statements) == 0:
            return Nil()
        elif len(statements) == 1 and not always_block:
            return statements[0]
        else:
            return Block(statements)
    def _parse_foreach(self) -> ForEach:
        """解析遍历循环：遍历 变量 于 列表：循环体。
        
        支持两种语法：
        1. 遍历 变量 于 列表：循环体。（传统语法）
        2. 遍历 变量 于 列表 换行缩进 循环体（新缩进语法）
        """
        self._advance()  # 消耗 '遍历'
        
        # 解析变量名
        if self._current().type != TokenType.WORD:
            raise ParserError("期望变量名", self._current().line, self._current().col)
        var = self._advance().value
        
        # 期望 '于'
        if not self._check_word('于'):
            raise ParserError("期望 '于'", self._current().line, self._current().col)
        self._advance()  # 消耗 '于'
        
        # 解析可迭代对象（支持可能被拆分的标识符，如"列表"可能被拆成"列"+"表"）
        iterable = self._parse_iterable()
        
        # 检查是否有 '：'（块开始）或 INDENT（缩进开始）
        has_block = self._current().type == TokenType.COLON or self._current().type == TokenType.INDENT
        if self._current().type == TokenType.COLON:
            self._advance()  # 消耗 '：'
        
        # 解析循环体
        body = self._parse_block()
        
        return ForEach(var, iterable, body)
    
    def _parse_iterable(self) -> Node:
        """解析可迭代对象，处理可能被拆分的标识符"""
        # 如果当前 token 是动词，解析为函数调用
        if self._current().type == TokenType.WORD and self._is_verb(self._current().value):
            return self._parse_term()
        
        # 收集连续的 WORD tokens 作为可能的标识符
        word_parts = []
        while self._current().type == TokenType.WORD:
            # 检查是否是块结束标记
            next_tok = self._peek(1)
            if next_tok.type in {TokenType.COLON, TokenType.INDENT, TokenType.DEDENT, TokenType.DOT, TokenType.EOF}:
                break
            if next_tok.type == TokenType.WORD and next_tok.value in {'如果', '那么', '否则', '定义', '函数'}:
                break
            word_parts.append(self._advance().value)
        
        if not word_parts:
            # 如果没有收集到任何词，尝试解析普通表达式
            return self._parse_term()
        
        # 将收集的词组合成一个标识符
        if len(word_parts) == 1:
            return Word(word_parts[0])
        else:
            # 组合成一个标识符节点
            return Word(''.join(word_parts))

    def _parse_while(self) -> While:
        """解析当循环：当 条件 则：循环体 或 当 条件：循环体。
        
        支持的语法：
        1. 当 条件：循环体。（传统语法）
        2. 当 条件 则：循环体。（传统语法）
        3. 当 变量 中缀动词 值：循环体。（如 当 小 j 边界：）
        4. 当 条件 换行缩进 循环体（新缩进语法）
        """
        self._advance()  # 消耗 '当满足'

        # 解析条件表达式（支持中缀表达式）
        cond = self._parse_expr_until({'那么', '：', 'INDENT'})

        # 可选的 '那么' 关键字
        if self._check_word('那么'):
            self._advance()  # 消耗 '那么'

        # 检查是否有 '：'（块开始）或 INDENT（缩进开始）
        has_block = self._current().type == TokenType.COLON or self._current().type == TokenType.INDENT
        if self._current().type == TokenType.COLON:
            self._advance()  # 消耗 '：'

        # 解析循环体
        body = self._parse_block()

        return While(cond, body)

    def _parse_expr_until(self, stop_words: Set[str]) -> Node:
        """解析表达式，直到遇到指定的停止词
        
        stop_words 可以包含字符串（WORD 值）和特殊标记如 '：'（冒号）和 'INDENT'（缩进）
        """
        # 收集所有 term 直到遇到停止词
        terms = []
        while not self._is_at_end():
            if self._current().type == TokenType.DOT:
                break
            # 检查 INDENT 类型的停止词
            if self._current().type == TokenType.INDENT and 'INDENT' in stop_words:
                break
            # 检查 WORD 类型的停止词
            if self._current().type == TokenType.WORD and self._current().value in stop_words:
                break
            # 检查 COLON 类型的停止词（支持 '：' 作为停止标记）
            if self._current().type == TokenType.COLON and '：' in stop_words:
                break
            if self._current().type == TokenType.WORD and self._current().value in {'如果', '若', '那么', '否则'}:
                # 如果是嵌套的条件语句
                # 但如果 '若' 不在 stop_words 中，说明这是外层条件的一部分，不要处理
                if self._current().value in {'如果', '若'} and '若' not in stop_words:
                    terms.append(self._parse_if())
                else:
                    break
            else:
                # 检查是否遇到 '则'，如果是则停止收集（条件部分结束）
                if self._current().type == TokenType.WORD and self._current().value == '则':
                    break
                # 传递 stop_words，防止 _parse_term 处理嵌套的 '若'
                terms.append(self._parse_term({TokenType.INDENT}))

        if len(terms) == 0:
            return Nil()
        elif len(terms) == 1:
            return terms[0]
        else:
            # 多个 term 组成管道
            return Pipeline(terms)

    def _parse_test(self) -> Test:
        """解析测试：测 "测试名"：测试体。"""
        self._advance()  # 消耗 '测'
        
        # 解析测试名称（字符串字面量）
        if self._current().type != TokenType.STR:
            raise self._error("期望测试名称（字符串）")
        name = self._advance().value
        
        # 期望 '：'（块开始）
        if self._current().type != TokenType.COLON:
            raise self._error("期望 '：' 开始测试体")
        self._advance()  # 消耗 '：'
        
        # 解析测试体
        body = self._parse_block()
        
        return Test(name, body)

    def _parse_test_suite(self) -> TestSuite:
        """解析测试套件：套 "套件名"：测试列表。"""
        self._advance()  # 消耗 '套'

        # 解析套件名称（字符串字面量）
        if self._current().type != TokenType.STR:
            raise self._error("期望套件名称（字符串）")
        name = self._advance().value

        # 期望 '：'（块开始）
        if self._current().type != TokenType.COLON:
            raise self._error("期望 '：' 开始测试套件")
        self._advance()  # 消耗 '：'

        # 解析测试列表
        tests = []
        setup = None
        teardown = None

        while not self._is_at_end():
            # 跳过句号
            if self._current().type == TokenType.DOT:
                self._advance()
                continue

            # 文件结束
            if self._current().type == TokenType.EOF:
                break

            # 前置钩子
            if self._check_word('前'):
                self._advance()
                if self._current().type != TokenType.COLON:
                    raise self._error("期望 '：' 开始前置钩子")
                self._advance()
                setup = self._parse_block()
                continue

            # 后置钩子
            if self._check_word('后'):
                self._advance()
                if self._current().type != TokenType.COLON:
                    raise self._error("期望 '：' 开始后置钩子")
                self._advance()
                teardown = self._parse_block()
                continue

            # 测试定义
            if self._check_word('测'):
                test = self._parse_test()
                tests.append(test)
                continue

            # 遇到新的测试套件，结束当前套件
            if self._check_word('套'):
                break

            # 其他语句，跳过
            self._advance()

        return TestSuite(name, tests, setup, teardown)

    def _parse_import(self) -> Import:
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
    
    def _parse_export(self) -> Export:
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
    
    def _parse_struct_def(self) -> StructDef:
        """解析结构体定义：结构 名称 字段1 类型1 字段2 类型2 ..."""
        self._advance()  # 消耗 '结构'
        
        # 结构体名称
        if self._current().type != TokenType.WORD:
            raise ParserError("期望结构体名称", self._current().line, self._current().col)
        name = self._advance().value
        
        fields = []
        
        # 解析字段
        while not self._is_at_end() and not self._check_word('。') and not self._check_word('；'):
            # 字段名
            if self._current().type != TokenType.WORD:
                break
            field_name = self._advance().value
            
            # 字段类型（可选）
            field_type = None
            if self._current().type == TokenType.WORD and not self._check_word('。') and not self._check_word('；'):
                field_type = self._advance().value
            
            fields.append((field_name, field_type))
        
        # 消耗句号或分号
        if self._check_word('。') or self._check_word('；'):
            self._advance()
        
        return StructDef(name=name, fields=fields)


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
