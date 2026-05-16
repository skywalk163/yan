"""
Python 到言语言代码转换器

将 Python 源代码转换为言语言（Yan）代码，保持语义等价。
支持标准库映射和第三方库 Python 桥接。

用法：
    python py2yan.py input.py -o output.yan
    python py2yan.py input.py -o output.yan -v  (验证模式)
"""

import ast
import sys
import os
import re
from typing import List, Optional, Set, Dict, Tuple


# ============ 标准库到言语言映射表 ============

# Python 模块 -> 言语言库名
STDLIB_MODULE_MAP = {
    'os': '文件',
    'json': 'JSON',
    'datetime': '时间',
    'time': '时间',
    're': '正则',
    'math': '数学',
    'random': '随机',
    'sys': '系统',
    'pathlib': '路径',
    'csv': 'CSV',
    'hashlib': '哈希',
    'base64': '编码',
    'uuid': 'UUID',
    'itertools': '迭代',
    'functools': '函数',
    'collections': '集合',
}

# Python 模块.函数 -> 言语言动词
STDLIB_FUNC_MAP = {
    # os 模块
    ('os', 'path.join'): '路径连接',
    ('os', 'path.exists'): '存在',
    ('os', 'listdir'): '列目录',
    ('os', 'makedirs'): '建目录',
    ('os', 'remove'): '删文件',
    ('os', 'rmdir'): '删目录',
    ('os', 'getcwd'): '当前目录',
    ('os', 'path.basename'): '文件名',
    ('os', 'path.dirname'): '目录名',
    ('os', 'path.splitext'): '扩展名',
    ('os', 'path.isfile'): '是文件',
    ('os', 'path.isdir'): '是目录',

    # json 模块
    ('json', 'loads'): 'JSON解码',
    ('json', 'dumps'): 'JSON编码',
    ('json', 'load'): 'JSON解码',
    ('json', 'dump'): 'JSON编码',

    # datetime 模块
    ('datetime', 'datetime.now'): '当前时间',
    ('datetime', 'datetime.strftime'): '格式化时间',
    ('datetime', 'datetime.strptime'): '解析时间',

    # time 模块
    ('time', 'time'): '当前时间',
    ('time', 'sleep'): '睡眠',
    ('time', 'strftime'): '格式化时间',
    ('time', 'localtime'): '本地时间',

    # re 模块
    ('re', 'match'): '正则匹配',
    ('re', 'search'): '正则查找',
    ('re', 'sub'): '正则替换',
    ('re', 'split'): '正则分割',
    ('re', 'findall'): '正则查找全部',
    ('re', 'compile'): '正则编译',

    # math 模块
    ('math', 'sin'): '正弦',
    ('math', 'cos'): '余弦',
    ('math', 'tan'): '正切',
    ('math', 'asin'): '反正弦',
    ('math', 'acos'): '反余弦',
    ('math', 'atan'): '反正切',
    ('math', 'exp'): '指数',
    ('math', 'log'): '对数',
    ('math', 'log10'): '对数10',
    ('math', 'sqrt'): '开方',
    ('math', 'floor'): '取整',
    ('math', 'ceil'): '进位',
    ('math', 'round'): '四舍五入',
    ('math', 'pi'): '圆周率',
    ('math', 'e'): '自然常数',

    # random 模块
    ('random', 'random'): '随机',
    ('random', 'randint'): '随机整数',
    ('random', 'choice'): '随机选择',
    ('random', 'shuffle'): '随机打乱',
    ('random', 'sample'): '随机抽样',
    ('random', 'uniform'): '随机小数',
}

# Python 内置函数 -> 言语言动词
BUILTIN_FUNC_MAP = {
    'abs': '绝对',
    'len': '长',
    'print': '印',
    'int': '转整数',
    'str': '转字符串',
    'float': '转浮点',
    'list': '转列表',
    'bool': '转布尔',
    'type': '类型',
    'max': '最大',
    'min': '最小',
    'sum': '总和',
    'round': '四舍五入',
    'range': '范围',
    'map': '皆',
    'filter': '只',
    'sorted': '排序',
    'reversed': '反转',
    'enumerate': '枚举',
    'zip': '拉链',
    'open': '打开文件',
    'input': '输入',
    'isinstance': '是实例',
}

# Python 运算符 -> 言语言动词
BINOP_MAP = {
    ast.Add: '加',
    ast.Sub: '减',
    ast.Mult: '乘',
    ast.Div: '除',
    ast.Mod: '模',
    ast.Pow: '幂',
    ast.FloorDiv: '整除',
    ast.LShift: '左移',
    ast.RShift: '右移',
    ast.BitOr: '位或',
    ast.BitXor: '位异或',
    ast.BitAnd: '位与',
}

CMPOP_MAP = {
    ast.Gt: '大',
    ast.Lt: '小',
    ast.GtE: '大等于',
    ast.LtE: '小等于',
    ast.Eq: '等',
    ast.NotEq: '不等',
    ast.In: '含',
    ast.NotIn: '不含',
    ast.Is: '是',
    ast.IsNot: '不是',
}

BOOLOP_MAP = {
    ast.And: '且',
    ast.Or: '或',
}

