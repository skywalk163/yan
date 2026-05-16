
# 言语言自举编译器
# 整合所有模块

# ============ 工具函数 ============
def is_chinese_char(char):
    return '\u4e00' <= char <= '\u9fff'

def is_digit(char):
    return char.isdigit()

def is_letter(char):
    return char.isalpha()

def substring(s, start, end=None):
    if end is None:
        return s[start:]
    return s[start:end]

def char_at(s, index):
    if index < len(s):
        return s[index]
    return ''

# ============ Token定义 ============
KEYWORDS = {'定', '函', '若', '则', '否则', '当', '真', '假', '空', '无'}
VERBS = {'加', '减', '乘', '除', '等于', '大于', '小于', '列', '印', '取', '入', '长', '连'}

def create_token(type_name, value, line, column):
    return (type_name, value, line, column)

def get_token_type(token):
    return token[0]

def get_token_value(token):
    return token[1]

# ============ 词法分析器 ============
def tokenize(source):
    tokens = []
    i = 0
    length = len(source)
    line = 1
    col = 1
    
    while i < length:
        ch = source[i]
        
        if ch == ' ':
            i += 1
            col += 1
        elif ch == '\t':
            i += 1
            col += 4
        elif ch == '\n':
            line += 1
            col = 1
            i += 1
        elif ch == '\r':
            i += 1
            
        # Python代码块
        elif ch == '{' and i + 1 < length and source[i+1] == '{':
            start_line, start_col = line, col
            i += 2
            col += 2
            j = i
            while j < length:
                if j + 1 < length and source[j] == '}' and source[j+1] == '}':
                    break
                if source[j] == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
                j += 1
            value = source[i:j]
            tokens.append(('PYTHON', value, start_line, start_col))
            i = j + 2
            
        elif ch in '，。：=；\'':
            special_map = {'，':'COMMA', '。':'DOT', '：':'COLON', '=':'EQUALS', '；':'SEMI', "'":'QUOTE'}
            tokens.append((special_map[ch], ch, line, col))
            i += 1
            col += 1
            
        elif ch == '"':
            j = i + 1
            while j < length and source[j] != '"':
                if source[j] == '\\' and j + 1 < length:
                    j += 2
                else:
                    j += 1
            value = source[i+1:j]
            tokens.append(('STR', value, line, col))
            i = j + 1
            
        elif ch.isdigit():
            j = i + 1
            while j < length and source[j].isdigit():
                j += 1
            value = source[i:j]
            tokens.append(('NUM', value, line, col))
            col += (j - i)
            i = j
            
        elif ch.isalpha():
            j = i + 1
            while j < length and (source[j].isalnum() or source[j] == '_'):
                j += 1
            value = source[i:j]
            if value in KEYWORDS:
                tokens.append(('KEYWORD', value, line, col))
            elif value in VERBS:
                tokens.append(('VERB', value, line, col))
            else:
                tokens.append(('WORD', value, line, col))
            col += (j - i)
            i = j
            
        elif '\u4e00' <= ch <= '\u9fff':
            j = i + 1
            while j < length and '\u4e00' <= source[j] <= '\u9fff':
                j += 1
            value = source[i:j]
            if value in KEYWORDS:
                tokens.append(('KEYWORD', value, line, col))
            elif value in VERBS:
                tokens.append(('VERB', value, line, col))
            else:
                tokens.append(('WORD', value, line, col))
            col += (j - i)
            i = j
            
        elif ch == '-' and i + 1 < length and source[i+1] == '-':
            while i < length and source[i] != '\n':
                i += 1
        else:
            tokens.append(('WORD', ch, line, col))
            i += 1
            col += 1
  
    tokens.append(('EOF', None, line, col))
    return tokens

