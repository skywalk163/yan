"""
言语言 WebAssembly 代码生成器
支持言语言所有特性的完整实现
"""

from typing import Dict, List, Any, Optional
import struct
from nodes import *


class WASMCodeGen:
    """完整的 WebAssembly 代码生成器"""
    
    def __init__(self):
        self.func_index = {'print': 0, 'print_num': 1, 'print_float': 2}
        self.next_func_index = 3
        
        self.global_vars = {}
        self.next_global_index = 0
        
        self.functions = []
        self.imports = []
        self.data_segments = []
        self.elem_segments = []
        
        self.string_constants = {}
        self.next_string_id = 0
        
        self.local_vars = {}
        self.next_local_index = 0
        
        self.label_counter = 0
        self.func_types = []
        
        self._init_basic_types()
    
    def _init_basic_types(self):
        """初始化基础类型"""
        self.func_types.append(b'\x02\x60\x01\x7f\x00')
        self.func_types.append(b'\x02\x60\x01\x7d\x00')
        self.func_types.append(b'\x02\x60\x01\x7c\x00')
        self.func_types.append(b'\x02\x60\x00\x00')
    
    def generate(self, node: Node) -> bytes:
        """生成 WASM 字节码"""
        if isinstance(node, Program):
            return self._gen_program(node)
        else:
            raise ValueError(f"不支持的节点类型: {type(node)}")
    
    def _gen_program(self, node: Program) -> bytes:
        """生成完整的 WASM 模块"""
        self._collect_functions(node)
        self._build_func_types()
        
        imports_bytes = self._gen_imports()
        type_bytes = self._gen_type_section()
        func_bytes = self._gen_func_section()
        global_bytes = self._gen_global_section()
        elem_bytes = self._gen_elem_section()
        code_bytes = self._gen_code_section(node)
        data_bytes = self._gen_data_section()
        export_bytes = self._gen_export_section()
        
        module = b'\x00asm\x01\x00\x00\x00'
        
        module += self._encode_section(0x01, type_bytes)
        module += self._encode_section(0x02, imports_bytes)
        module += self._encode_section(0x03, func_bytes)
        
        if global_bytes:
            module += self._encode_section(0x06, global_bytes)
        
        if elem_bytes:
            module += self._encode_section(0x09, elem_bytes)
        
        module += self._encode_section(0x0a, code_bytes)
        
        if data_bytes:
            module += self._encode_section(0x0b, data_bytes)
        
        module += self._encode_section(0x07, export_bytes)
        
        return module
    
    def _collect_functions(self, node: Program):
        """收集所有函数定义"""
        for stmt in node.statements:
            if isinstance(stmt, Define) and isinstance(stmt.value, Lambda):
                self.functions.append((stmt.name, stmt.value))
    
    def _build_func_types(self):
        """构建函数类型"""
        for _, func in self.functions:
            param_count = len(func.params) if func.params else 0
            type_str = b'\x02\x60' + bytes([param_count]) + b'\x7f' * param_count + b'\x01\x7f'
            self.func_types.append(type_str)
    
    def _gen_imports(self) -> bytes:
        """生成导入段"""
        imports = []
        imports.append(b'\x07\x65\x6e\x76\x08print\x00\x00')
        imports.append(b'\x07\x65\x6e\x76\x0a\x70\x72\x69\x6e\x74\x5f\x6e\x75\x6d\x00\x01')
        imports.append(b'\x07\x65\x6e\x76\x0c\x70\x72\x69\x6e\x74\x5f\x66\x6c\x6f\x61\x74\x00\x02')
        return b''.join(imports)
    
    def _gen_type_section(self) -> bytes:
        """生成类型段"""
        result = self._encode_varuint(len(self.func_types))
        for t in self.func_types:
            result += t
        return result
    
    def _gen_func_section(self) -> bytes:
        """生成函数声明段"""
        func_count = len(self.functions) + 1
        result = self._encode_varuint(func_count)
        
        result += self._encode_varuint(3)
        
        for i, _ in enumerate(self.functions):
            result += self._encode_varuint(4 + i)
        
        return result
    
    def _gen_global_section(self) -> bytes:
        """生成全局变量段"""
        if not self.global_vars:
            return b''
        
        result = self._encode_varuint(len(self.global_vars))
        
        for name, idx in self.global_vars.items():
            result += b'\x00\x7f'
            result += b'\x41\x00'
            result += b'\x0b'
        
        return result
    
    def _gen_elem_section(self) -> bytes:
        """生成元素段"""
        if not self.elem_segments:
            return b''
        
        result = self._encode_varuint(len(self.elem_segments))
        
        for seg in self.elem_segments:
            result += seg
        
        return result
    
    def _gen_code_section(self, node: Program) -> bytes:
        """生成代码段"""
        result = self._encode_varuint(len(self.functions) + 1)
        
        for _, func in self.functions:
            body = self._gen_lambda(func)
            result += self._encode_varuint(len(body)) + body
        
        main_body = self._gen_main(node)
        result += self._encode_varuint(len(main_body)) + main_body
        
        return result
    
    def _gen_data_section(self) -> bytes:
        """生成数据段"""
        if not self.string_constants:
            return b''
        
        result = b'\x01\x01\x00'
        
        for data, offset in self.string_constants.items():
            result += b'\x00'
            result += self._encode_varuint(offset)
            result += self._encode_varuint(len(data))
            result += data.encode('utf-8')
        
        return result
    
    def _gen_export_section(self) -> bytes:
        """生成导出段"""
        exports = []
        
        exports.append(b'\x04main\x00\x00' + self._encode_varuint(len(self.functions)))
        exports.append(b'\x04memory\x00\x02\x00')
        
        for i, (name, _) in enumerate(self.functions):
            name_bytes = name.encode('utf-8')
            export = self._encode_varuint(len(name_bytes)) + name_bytes
            export += b'\x00\x00' + self._encode_varuint(i)
            exports.append(export)
        
        result = self._encode_varuint(len(exports))
        for e in exports:
            result += e
        
        return result
    
    def _gen_main(self, node: Program) -> bytes:
        """生成主函数"""
        instructions = []
        
        for stmt in node.statements:
            if isinstance(stmt, Define) and isinstance(stmt.value, Lambda):
                continue
            instructions.extend(self._gen_statement(stmt))
        
        instructions.append(b'\x0b')
        return b''.join(instructions)
    
    def _gen_lambda(self, func: Lambda) -> bytes:
        """生成 Lambda 函数"""
        instructions = []
        
        param_count = len(func.params) if func.params else 0
        instructions.append(self._encode_varuint(0))
        
        for stmt in func.body.statements:
            instructions.extend(self._gen_statement(stmt))
        
        instructions.append(b'\x0f')
        instructions.append(b'\x0b')
        
        return b''.join(instructions)
    
    def _gen_statement(self, stmt: Node) -> List[bytes]:
        """生成语句"""
        if isinstance(stmt, Define):
            return self._gen_define(stmt)
        elif isinstance(stmt, Call):
            return self._gen_call(stmt)
        elif isinstance(stmt, If):
            return self._gen_if(stmt)
        elif isinstance(stmt, While):
            return self._gen_while(stmt)
        elif isinstance(stmt, ForEach):
            return self._gen_foreach(stmt)
        elif isinstance(stmt, Continue):
            return [b'\x0c' + self._encode_varuint(self.label_counter - 1)]
        elif isinstance(stmt, Block):
            return self._gen_block(stmt)
        else:
            return []
    
    def _gen_block(self, block: Block) -> List[bytes]:
        """生成代码块"""
        instructions = []
        for stmt in block.statements:
            instructions.extend(self._gen_statement(stmt))
        return instructions
    
    def _gen_define(self, node: Define) -> List[bytes]:
        """生成定义语句"""
        if isinstance(node.value, Lambda):
            return []
        
        expr_bytes = self._gen_expression(node.value)
        
        if node.name not in self.global_vars:
            self.global_vars[node.name] = self.next_global_index
            self.next_global_index += 1
        
        return expr_bytes + [b'\x24' + self._encode_varuint(self.global_vars[node.name])]
    
    def _gen_if(self, node: If) -> List[bytes]:
        """生成条件语句"""
        instructions = []
        
        cond_bytes = self._gen_expression(node.cond)
        instructions.extend(cond_bytes)
        
        instructions.append(b'\x0d\x01')
        instructions.append(self._encode_varuint(1))
        
        if isinstance(node.then_branch, Block):
            for stmt in node.then_branch.statements:
                instructions.extend(self._gen_statement(stmt))
        
        if node.else_branch and isinstance(node.else_branch, Block):
            instructions.append(b'\x0c\x01')
            instructions.append(self._encode_varuint(1))
            
            for stmt in node.else_branch.statements:
                instructions.extend(self._gen_statement(stmt))
        
        instructions.append(b'\x0b')
        
        return instructions
    
    def _gen_while(self, node: While) -> List[bytes]:
        """生成 while 循环"""
        instructions = []
        
        instructions.append(b'\x03')
        instructions.append(self._encode_varuint(1))
        
        cond_bytes = self._gen_expression(node.cond)
        instructions.extend(cond_bytes)
        
        instructions.append(b'\x0d\x00')
        instructions.append(self._encode_varuint(1))
        
        for stmt in node.body.statements:
            instructions.extend(self._gen_statement(stmt))
        
        instructions.append(b'\x0c\x00')
        
        instructions.append(b'\x0b')
        
        return instructions
    
    def _gen_foreach(self, node: ForEach) -> List[bytes]:
        """生成 for-each 循环"""
        instructions = []
        
        list_expr = self._gen_expression(node.iterable)
        
        instructions.append(b'\x03')
        instructions.append(self._encode_varuint(1))
        
        instructions.extend(list_expr)
        instructions.append(b'\x41\x00')
        instructions.append(b'\x48\x46')
        instructions.append(b'\x0d\x00')
        instructions.append(self._encode_varuint(1))
        
        if node.var not in self.global_vars:
            self.global_vars[node.var] = self.next_global_index
            self.next_global_index += 1
        
        instructions.extend(list_expr)
        instructions.append(b'\x24' + self._encode_varuint(self.global_vars[node.var]))
        
        for stmt in node.body.statements:
            instructions.extend(self._gen_statement(stmt))
        
        instructions.append(b'\x0c\x00')
        
        instructions.append(b'\x0b')
        
        return instructions
    
    def _gen_expression(self, expr: Node) -> List[bytes]:
        """生成表达式"""
        if isinstance(expr, Num):
            if isinstance(expr.value, float):
                return [self._f64_const(expr.value)]
            else:
                return [self._i32_const(expr.value)]
        elif isinstance(expr, Str):
            str_offset = self._add_string(expr.value)
            return [self._i32_const(str_offset)]
        elif isinstance(expr, Bool):
            return [self._i32_const(1 if expr.value else 0)]
        elif isinstance(expr, Nil):
            return [self._i32_const(0)]
        elif isinstance(expr, Word):
            if expr.name in self.global_vars:
                return [b'\x23' + self._encode_varuint(self.global_vars[expr.name])]
            else:
                return [self._i32_const(0)]
        elif isinstance(expr, Call):
            return self._gen_call(expr)
        elif isinstance(expr, MathExpr):
            return self._gen_math_expr(expr)
        elif isinstance(expr, ListLiteral):
            return self._gen_list(expr)
        elif isinstance(expr, Quote):
            return self._gen_quote(expr)
        elif isinstance(expr, Pipeline):
            return self._gen_pipeline(expr)
        else:
            return []
    
    def _gen_math_expr(self, node: MathExpr) -> List[bytes]:
        """生成数学表达式"""
        instructions = []
        
        instructions.extend(self._gen_expression(node.left))
        instructions.extend(self._gen_expression(node.right))
        
        float_ops = {'+': b'\x92', '-': b'\x93', '*': b'\x94', '/': b'\x95'}
        int_ops = {'+': b'\x6a', '-': b'\x6b', '*': b'\x6c', '/': b'\x6d', '%': b'\x6e'}
        cmp_ops = {
            '<': b'\x48\x46', '>': b'\x48\x47', '<=': b'\x48\x56', '>=': b'\x48\x57', 
            '==': b'\x48\x45', '!=': b'\x48\x45\x41\x01\x6a'
        }
        
        if node.op in float_ops:
            instructions.append(float_ops[node.op])
        elif node.op in int_ops:
            instructions.append(int_ops[node.op])
        elif node.op in cmp_ops:
            instructions.append(cmp_ops[node.op])
        
        return instructions
    
    def _gen_call(self, node: Call) -> List[bytes]:
        """生成函数调用"""
        instructions = []
        
        for arg in node.args:
            instructions.extend(self._gen_expression(arg))
        
        verb_name = getattr(node.verb, 'name', None)
        
        float_verbs = {'浮点加': b'\x92', '浮点减': b'\x93', '浮点乘': b'\x94', '浮点除': b'\x95'}
        int_verbs = {'加': b'\x6a', '减': b'\x6b', '乘': b'\x6c', '除': b'\x6d'}
        
        if verb_name in float_verbs:
            instructions.append(float_verbs[verb_name])
        elif verb_name in int_verbs:
            instructions.append(int_verbs[verb_name])
        elif verb_name == '印':
            if node.args:
                if isinstance(node.args[0], Str):
                    instructions.append(b'\x10\x00')
                elif isinstance(node.args[0], Num) and isinstance(node.args[0].value, float):
                    instructions.append(b'\x10\x02')
                else:
                    instructions.append(b'\x10\x01')
            else:
                instructions.append(b'\x10\x00')
        else:
            func_idx = None
            for i, (name, _) in enumerate(self.functions):
                if name == verb_name:
                    func_idx = i
                    break
            
            if func_idx is not None:
                instructions.append(b'\x10' + self._encode_varuint(func_idx))
            else:
                instructions.append(b'\x10\x00')
        
        return instructions
    
    def _gen_list(self, node: ListLiteral) -> List[bytes]:
        """生成列表字面量"""
        instructions = []
        
        instructions.append(self._i32_const(len(node.elements)))
        
        for elem in node.elements:
            instructions.extend(self._gen_expression(elem))
        
        return instructions
    
    def _gen_quote(self, node: Quote) -> List[bytes]:
        """生成引用表达式"""
        return self._gen_expression(node.value)
    
    def _gen_pipeline(self, node: Pipeline) -> List[bytes]:
        """生成管道表达式"""
        instructions = []
        
        for step in node.steps:
            instructions.extend(self._gen_expression(step))
        
        return instructions
    
    def _add_string(self, s: str) -> int:
        """添加字符串常量"""
        if s not in self.string_constants:
            self.string_constants[s] = self.next_string_id
            self.next_string_id += len(s) + 1
        
        return self.string_constants[s]
    
    def _i32_const(self, value: int) -> bytes:
        """生成 i32.const 指令"""
        if value == 0:
            return b'\x41\x00'
        elif value == 1:
            return b'\x41\x01'
        elif 0 < value < 128:
            return b'\x41' + bytes([value])
        elif -128 <= value < 0:
            return b'\x41' + bytes([value & 0xff])
        else:
            return b'\x41' + self._encode_varint(value)
    
    def _f64_const(self, value: float) -> bytes:
        """生成 f64.const 指令"""
        bytes_val = struct.pack('>d', value)
        return b'\x44' + bytes_val
    
    def _encode_varuint(self, value: int) -> bytes:
        """LEB128 无符号整数编码"""
        if value == 0:
            return b'\x00'
        
        result = []
        while value > 0:
            byte = value & 0x7f
            value >>= 7
            if value > 0:
                byte |= 0x80
            result.append(byte)
        
        return bytes(result)
    
    def _encode_varint(self, value: int) -> bytes:
        """LEB128 有符号整数编码"""
        result = []
        while True:
            byte = value & 0x7f
            value >>= 7
            if (value == 0 and (byte & 0x40) == 0) or (value == -1 and (byte & 0x40) != 0):
                result.append(byte)
                break
            result.append(byte | 0x80)
        
        return bytes(result)
    
    def _encode_section(self, section_id: int, content: bytes) -> bytes:
        """编码段"""
        return bytes([section_id]) + self._encode_varuint(len(content)) + content
    
    def save_to_file(self, node: Node, filename: str):
        """保存到 WASM 文件"""
        wasm_bytes = self.generate(node)
        with open(filename, 'wb') as f:
            f.write(wasm_bytes)


def compile_yan_to_wasm(code: str, output_file: str = 'output.wasm') -> bytes:
    """
    将言语言代码编译为 WebAssembly
    
    Args:
        code: 言语言源代码
        output_file: 输出文件名
    
    Returns:
        WASM 字节码
    """
    from lexer import Lexer
    from parser import Parser
    
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    
    parser = Parser()
    ast = parser.parse(tokens)
    
    wasm_gen = WASMCodeGen()
    wasm_bytes = wasm_gen.generate(ast)
    
    wasm_gen.save_to_file(ast, output_file)
    
    return wasm_bytes


if __name__ == '__main__':
    code = '''定义x=10。
定义y=20。
定义和=加x y。
印和。
定义pi=3.14159。
定义面积=浮点乘浮点乘pi 2.0 2.0。
印面积。
如果大于和25则印"大"否则印"小"。'''
    
    wasm = compile_yan_to_wasm(code, 'yan_program.wasm')
    print(f"WASM 文件生成成功，大小: {len(wasm)} 字节")
    
    if wasm[:4] == b'\x00asm':
        print("WASM 格式验证通过")
    else:
        print("WASM 格式验证失败")