UNARYOP_MAP = {
    ast.UAdd: '',
    ast.USub: '负',
    ast.Not: '非',
    ast.Invert: '位反',
}

# Python 模块.常量 -> 言语言变量
STDLIB_CONST_MAP = {
    ('math', 'pi'): '圆周率',
    ('math', 'e'): '自然常数',
    ('math', 'inf'): '无穷',
    ('math', 'nan'): '非数',
}

# 需要桥接的第三方库（无言语言等价实现）
THIRD_PARTY_LIBS = {
    'numpy', 'pandas', 'scipy', 'matplotlib', 'sklearn',
    'tensorflow', 'torch', 'flask', 'django', 'requests',
    'beautifulsoup4', 'selenium', 'pillow', 'opencv',
    'nltk', 'transformers', 'sqlalchemy', 'pytest',
}


class ConversionError(Exception):
    """转换错误"""
    pass


class PythonToYanConverter:
    """Python 到言语言代码转换器"""

    def __init__(self):
        self.indent_level = 0
        self.indent_str = '  '
        self.imports: List[str] = []  # 已处理的导入
        self.bridged_modules: Set[str] = set()  # 需要桥接的模块
        self.used_stdlib_modules: Set[str] = set()  # 已使用的标准库
        self.local_vars: Set[str] = set()  # 局部变量
        self.function_names: Set[str] = set()  # 函数名
        self.loop_var_stack: List[str] = []  # 循环变量栈
        self.in_function_body: bool = False  # 是否在函数体中
        self.in_block: bool = False  # 是否在块结构中
        self.imported_names: Dict[str, str] = {}  # 本地名 -> 模块名映射
        self.conversion_report = ConversionReport()

    def convert(self, python_source: str) -> str:
        """转换 Python 源码为言语言代码"""
        try:
            tree = ast.parse(python_source)
        except SyntaxError as e:
            raise ConversionError(f"Python 语法错误: {e}")

        self._collect_function_names(tree)
        result = self._visit(tree)
        return self._finalize(result)

    def _collect_function_names(self, tree: ast.AST):
        """第一遍扫描：收集所有函数名"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.function_names.add(node.name)

    def _finalize(self, code: str) -> str:
        """最终处理：添加导入语句等"""
        lines = []

        # 添加标准库导入
        for module in sorted(self.used_stdlib_modules):
            lib_name = STDLIB_MODULE_MAP.get(module, module)
            lines.append(f"入{lib_name}。")

        # 添加桥接模块导入
        for module in sorted(self.bridged_modules):
            var_name = module.split('.')[-1]
            lines.append(f"定{var_name}=引入Python\"{module}\"。")

        if lines:
            lines.append('')

        # 添加主代码
        lines.append(code)

        return '\n'.join(lines)

    def _visit(self, node: ast.AST) -> str:
        """访问 AST 节点"""
        method_name = f'_visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self._generic_visit)
        try:
            return visitor(node)
        except Exception as e:
            lineno = getattr(node, 'lineno', '?')
            raise ConversionError(f"转换错误 (行 {lineno}): {e}")

    def _generic_visit(self, node: ast.AST) -> str:
        """通用访问方法（未实现时调用）"""
        raise ConversionError(f"不支持的语法: {type(node).__name__}")

    def _indent(self) -> str:
        """获取当前缩进"""
        return self.indent_str * self.indent_level

    def _with_indent(self, code: str) -> str:
        """为代码添加缩进"""
        if '\n' in code:
            lines = code.split('\n')
            return '\n'.join(self._indent() + line for line in lines)
        return self._indent() + code

    # ============ 模块 ============

    def _visit_Module(self, node: ast.Module) -> str:
        """处理模块"""
        statements = []
        for stmt in node.body:
            code = self._visit(stmt)
            if code:
                statements.append(code)
        return '\n'.join(statements)

    # ============ 导入语句 ============

    def _visit_Import(self, node: ast.Import) -> str:
        """处理 import 语句"""
        results = []
        for alias in node.names:
            module = alias.name
            asname = alias.asname or module
            base_module = module.split('.')[0]
            self.conversion_report.total_imports += 1

            if base_module in STDLIB_MODULE_MAP:
                self.used_stdlib_modules.add(base_module)
                self.conversion_report.converted_imports += 1
            elif base_module in THIRD_PARTY_LIBS or '.' in module:
                self.bridged_modules.add(base_module)
                self.conversion_report.bridged_imports += 1
                if asname != module:
                    results.append(f"定{asname}=引入Python\"{base_module}\"。")
                    self.imported_names[asname] = base_module
            else:
                self.bridged_modules.add(base_module)
                self.conversion_report.bridged_imports += 1
                if asname != module:
                    results.append(f"定{asname}=引入Python\"{base_module}\"。")
                    self.imported_names[asname] = base_module
            if asname == module:
                self.imported_names[asname] = base_module
        return '\n'.join(results)

    def _visit_ImportFrom(self, node: ast.ImportFrom) -> str:
        """处理 from ... import 语句"""
        module = node.module or ''
        results = []
        self.conversion_report.total_imports += 1

        base_module = module.split('.')[0] if module else ''

        if base_module in STDLIB_MODULE_MAP:
            self.used_stdlib_modules.add(base_module)
            self.conversion_report.converted_imports += 1
            for alias in node.names:
                local_name = alias.asname or alias.name
                self.imported_names[local_name] = module
        elif base_module in THIRD_PARTY_LIBS or (base_module and '.' in module):
            self.bridged_modules.add(base_module)
            self.conversion_report.bridged_imports += 1
            for alias in node.names:
                name = alias.name
                asname = alias.asname or name
                results.append(f"定{asname}=引入Python\"{base_module}\"之{name}。")
                self.imported_names[asname] = base_module
        else:
            if base_module:
                self.bridged_modules.add(base_module)
                self.conversion_report.bridged_imports += 1
                for alias in node.names:
                    name = alias.name
                    asname = alias.asname or name
                    results.append(f"定{asname}=引入Python\"{base_module}\"之{name}。")
                    self.imported_names[asname] = base_module

        return '\n'.join(results)

    # ============ 赋值语句 ============

    def _visit_Assign(self, node: ast.Assign) -> str:
        """处理赋值语句"""
        if len(node.targets) != 1:
            raise ConversionError("仅支持单目标赋值")

        target = node.targets[0]
        value_code = self._visit(node.value)

        if isinstance(target, ast.Name):
            name = target.id
            self.local_vars.add(name)
            return f"定{name}={value_code}。"

        elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
            names = [elt.id for elt in target.elts
                     if isinstance(elt, ast.Name)]
            for n in names:
                self.local_vars.add(n)
            if isinstance(node.value, ast.Tuple) or isinstance(node.value, ast.List):
                elts_code = ', '.join(self._visit(e) for e in node.value.elts)
                return '\n'.join(f"定{name}={val}。" for name, val in zip(names, elts_code.split(', ')))
            return '\n'.join(f"定{name}=入{value_code}{i}。" for i, name in enumerate(names))

        elif isinstance(target, ast.Subscript):
            target_code = self._visit(target.value)
            slice_code = self._visit(target.slice)
            return f"{target_code}，设{slice_code}{value_code}。"

        elif isinstance(target, ast.Attribute):
            target_code = self._visit(target.value)
            return f"{target_code}，设{target.attr}{value_code}。"

        return f"定{self._visit(target)}={value_code}。"

    def _visit_AnnAssign(self, node: ast.AnnAssign) -> str:
        """处理带类型注解的赋值"""
        if node.value is None:
            return ''
        target = node.target
        value_code = self._visit(node.value)
        if isinstance(target, ast.Name):
            self.local_vars.add(target.id)
            return f"定{target.id}={value_code}。"
        return f"定{self._visit(target)}={value_code}。"

    def _visit_AugAssign(self, node: ast.AugAssign) -> str:
        """处理增强赋值（+=, -= 等）"""
        target = self._visit(node.target)
        op_map = {
            ast.Add: '加', ast.Sub: '减', ast.Mult: '乘', ast.Div: '除',
            ast.Mod: '模', ast.Pow: '幂',
        }
        op = op_map.get(type(node.op), '?')
        value = self._visit(node.value)
        return f"设{target}={target}{op}{value}。"

    # ============ 表达式 ============

    def _visit_Expr(self, node: ast.Expr) -> str:
        """处理表达式语句"""
        code = self._visit(node.value)
        return f"{code}。"

    def _visit_BinOp(self, node: ast.BinOp) -> str:
        """处理二元运算"""
        left = self._visit(node.left)
        right = self._visit(node.right)
        op = BINOP_MAP.get(type(node.op), '?')
        return f"{left}{op}{right}"

    def _visit_Compare(self, node: ast.Compare) -> str:
        """处理比较运算"""
        left = self._visit(node.left)
        ops = []
        comparators = [self._visit(c) for c in node.comparators]

        for i, op in enumerate(node.ops):
            op_name = CMPOP_MAP.get(type(op), '?')
            if i == 0:
                ops.append(f"{left}{op_name}{comparators[i]}")
            else:
                ops.append(f"{comparators[i-1]}{op_name}{comparators[i]}")

        if len(ops) == 1:
            return ops[0]
        return '且'.join(ops)

    def _visit_BoolOp(self, node: ast.BoolOp) -> str:
        """处理布尔运算"""
        op = BOOLOP_MAP.get(type(node.op), '?')
        values = [self._visit(v) for v in node.values]
        return op.join(values)

    def _visit_UnaryOp(self, node: ast.UnaryOp) -> str:
        """处理一元运算"""
        operand = self._visit(node.operand)
        op = UNARYOP_MAP.get(type(node.op), '?')
        if op:
            return f"{op}{operand}"
        return operand

    def _visit_Call(self, node: ast.Call) -> str:
        """处理函数调用"""
        func = self._visit(node.func)
        args = [self._visit(a) for a in node.args]
        keywords = {kw.arg: self._visit(kw.value) for kw in node.keywords if kw.arg}

        # 识别内置函数
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            # 检查是否是从标准库导入的函数
            if func_name in self.imported_names:
                source_module = self.imported_names[func_name]
                if source_module in STDLIB_MODULE_MAP:
                    self.used_stdlib_modules.add(source_module.split('.')[0])
                local_key = (source_module, func_name)
                if local_key in STDLIB_FUNC_MAP:
                    yan_func = STDLIB_FUNC_MAP[local_key]
                    return f"{yan_func}{' '.join(args)}"
            if func_name in BUILTIN_FUNC_MAP:
                yan_func = BUILTIN_FUNC_MAP[func_name]
                if yan_func == '印':
                    return f"印{''.join(args)}"
                if yan_func == '长':
                    return f"{args[0]}，长"
                if yan_func == '范围':
                    if len(args) == 1:
                        return f"范围{args[0]}"
                    elif len(args) == 2:
                        return f"范围{args[0]}{args[1]}"
                    return f"范围{''.join(args)}"
                if yan_func == '皆':
                    return f"{args[1]}，皆{args[0]}。"
                if yan_func == '只':
                    return f"{args[1]}，只{args[0]}。"
                if yan_func == '绝对':
                    return f"绝对{args[0]}"
                if yan_func == '总和':
                    return f"{args[0]}，归加0"
                if yan_func == '转整数':
                    return f"转整数{args[0]}"
                if yan_func == '转字符串':
                    return f"转字符串{args[0]}"
                if yan_func == '转浮点':
                    return f"转浮点{args[0]}"
                if yan_func == '转列表':
                    return f"转列表{args[0]}"
                if yan_func == '排序':
                    return f"{args[0]}，排序。"
                if yan_func == '反转':
                    return f"{args[0]}，反转。"
                if yan_func == '枚举':
                    return f"{args[0]}，枚举。"
                if yan_func == '拉链':
                    return f"{' '.join(args)}，拉链。"
                if yan_func == '最大':
                    return f"最大{' '.join(args)}"
                if yan_func == '最小':
                    return f"最小{' '.join(args)}"
                if yan_func == '四舍五入':
                    return f"四舍五入{args[0]}"
                if yan_func == '输入':
                    return f"输入{args[0] if args else ''}"
                if yan_func == '是实例':
                    return f"{yan_func}{' '.join(args)}"
                return f"{yan_func}{' '.join(args)}"

        # 识别标准库函数调用（支持 os.path.join 等嵌套路径）
        if isinstance(node.func, ast.Attribute):
            full_path = self._extract_attr_path(node.func)
            parts = full_path.split('.')
            if len(parts) >= 2:
                module = parts[0]
                func_key = '.'.join(parts[1:])
                key = (module, func_key)
                if key in STDLIB_FUNC_MAP:
                    yan_func = STDLIB_FUNC_MAP[key]
                    return f"{yan_func}{' '.join(args)}"
                # 尝试 module.类.func 模式（如 datetime.datetime.now）
                alt_key = (module, f"{module}.{func_key}")
                if alt_key in STDLIB_FUNC_MAP:
                    yan_func = STDLIB_FUNC_MAP[alt_key]
                    return f"{yan_func}{' '.join(args)}"

        # isinstance(x, int) 等类型检查
        if isinstance(node.func, ast.Name) and node.func.id == 'isinstance':
            obj = self._visit(node.args[0])
            type_name = self._visit(node.args[1]) if len(node.args) > 1 else ''
            type_short = type_name.replace('转', '').replace('类型', '')
            return f"{obj}是{type_short}类型"

        # 方法调用：对象.方法(参数)
        if isinstance(node.func, ast.Attribute):
            obj_code = self._visit(node.func.value)
            method = node.func.attr
            if method == 'append':
                return f"{obj_code}，添{args[0]}"
            if method == 'join':
                return f"{args[0]}，连接{obj_code}"
            if method == 'split':
                return f"{obj_code}，分割{args[0] if args else ''}"
            if method == 'strip':
                return f"{obj_code}，去空"
            if method == 'lower':
                return f"{obj_code}，小写"
            if method == 'upper':
                return f"{obj_code}，大写"
            if method == 'replace':
                return f"{obj_code}，替换{args[0]}{args[1] if len(args) > 1 else ''}"
            if method == 'find':
                return f"{obj_code}，查找{args[0]}"
            if method == 'startswith':
                return f"{obj_code}，开头是{args[0]}"
            if method == 'endswith':
                return f"{obj_code}，结尾是{args[0]}"
            if method == 'format':
                return f"{obj_code}，格式化{' '.join(args)}"
            if method == 'items':
                return f"{obj_code}，项"
            if method == 'keys':
                return f"{obj_code}，键"
            if method == 'values':
                return f"{obj_code}，值"
            if method == 'get':
                return f"{obj_code}，取{args[0]}"
            if method == 'pop':
                return f"{obj_code}，弹出{args[0] if args else ''}"
            if method == 'sort':
                return f"{obj_code}，排序"
            if method == 'reverse':
                return f"{obj_code}，反转"
            if method == 'extend':
                return f"{obj_code}，扩展{args[0]}"
            if method == 'remove':
                return f"{obj_code}，移除{args[0]}"
            if method == 'count':
                return f"{obj_code}，计数{args[0]}"
            if method == 'index':
                return f"{obj_code}，索引{args[0]}"
            if method == 'clear':
                return f"{obj_code}，清空"
            if method == 'copy':
                return f"{obj_code}，复制"
            if method == 'read':
                return f"{obj_code}，读"
            if method == 'write':
                return f"{obj_code}，写{args[0]}"
            if method == 'readlines':
                return f"{obj_code}，读行"
            if method == 'writelines':
                return f"{obj_code}，写行{args[0]}"

            # 桥接模块的方法调用
            if isinstance(node.func.value, ast.Name) and node.func.value.id in self.bridged_modules:
                return f"{obj_code}{method}{' '.join(args)}"

            return f"{obj_code}，{method}{' '.join(args)}"

        # 普通函数调用
        if isinstance(node.func, ast.Name) and node.func.id in self.function_names:
            if args:
                return f"{node.func.id} {' '.join(args)}"
            return node.func.id

        if args:
            return f"{func} {' '.join(args)}"
        return func

    def _visit_Name(self, node: ast.Name) -> str:
        """处理变量名"""
        return node.id

    def _visit_Constant(self, node: ast.Constant) -> str:
        """处理常量"""
        if node.value is None:
            return '空'
        if node.value is True:
            return '真'
        if node.value is False:
            return '假'
        if isinstance(node.value, str):
            return repr(node.value)
        if isinstance(node.value, (int, float)):
            return str(node.value)
        if isinstance(node.value, bytes):
            return repr(node.value)
        return str(node.value)

    def _visit_Num(self, node: ast.Num) -> str:
        """处理数字（兼容旧版 Python）"""
        return str(node.n)

    def _visit_Str(self, node: ast.Str) -> str:
        """处理字符串（兼容旧版 Python）"""
        return repr(node.s)

    def _visit_JoinedStr(self, node: ast.JoinedStr) -> str:
        """处理 f-string"""
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                expr_code = self._visit(value.value)
                parts.append(f"\"+转字符串{expr_code}+\"")
        result = ''.join(parts)
        if result.startswith('"+"') and result.endswith('+"'):
            result = result[3:-3]
        elif result.startswith('"+"'):
            result = result[3:]
        elif result.endswith('+"'):
            result = result[:-3]
        if result and not result.startswith('"'):
            result = f'""{result}'
        if result and not result.endswith('"'):
            result = f'{result}""'
        return result if result else '""'

    def _visit_FormattedValue(self, node: ast.FormattedValue) -> str:
        """处理格式化值"""
        return self._visit(node.value)

    # ============ 列表和字典 ============

    def _visit_List(self, node: ast.List) -> str:
        """处理列表字面量"""
        elts = [self._visit(e) for e in node.elts]
        return f"列{' '.join(elts)}"

    def _visit_Tuple(self, node: ast.Tuple) -> str:
        """处理元组字面量"""
        elts = [self._visit(e) for e in node.elts]
        return f"列{' '.join(elts)}"

    def _visit_Dict(self, node: ast.Dict) -> str:
        """处理字典字面量"""
        if not node.keys:
            return "典"
        items = []
        for k, v in zip(node.keys, node.values):
            key_code = self._visit(k)
            val_code = self._visit(v)
            items.append(f"列{key_code}{val_code}")
        return f"典{' '.join(items)}"

    def _visit_Set(self, node: ast.Set) -> str:
        """处理集合字面量"""
        elts = [self._visit(e) for e in node.elts]
        return f"集{' '.join(elts)}"

    def _visit_Subscript(self, node: ast.Subscript) -> str:
        """处理下标访问"""
        value = self._visit(node.value)
        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int):
            return f"{value}，入{node.slice.value}。"
        if isinstance(node.slice, ast.Slice):
            lower = self._visit(node.slice.lower) if node.slice.lower else ''
            upper = self._visit(node.slice.upper) if node.slice.upper else ''
            if lower and not upper:
                return f"{value}，余{lower}。"
            if not lower and upper:
                return f"{value}，首{upper}。"
            return f"{value}，截取{lower}{upper}。"
        slice_code = self._visit(node.slice)
        return f"{value}，入{slice_code}。"

    def _visit_Slice(self, node: ast.Slice) -> str:
        """处理切片"""
        parts = []
        if node.lower:
            parts.append(self._visit(node.lower))
        if node.upper:
            parts.append(self._visit(node.upper))
        return ' '.join(parts)

    def _visit_Index(self, node: ast.Index) -> str:
        """处理索引（兼容旧版 Python）"""
        return self._visit(node.value)

    # ============ 条件语句 ============

    def _visit_If(self, node: ast.If) -> str:
        """处理条件语句"""
        test = self._visit(node.test)
        body_code = self._visit_body(node.body)
        result = f"若{test}则：\n{body_code}"

        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                else_code = self._visit(node.orelse[0])
                result += f"\n{self._indent()}否则{else_code}"
            else:
                else_body = self._visit_body(node.orelse)
                result += f"\n{self._indent()}否则：\n{else_body}"

        return result

    def _visit_body(self, body: List[ast.stmt]) -> str:
        """处理语句体"""
        self.indent_level += 1
        statements = []
        for stmt in body:
            code = self._visit(stmt)
            if code:
                statements.append(self._with_indent(code))
        self.indent_level -= 1
        return '\n'.join(statements)

    # ============ 循环语句 ============

    def _visit_For(self, node: ast.For) -> str:
        """处理 for 循环"""
        target = self._visit(node.target)
        iter_code = self._visit(node.iter)
        self.loop_var_stack.append(target)
        body_code = self._visit_body(node.body)
        self.loop_var_stack.pop()

        result = f"遍历{target}于{iter_code}：\n{body_code}"

        if node.orelse:
            else_body = self._visit_body(node.orelse)
            result += f"\n{self._indent()}否则：\n{else_body}"

        return result

    def _visit_While(self, node: ast.While) -> str:
        """处理 while 循环"""
        test = self._visit(node.test)
        body_code = self._visit_body(node.body)
        result = f"当{test}：\n{body_code}"

        if node.orelse:
            else_body = self._visit_body(node.orelse)
            result += f"\n{self._indent()}否则：\n{else_body}"

        return result

    def _visit_Break(self, node: ast.Break) -> str:
        """处理 break"""
        return "跳出。"

    def _visit_Continue(self, node: ast.Continue) -> str:
        """处理 continue"""
        return "继续。"

    # ============ 函数定义 ============

    def _visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        """处理函数定义"""
        name = node.name
        args = [arg.arg for arg in node.args.args]
        args_str = ' '.join(args) if args else '_'

        self.function_names.add(name)
        old_in_function = self.in_function_body
        self.in_function_body = True

        # 检查是否有 return 语句
        has_return = any(isinstance(stmt, ast.Return) for stmt in
                         ast.walk(node))

        if has_return or len(node.body) > 1:
            self.indent_level += 1
            body_lines = []
            for i, stmt in enumerate(node.body):
                code = self._visit(stmt)
                if code:
                    body_lines.append(self._with_indent(code))
            self.indent_level -= 1
            body_code = '\n'.join(body_lines)
            result = f"定{name}=函{args_str}：\n{body_code}"
        else:
            body_code = self._visit(node.body[0])
            result = f"定{name}=函{args_str}{body_code}"

        self.in_function_body = old_in_function
        return result

    def _visit_Return(self, node: ast.Return) -> str:
        """处理 return 语句"""
        if node.value is None:
            return "返回空。"
        value = self._visit(node.value)
        return f"返回{value}。"

    def _visit_Lambda(self, node: ast.Lambda) -> str:
        """处理 lambda 表达式"""
        args = [arg.arg for arg in node.args.args]
        args_str = ' '.join(args) if args else '_'
        body = self._visit(node.body)
        return f"函{args_str}{body}"

    # ============ 列表推导式 ============

    def _extract_attr_path(self, node: ast.AST) -> str:
        """提取属性链的完整路径，如 ast.Attribute(ast.Attribute(Name('os'), 'path'), 'join') -> 'os.path'"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._extract_attr_path(node.value)}.{node.attr}"
        return self._visit(node)

    def _visit_ListComp(self, node: ast.ListComp) -> str:
        """处理列表推导式"""
        generator = node.generators[0]
        iter_code = self._visit(generator.iter)
        target = generator.target.id

        parts = [iter_code]

        for if_clause in generator.ifs:
            cond = self._visit(if_clause)
            parts.append(f"只函{target}{cond}")

        body = self._visit(node.elt)
        parts.append(f"皆函{target}{body}")

        return '，'.join(parts)

    def _visit_DictComp(self, node: ast.DictComp) -> str:
        """处理字典推导式"""
        key = self._visit(node.key)
        value = self._visit(node.value)
        generator = node.generators[0]
        iter_code = self._visit(generator.iter)
        target = generator.target.id

        lines = []
        lines.append(f"定结果=典。")
        lines.append(f"遍历{target}于{iter_code}：")
        self.indent_level += 1
        lines.append(self._with_indent(f"结果，设{key}{value}。"))
        self.indent_level -= 1
        return '\n'.join(lines)

    def _visit_SetComp(self, node: ast.SetComp) -> str:
        """处理集合推导式"""
        elt = self._visit(node.elt)
        generator = node.generators[0]
        iter_code = self._visit(generator.iter)
        target = generator.target.id
        return f"{iter_code}，皆函{target}{elt}，转集合。"

    def _visit_GeneratorExp(self, node: ast.GeneratorExp) -> str:
        """处理生成器表达式（转换为列表）"""
        return self._visit_ListComp(node)

    # ============ 上下文管理器 ============

    def _visit_With(self, node: ast.With) -> str:
        """处理 with 语句"""
        results = []
        for item in node.items:
            context_expr = self._visit(item.context_expr)
            if isinstance(item.context_expr, ast.Call):
                if isinstance(item.context_expr.func, ast.Name):
                    func_name = item.context_expr.func.id
                    if func_name == 'open':
                        args = [self._visit(a) for a in item.context_expr.args]
                        file_path = args[0] if args else ''
                        mode = args[1] if len(args) > 1 else '"r"'
                        if 'r' in mode:
                            results.append(f"定内容=读文件{file_path}。")
                        elif 'w' in mode:
                            results.append(f"写文件{file_path}内容。")
                        elif 'a' in mode:
                            results.append(f"追加文件{file_path}内容。")
                        continue
            if item.optional_vars:
                var_name = self._visit(item.optional_vars)
                results.append(f"定{var_name}={context_expr}。")

        body_code = self._visit_body(node.body)
        results.append(body_code)
        return '\n'.join(results)

    def _visit_withitem(self, node: ast.withitem) -> str:
        """处理 with 项"""
        return self._visit(node.context_expr)

    # ============ 异常处理 ============

    def _visit_Try(self, node: ast.Try) -> str:
        """处理 try 语句"""
        body_code = self._visit_body(node.body)
        result = f"尝试：\n{body_code}"

        for handler in node.handlers:
            handler_code = self._visit(handler)
            result += f"\n{handler_code}"

        if node.orelse:
            else_body = self._visit_body(node.orelse)
            result += f"\n{self._indent()}否则：\n{else_body}"

        if node.finalbody:
            final_body = self._visit_body(node.finalbody)
            result += f"\n{self._indent()}最终：\n{final_body}"

        return result

    def _visit_ExceptHandler(self, node: ast.ExceptHandler) -> str:
        """处理 except 子句"""
        if node.type:
            type_code = self._visit(node.type)
            body_code = self._visit_body(node.body)
            return f"捕获{type_code}：\n{body_code}"
        else:
            body_code = self._visit_body(node.body)
            return f"捕获：\n{body_code}"

    def _visit_Raise(self, node: ast.Raise) -> str:
        """处理 raise 语句"""
        if node.exc:
            exc_code = self._visit(node.exc)
            return f"抛出{exc_code}。"
        return "抛出。"

    # ============ 类定义 ============

    def _is_dataclass(self, node: ast.ClassDef) -> bool:
        """检查是否为 @dataclass 类"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'dataclass':
                return True
            if isinstance(decorator, ast.Attribute) and decorator.attr == 'dataclass':
                return True
        return False

    def _is_enum(self, node: ast.ClassDef) -> bool:
        """检查是否为 Enum 类"""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'Enum':
                return True
        return False

    def _visit_dataclass(self, node: ast.ClassDef) -> str:
        """处理 @dataclass 类定义（转换为 tagged list 构造器）"""
        fields = []
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign):
                field_name = stmt.target.id if isinstance(stmt.target, ast.Name) else None
                if field_name:
                    if stmt.value:
                        default_val = self._visit(stmt.value)
                        fields.append((field_name, default_val, True))
                    else:
                        fields.append((field_name, None, False))

        # 分离必需和可选参数
        required = [f for f in fields if not f[2]]
        optional = [f for f in fields if f[2]]

        required_names = [f[0] for f in required]
        optional_names = [f[0] for f in optional]
        all_param_names = required_names + optional_names

        args_str = ' '.join(all_param_names) if all_param_names else '_'
        lines = [f"-- 类 {node.name} 转换为 tagged list"]
        lines.append(f"定创建{node.name}=函{args_str}：")

        self.indent_level += 1
        # 设置默认值
        for fname, default, has_default in optional:
            lines.append(self._with_indent(f"定{fname}={default}。"))

        # 构建 tagged list: 列"TypeName" field1 field2 ...
        list_parts = [f'列"{node.name}"']
        list_parts.extend(f[0] for f in fields)
        lines.append(self._with_indent(f"返回{' '.join(list_parts)}。"))
        self.indent_level -= 1

        # 生成类型检查函数
        lines.append(f"定是{node.name}=函节点：")
        self.indent_level += 1
        lines.append(self._with_indent(f"等首节点\"{node.name}\"。"))
        self.indent_level -= 1

        return '\n'.join(lines)

    def _visit_Enum(self, node: ast.ClassDef) -> str:
        """处理 Enum 类定义（转换为字符串常量）"""
        lines = [f"-- 枚举 {node.name} 转换为字符串常量"]
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        lines.append(f'定{node.name}_{target.id}="{target.id}"。')
        return '\n'.join(lines)

    def _visit_ClassDef(self, node: ast.ClassDef) -> str:
        """处理类定义（转换为函数式实现）"""
        if self._is_dataclass(node):
            return self._visit_dataclass(node)
        if self._is_enum(node):
            return self._visit_Enum(node)

        lines = []
        init_method = None
        methods = []

        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                if stmt.name == '__init__':
                    init_method = stmt
                else:
                    methods.append(stmt)

        if init_method:
            args = [arg.arg for arg in init_method.args.args[1:]]
            args_str = ' '.join(args) if args else '_'
            lines.append(f"-- 类 {node.name} 转换为函数式")
            lines.append(f"定创建{node.name}=函{args_str}：")
            self.indent_level += 1
            for stmt in init_method.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                            attr_name = target.attr
                            val_code = self._visit(stmt.value)
                            lines.append(self._with_indent(f"列{attr_name}{val_code}。"))
                elif isinstance(stmt, ast.Expr):
                    code = self._visit(stmt)
                    if code:
                        lines.append(self._with_indent(code))
            self.indent_level -= 1

        for method in methods:
            method_name = method.name
            args = [arg.arg for arg in method.args.args]
            args_str = ' '.join(args) if args else '_'
            lines.append(f"定{node.name}_{method_name}=函{args_str}：")
            self.indent_level += 1
            for stmt in method.body:
                code = self._visit(stmt)
                if code:
                    lines.append(self._with_indent(code))
            self.indent_level -= 1

        return '\n'.join(lines)

    # ============ 装饰器 ============

    # ============ 其他语句 ============

    def _visit_Pass(self, node: ast.Pass) -> str:
        """处理 pass"""
        return ""

    def _visit_Delete(self, node: ast.Delete) -> str:
        """处理 del 语句"""
        targets = [self._visit(t) for t in node.targets]
        return f"删{' '.join(targets)}。"

    def _visit_Global(self, node: ast.Global) -> str:
        """处理 global 语句"""
        return f"全局{' '.join(node.names)}。"

    def _visit_Nonlocal(self, node: ast.Nonlocal) -> str:
        """处理 nonlocal 语句"""
        return f"非局部{' '.join(node.names)}。"

    def _visit_Yield(self, node: ast.Yield) -> str:
        """处理 yield"""
        if node.value:
            value = self._visit(node.value)
            return f"产出{value}"
        return "产出"

    def _visit_YieldFrom(self, node: ast.YieldFrom) -> str:
        """处理 yield from"""
        value = self._visit(node.value)
        return f"产出{value}"

    def _visit_Await(self, node: ast.Await) -> str:
        """处理 await"""
        value = self._visit(node.value)
        return f"等待{value}"

    def _visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> str:
        """处理异步函数定义"""
        return self._visit_FunctionDef(node)

    def _visit_AsyncFor(self, node: ast.AsyncFor) -> str:
        """处理异步 for 循环"""
        return self._visit_For(node)

    def _visit_AsyncWith(self, node: ast.AsyncWith) -> str:
        """处理异步 with 语句"""
        return self._visit_With(node)

    def _visit_IfExp(self, node: ast.IfExp) -> str:
        """处理三元表达式"""
        test = self._visit(node.test)
        body = self._visit(node.body)
        orelse = self._visit(node.orelse)
        return f"若{test}则{body}否则{orelse}"

    def _visit_Attribute(self, node: ast.Attribute) -> str:
        """处理属性访问"""
        # 检查是否为标准库常量（如 math.pi）
        if isinstance(node.value, ast.Name):
            module_name = node.value.id
            const_key = (module_name, node.attr)
            if const_key in STDLIB_CONST_MAP:
                return STDLIB_CONST_MAP[const_key]
        value = self._visit(node.value)
        return f"{value}，{node.attr}"

    def _visit_Starred(self, node: ast.Starred) -> str:
        """处理 starred 表达式"""
        value = self._visit(node.value)
        return f"展开{value}"

    def _visit_Assert(self, node: ast.Assert) -> str:
        """处理 assert 语句"""
        test = self._visit(node.test)
        if node.msg:
            msg = self._visit(node.msg)
            return f"断言{test}，{msg}。"
        return f"断言{test}。"

    def _visit_ImportStar(self, node) -> str:
        """处理 from module import *"""
        return ""


class ConversionReport:
    """转换报告"""

    def __init__(self):
        self.total_imports = 0
        self.converted_imports = 0
        self.bridged_imports = 0
        self.unsupported_imports = 0

    def generate(self) -> str:
        """生成转换报告"""
        if self.total_imports == 0:
            return "无导入语句需要处理。"

        converted_rate = self.converted_imports / self.total_imports * 100
        bridged_rate = self.bridged_imports / self.total_imports * 100

        return f"""
