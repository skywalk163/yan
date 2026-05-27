#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 测试代码
code = '''印 "Hello, WASM!"。
定 x = 42。
印数 x。'''

print("Detailed instruction stack analysis...")
print(f"Code:\n{code}")
print()

try:
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    
    parser = Parser()
    ast = parser.parse(tokens)
    
    codegen = WASMCodeGen()
    
    # 生成代码段
    code_bytes = codegen._gen_code_section(ast)
    
    print("Full Code section (hex):")
    print(code_bytes.hex())
    print()
    
    # 解析并分析栈状态
    offset = 0
    stack_size = 0
    
    # 函数数量
    func_count = code_bytes[offset]
    print(f"Function count: {func_count}")
    offset += 1
    
    for func_idx in range(func_count):
        print(f"\n=== Function {func_idx} ===")
        
        # 函数体大小
        size = 0
        shift = 0
        while offset < len(code_bytes):
            b = code_bytes[offset]
            size |= (b & 0x7f) << shift
            offset += 1
            if not (b & 0x80):
                break
            shift += 7
        print(f"Body size: {size} bytes")
        
        # 函数体
        body = code_bytes[offset:offset+size]
        offset += size
        
        # 反汇编并追踪栈
        body_offset = 0
        stack_size = 0
        
        while body_offset < len(body):
            byte = body[body_offset]
            print(f"0x{body_offset:04x}: 0x{byte:02x} ", end='')
            
            if byte == 0x41:  # i32.const
                body_offset += 1
                val = 0
                shift = 0
                while body_offset < len(body):
                    b = body[body_offset]
                    val |= (b & 0x7f) << shift
                    body_offset += 1
                    if not (b & 0x80):
                        break
                    shift += 7
                print(f"i32.const {val}")
                stack_size += 1
                
            elif byte == 0x10:  # call
                body_offset += 1
                idx = 0
                shift = 0
                while body_offset < len(body):
                    b = body[body_offset]
                    idx |= (b & 0x7f) << shift
                    body_offset += 1
                    if not (b & 0x80):
                        break
                    shift += 7
                print(f"call {idx}")
                # call 消耗参数（根据函数类型）
                # 我们的导入函数都接收1个参数
                stack_size -= 1
                
            elif byte == 0x24:  # global.set
                body_offset += 1
                idx = 0
                shift = 0
                while body_offset < len(body):
                    b = body[body_offset]
                    idx |= (b & 0x7f) << shift
                    body_offset += 1
                    if not (b & 0x80):
                        break
                    shift += 7
                print(f"global.set {idx}")
                stack_size -= 1
                
            elif byte == 0x23:  # global.get
                body_offset += 1
                idx = 0
                shift = 0
                while body_offset < len(body):
                    b = body[body_offset]
                    idx |= (b & 0x7f) << shift
                    body_offset += 1
                    if not (b & 0x80):
                        break
                    shift += 7
                print(f"global.get {idx}")
                stack_size += 1
                
            elif byte == 0x0b:  # end
                print(f"end (stack size: {stack_size})")
                body_offset += 1
                
            elif byte == 0x00:  # local count 0
                print("local 0")
                body_offset += 1
                
            else:
                print(f"unknown (stack size before: {stack_size})")
                body_offset += 1
            
            # 显示栈状态
            if byte not in [0x0b, 0x00]:
                print(f"      Stack: {stack_size}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()