# ============ 语法分析器 ============
def parse(tokens):
    pos = 0
    length = len(tokens)
    errors = []
    
    def current():
        if pos < length:
            return tokens[pos]
        return ('EOF', None, 0, 0)
    
    def advance():
        nonlocal pos
        tok = current()
        pos += 1
        return tok
    
    def peek():
        if pos + 1 < length:
            return tokens[pos + 1]
        return ('EOF', None, 0, 0)
    
    def parse_program():
        statements = []
        while current()[0] != 'EOF':
            stmt = parse_statement()
            if stmt:
                statements.append(stmt)
        return ('Program', statements)
    
    def parse_statement():
        tok = current()
        
        if tok[0] == 'DOT':
            advance()
            return None
        if tok[0] == 'SEMI':
            advance()
            return None
        
        if tok[0] == 'PYTHON':
            return parse_python_code()
        
        if tok[0] == 'KEYWORD' and tok[1] == '定':
            return parse_define()
        
        if tok[0] == 'KEYWORD' and tok[1] == '若':
            return parse_if()
        
        if tok[0] == 'KEYWORD' and tok[1] == '当':
            return parse_while()
        
        return parse_expression()
    
    def parse_python_code():
        tok = advance()
        return ('PythonCode', tok[1])
    
    def parse_define():
        advance()
        name_tok = advance()
        name = name_tok[1]
        
        if current()[0] == 'EQUALS':
            advance()
        
        value = parse_expression()
        return ('Define', name, value)
    
    def parse_if():
        advance()
        cond = parse_expression()
        
        if current()[0] == 'KEYWORD' and current()[1] == '则':
            advance()
        
        then_branch = parse_expression()
        else_branch = None
        
        if current()[0] == 'KEYWORD' and current()[1] == '否则':
            advance()
            else_branch = parse_expression()
        
        return ('If', cond, then_branch, else_branch)
    
    def parse_while():
        advance()
        cond = parse_expression()
        
        if current()[0] == 'KEYWORD' and current()[1] == '则':
            advance()
        elif current()[0] == 'COLON':
            advance()
        
        body = parse_expression()
        return ('While', cond, body)
    
    def parse_expression():
        return parse_pipeline()
    
    def parse_pipeline():
        steps = [parse_expr()]
        while current()[0] == 'COMMA':
            advance()
            steps.append(parse_expr())
        if len(steps) == 1:
            return steps[0]
        return ('Pipeline', steps)
    
    def parse_expr():
        terms = [parse_term()]
        return terms[0] if len(terms) == 1 else ('Binary', terms)
    
    def parse_term():
        tok = current()
        
        if tok[0] == 'WORD' or tok[0] == 'VERB':
            advance()
            verb = tok[1]
            
            if verb in KEYWORDS:
                pos -= 1
                return ('Word', verb)
            
            if peek()[0] == 'KEYWORD' and peek()[1] == '函':
                return parse_lambda(verb)
            
            args = []
            while current()[0] not in ('DOT', 'SEMI', 'COLON', 'COMMA', 'EOF'):
                next_tok = current()
                if next_tok[0] == 'KEYWORD' and next_tok[1] in ['若', '当', '定', '否则', '则']:
                    break
                args.append(parse_expression())
            
            return ('Call', verb, args)
        
        if tok[0] == 'NUM':
            advance()
            return ('Num', tok[1])
        
        if tok[0] == 'STR':
            advance()
            return ('Str', tok[1])
        
        if tok[0] == 'KEYWORD':
            advance()
            if tok[1] == '真':
                return ('Bool', True)
            elif tok[1] == '假':
                return ('Bool', False)
            elif tok[1] == '空' or tok[1] == '无':
                return ('Nil',)
        
        return ('Word', None)
    
    def parse_lambda(name):
        advance()
        params = []
        
        while current()[0] == 'WORD':
            params.append(advance()[1])
            if current()[0] != 'COMMA':
                break
            advance()
        
        if current()[0] == 'COLON':
            advance()
        
        body = parse_expression()
        return ('Lambda', name, params, body)
    
    ast = parse_program()
    return (ast, errors)

# ============ 代码生成器 ============
OPERATOR_MAP = {
    '加': '+', '减': '-', '乘': '*', '除': '/',
    '等于': '==', '不等': '!=', '大于': '>', '小于': '<',
    '大等于': '>=', '小等于': '<=',
}

def generate(ast):
    def gen(node):
        if node is None:
            return ''
        
        node_type = node[0]
        
        if node_type == 'Program':
            result = []
            for stmt in node[1]:
                code = gen(stmt)
                if code:
                    result.append(code)
            return '\n'.join(result)
        
        if node_type == 'Define':
            name = node[1]
            value = gen(node[2])
            return f"{name} = {value}"
        
        if node_type == 'Lambda':
            name = node[1]
            params = node[2]
            body = gen(node[3])
            params_str = ', '.join(params) if params else ''
            return f"def {name}({params_str}):\n    {body}"
        
        if node_type == 'Call':
            verb = node[1]
            args = node[2]
            
            if verb in OPERATOR_MAP:
                if len(args) == 2:
                    op = OPERATOR_MAP[verb]
                    return f"({gen(args[0])} {op} {gen(args[1])})"
            
            if verb == '印':
                args_str = ', '.join([gen(arg) for arg in args])
                return f"print({args_str})"
            elif verb == '长':
                return f"len({gen(args[0])})"
            elif verb == '添':
                if len(args) >= 2:
                    return f"{gen(args[0])}.append({gen(args[1])})"
            elif verb == '连':
                parts = [gen(arg) for arg in args]
                return ' + '.join(parts)
            elif verb == '列':
                args_str = ', '.join([gen(arg) for arg in args])
                return f"[{args_str}]"
            elif verb == '入' or verb == '取':
                if len(args) >= 2:
                    return f"{gen(args[0])}[{gen(args[1])}]"
            
            args_str = ', '.join([gen(arg) for arg in args])
            return f"{verb}({args_str})"
        
        if node_type == 'Num':
            return node[1]
        
        if node_type == 'Str':
            return f"'{node[1]}'"
        
        if node_type == 'Word':
            return node[1] if node[1] else ''
        
        if node_type == 'Bool':
            return 'True' if node[1] else 'False'
        
        if node_type == 'Nil':
            return 'None'
        
        if node_type == 'If':
            cond = gen(node[1])
            then_branch = gen(node[2])
            else_branch = gen(node[3]) if node[3] else 'None'
            return f"({then_branch} if {cond} else {else_branch})"
        
        if node_type == 'While':
            cond = gen(node[1])
            body = gen(node[2])
            return f"while {cond}:\n    {body}"
        
        if node_type == 'Pipeline':
            steps = [gen(step) for step in node[1]]
            return '\n'.join(steps)
        
        if node_type == 'PythonCode':
            return node[1]
        
        return ''
    
    return gen(ast)

# ============ 编译函数 ============
def compile(source):
    tokens = tokenize(source)
    parse_result = parse(tokens)
    ast = parse_result[0]
    errors = parse_result[1]
    code = generate(ast)
    return (code, errors)

# 测试
test_source = '定x=加1 2。定y=乘x 3。印y。'
result = compile(test_source)
print("编译结果:")
print(result[0])
