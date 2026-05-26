"""
言语言 JavaScript 代码生成器
"""

from typing import Dict, Any, Optional
from nodes import *


class JSCodeGenError(Exception):
    pass


class JavaScriptCodeGen:
    """JavaScript 代码生成器"""

    def __init__(self):
        # 用户定义的函数/变量：名称 -> 元数
        self.user_defined: Dict[str, int] = {}
        # 生成的辅助函数
        self.helpers: Dict[str, str] = {}

    def generate(self, node: Node) -> str:
        """生成 JavaScript 代码"""
        if isinstance(node, Program):
            return self._gen_program(node)
        elif isinstance(node, Num):
            return repr(node.value)
        elif isinstance(node, Str):
            return repr(node.value)
        elif isinstance(node, Bool):
            return 'true' if node.value else 'false'
        elif isinstance(node, Nil):
            return 'null'
        elif isinstance(node, MathExpr):
            return f'({node.expr})'
        elif isinstance(node, PythonCode):
            return f'/* Python code: {node.code} */'
        elif isinstance(node, Continue):
            return 'continue'
        elif isinstance(node, ListLiteral):
            return self._gen_list(node)
        elif isinstance(node, Word):
            return node.name
        elif isinstance(node, Call):
            return self._gen_call(node)
        elif isinstance(node, Pipeline):
            return self._gen_pipeline(node)
        elif isinstance(node, Quote):
            return self._gen_quote(node)
        elif isinstance(node, Define):
            return self._gen_define(node)
        elif isinstance(node, Lambda):
            return self._gen_lambda(node)
        elif isinstance(node, Block):
            return self._gen_block(node)
        elif isinstance(node, If):
            return self._gen_if(node)
        elif isinstance(node, ForEach):
            return self._gen_foreach(node)
        elif isinstance(node, While):
            return self._gen_while(node)
        elif isinstance(node, Import):
            return self._gen_import(node)
        elif isinstance(node, Export):
            return self._gen_export(node)
        elif isinstance(node, StructDef):
            return self._gen_struct_def(node)
        elif isinstance(node, StructInit):
            return self._gen_struct_init(node)
        else:
            raise JSCodeGenError(f"未知节点类型: {type(node)}")

    def _gen_program(self, node: Program) -> str:
        """生成完整的 JavaScript 程序"""
        lines = []
        
        # 添加辅助函数
        lines.extend(self._gen_helpers())
        
        # 添加主代码
        for stmt in node.statements:
            code = self.generate(stmt)
            if code:
                lines.append(code)
        
        return '\n\n'.join(lines)

    def _gen_helpers(self) -> list:
        """生成 JavaScript 辅助函数"""
        helpers = []
        
        # 基础运行时函数
        helpers.append("""
// 言语言 JavaScript 运行时
const YanRuntime = {
    // 数学函数
    加: (a, b) => a + b,
    减: (a, b) => a - b,
    乘: (a, b) => a * b,
    除: (a, b) => a / b,
    模: (a, b) => a % b,
    幂: (a, b) => Math.pow(a, b),
    绝对: (x) => Math.abs(x),
    负: (x) => -x,
    
    // 比较函数
    大: (a, b) => a > b,
    小: (a, b) => a < b,
    等: (a, b) => a == b,
    不等: (a, b) => a != b,
    
    // 逻辑函数
    且: (a, b) => a && b,
    或: (a, b) => a || b,
    非: (x) => !x,
    
    // 列表函数
    列: (...args) => args,
    首: (arr) => arr[0],
    余: (arr) => arr.slice(1),
    入: (arr, idx) => arr[idx],
    长: (arr) => arr.length,
    添: (arr, val) => { arr.push(val); return arr; },
    连: (arr1, arr2) => arr1.concat(arr2),
    反: (arr) => [...arr].reverse(),
    排: (arr) => [...arr].sort(),
    最大: (arr) => Math.max(...arr),
    最小: (arr) => Math.min(...arr),
    求和: (arr) => arr.reduce((a, b) => a + b, 0),
    计数: (arr, val) => arr.filter(x => x == val).length,
    
    // 高阶函数
    皆: (fn, arr) => arr.map(fn),
    只: (fn, arr) => arr.filter(fn),
    归: (fn, init, arr) => arr.reduce(fn, init),
    
    // 输入输出
    印: (...args) => console.log(...args),
    读: () => prompt(),
    
    // 字符串函数
    连接: (a, b) => a + b,
    分割: (str, sep) => str.split(sep),
    替换: (str, old, newStr) => str.replace(old, newStr),
    截取: (str, start, end) => str.slice(start, end),
    小写: (str) => str.toLowerCase(),
    大写: (str) => str.toUpperCase(),
    查找: (str, substr) => str.indexOf(substr),
    包含: (str, substr) => str.includes(substr),
    去空: (str) => str.trim(),
    开头是: (str, prefix) => str.startsWith(prefix),
    结尾是: (str, suffix) => str.endsWith(suffix),
    
    // 数学函数
    正弦: (x) => Math.sin(x),
    余弦: (x) => Math.cos(x),
    正切: (x) => Math.tan(x),
    反正弦: (x) => Math.asin(x),
    反余弦: (x) => Math.acos(x),
    反正切: (x) => Math.atan(x),
    指数: (x) => Math.exp(x),
    对数: (x) => Math.log(x),
    对数10: (x) => Math.log10(x),
    开方: (x) => Math.sqrt(x),
    取整: (x) => Math.floor(x),
    进位: (x) => Math.ceil(x),
    四舍五入: (x) => Math.round(x),
    
    // 随机数
    随机: () => Math.random(),
    随机整数: (min, max) => Math.floor(Math.random() * (max - min + 1)) + min,
    
    // 常量
    圆周率: Math.PI,
    自然常数: Math.E,
    
    // 时间函数
    当前时间: () => Date.now(),
    日期: () => new Date().toLocaleDateString(),
    时间: () => new Date().toLocaleTimeString(),
    日期时间: () => new Date().toLocaleString(),
    格式化时间: (fmt) => {
        const d = new Date();
        return fmt.replace(/yyyy/g, d.getFullYear())
                  .replace(/MM/g, String(d.getMonth() + 1).padStart(2, '0'))
                  .replace(/dd/g, String(d.getDate()).padStart(2, '0'))
                  .replace(/HH/g, String(d.getHours()).padStart(2, '0'))
                  .replace(/mm/g, String(d.getMinutes()).padStart(2, '0'))
                  .replace(/ss/g, String(d.getSeconds()).padStart(2, '0'));
    },
    
    // 类型检查
    是数: (x) => typeof x === 'number',
    是串: (x) => typeof x === 'string',
    是表: (x) => Array.isArray(x),
    是函: (x) => typeof x === 'function',
    是真: (x) => x === true,
    是空: (x) => x === null || x === undefined,
    类型: (x) => typeof x
};

// 便捷别名
const {
    加, 减, 乘, 除, 模, 幂, 绝对, 负,
    大, 小, 等, 不等,
    且, 或, 非,
    列, 首, 余, 入, 长, 添, 连, 反, 排, 最大, 最小, 求和, 计数,
    皆, 只, 归,
    印, 读,
    正弦, 余弦, 正切, 反正弦, 反余弦, 反正切,
    指数, 对数, 对数10, 开方, 取整, 进位, 四舍五入,
    随机, 随机整数, 圆周率, 自然常数,
    当前时间, 日期, 时间, 日期时间, 格式化时间,
    是数, 是串, 是表, 是函, 是真, 是空, 类型
} = YanRuntime;
""")
        
        return helpers

    def _gen_list(self, node: ListLiteral) -> str:
        """生成列表"""
        elements = ', '.join(self.generate(e) for e in node.elements)
        return f'[{elements}]'

    def _gen_call(self, node: Call, pipeline_arg: str = None) -> str:
        """生成函数调用"""
        verb_name = node.verb.name

        # 处理成员访问：obj.attr -> obj.attr
        if verb_name == '.':
            if len(node.args) >= 2:
                obj = self.generate(node.args[0])
                attr = self.generate(node.args[1])
                if isinstance(node.args[1], Word):
                    return f'{obj}.{attr}'
                else:
                    return f'{obj}[{attr}]'
            return verb_name

        # 处理返回语句：返回 value -> return value
        if verb_name == '返回':
            if node.args:
                return f'return {self.generate(node.args[0])}'
            return 'return'

        # 生成参数
        args = [self.generate(a) for a in node.args]

        # 如果有管道参数，插入到参数列表首位
        if pipeline_arg is not None:
            args.insert(0, pipeline_arg)

        # 检查是否是内置函数
        builtin_names = {
            '加', '减', '乘', '除', '模', '幂', '绝对', '负',
            '大', '小', '等', '不等',
            '且', '或', '非',
            '列', '首', '余', '入', '长', '添', '连', '反', '排', '最大', '最小', '求和', '计数',
            '皆', '只', '归',
            '印', '读',
            '正弦', '余弦', '正切', '反正弦', '反余弦', '反正切',
            '指数', '对数', '对数10', '开方', '取整', '进位', '四舍五入',
            '随机', '随机整数', '圆周率', '自然常数',
            '当前时间', '日期', '时间', '日期时间', '格式化时间',
            '是数', '是串', '是表', '是函', '是真', '是空', '类型'
        }

        if verb_name in builtin_names:
            func_name = verb_name
        else:
            func_name = verb_name

        # 如果没有参数，直接返回函数名（可能是变量引用）
        if len(args) == 0:
            return func_name

        # 生成调用
        args_str = ', '.join(args)
        return f'{func_name}({args_str})'

    def _gen_pipeline(self, node: Pipeline) -> str:
        """生成管道表达式"""
        if not node.steps:
            return ''
        
        # 依次处理每个步骤，前一个结果作为后一个的管道参数
        result = None
        for step in node.steps:
            if isinstance(step, Call):
                if result is None:
                    result = self._gen_call(step)
                else:
                    result = self._gen_call(step, result)
            else:
                # 如果不是调用，直接生成代码
                step_code = self.generate(step)
                if result is None:
                    result = step_code
                else:
                    # 管道中的非调用节点，可能是变量引用或值
                    result = step_code
        
        return result or ''

    def _gen_quote(self, node: Quote) -> str:
        """生成引用表达式"""
        # 在 JS 中，引用可以用数组包装表示
        inner = self.generate(node.expr)
        return f'[Symbol.for("quote"), {inner}]'

    def _gen_define(self, node: Define) -> str:
        """生成变量定义"""
        name = node.name
        value = self.generate(node.value)
        
        # 如果是函数定义，记录用户定义
        if isinstance(node.value, Lambda):
            self.user_defined[name] = len(node.value.params)
        
        return f'const {name} = {value};'

    def _gen_lambda(self, node: Lambda) -> str:
        """生成匿名函数"""
        params = ', '.join(node.params) if node.params else ''
        
        if isinstance(node.body, Block):
            body = self._gen_block(node.body)
            return f'({params}) => {{{body}}}'
        else:
            body = self.generate(node.body)
            return f'({params}) => {body}'

    def _gen_block(self, node: Block) -> str:
        """生成代码块"""
        lines = []
        for stmt in node.statements:
            code = self.generate(stmt)
            if code:
                lines.append(code)
        return '\n'.join(lines)

    def _gen_if(self, node: If) -> str:
        """生成条件语句"""
        cond = self.generate(node.cond)
        then_branch = self.generate(node.then_branch)
        else_branch = self.generate(node.else_branch) if node.else_branch else ''
        
        # 检查是否是块
        has_then_block = isinstance(node.then_branch, Block)
        has_else_block = isinstance(node.else_branch, Block)
        
        if else_branch:
            if has_then_block and has_else_block:
                return f'if ({cond}) {{{then_branch}}} else {{{else_branch}}}'
            elif has_then_block:
                return f'if ({cond}) {{{then_branch}}} else {else_branch}'
            elif has_else_block:
                return f'if ({cond}) {then_branch} else {{{else_branch}}}'
            else:
                return f'if ({cond}) {then_branch} else {else_branch}'
        else:
            if has_then_block:
                return f'if ({cond}) {{{then_branch}}}'
            else:
                return f'if ({cond}) {then_branch}'

    def _gen_foreach(self, node: ForEach) -> str:
        """生成遍历循环"""
        var_name = node.var
        iterable = self.generate(node.iterable)
        body = self.generate(node.body)
        
        if isinstance(node.body, Block):
            return f'for (const {var_name} of {iterable}) {{{body}}}'
        else:
            return f'for (const {var_name} of {iterable}) {body}'

    def _gen_while(self, node: While) -> str:
        """生成当循环"""
        cond = self.generate(node.cond)
        body = self.generate(node.body)
        
        if isinstance(node.body, Block):
            return f'while ({cond}) {{{body}}}'
        else:
            return f'while ({cond}) {body}'

    def _gen_import(self, node: Import) -> str:
        """生成导入语句"""
        module_name = node.module_name
        return f'// 导入: {module_name} (在浏览器环境中需要手动处理)'

    def _gen_export(self, node: Export) -> str:
        """生成导出语句"""
        names = ', '.join(node.names)
        return f'export const {names};'

    def _gen_struct_def(self, node: StructDef) -> str:
        """生成结构体定义"""
        fields = []
        for field_name, field_type in node.fields.items():
            fields.append(f'    {field_name}: {self.generate(field_type) if field_type else "null"}')
        
        fields_str = ',\n'.join(fields)
        return f'class {node.name} {{\n{fields_str}\n}}'

    def _gen_struct_init(self, node: StructInit) -> str:
        """生成结构体初始化"""
        struct_name = node.struct_name
        fields = []
        for field_name, field_value in node.fields.items():
            fields.append(f'{field_name}: {self.generate(field_value)}')
        
        fields_str = ', '.join(fields)
        return f'new {struct_name}({{{fields_str}}})'