转换报告：
- 总导入数：{self.total_imports}
- 已转换（言语言标准库）：{self.converted_imports}（{converted_rate:.1f}%）
- 已桥接（Python 桥接）：{self.bridged_imports}（{bridged_rate:.1f}%）
- 不支持：{self.unsupported_imports}

转换率：{converted_rate:.1f}%
桥接率：{bridged_rate:.1f}%
"""


def convert_python_file(input_path: str, output_path: str = None,
                        verify: bool = False) -> str:
    """转换 Python 文件为言语言代码

    参数：
        input_path: Python 源文件路径
        output_path: 输出文件路径（可选）
        verify: 是否验证转换

    返回：
        生成的言语言代码
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        python_code = f.read()

    converter = PythonToYanConverter()
    yan_code = converter.convert(python_code)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yan_code)
        print(f"✓ 已生成: {output_path}")

    if verify:
        print(converter.conversion_report.generate())

    return yan_code


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Python 到言语言代码转换器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python py2yan.py example.py -o example.yan
  python py2yan.py example.py -o example.yan -v
  python py2yan.py example.py --stdout
        """
    )
    parser.add_argument('input', help='Python 源文件')
    parser.add_argument('-o', '--output', help='输出文件')
    parser.add_argument('-v', '--verify', action='store_true',
                        help='验证转换并生成报告')
    parser.add_argument('--stdout', action='store_true',
                        help='输出到控制台')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误: 文件不存在: {args.input}")
        sys.exit(1)

    try:
        yan_code = convert_python_file(
            args.input,
            output_path=args.output,
            verify=args.verify
        )

        if args.stdout or not args.output:
            print(yan_code)

    except ConversionError as e:
        print(f"转换错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()