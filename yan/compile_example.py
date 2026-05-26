#!/usr/bin/env python3
"""
编译言语言示例到 WebAssembly
"""

from codegen_wasm import compile_yan_to_wasm
import os

def compile_example():
    """编译汉诺塔示例"""
    example_dir = 'examples'
    output_dir = 'wasm_output'
    
    os.makedirs(output_dir, exist_ok=True)
    
    example_files = [
        ('tower_of_hanoi.yan', 'tower_of_hanoi.wasm')
    ]
    
    for input_file, output_file in example_files:
        input_path = os.path.join(example_dir, input_file)
        output_path = os.path.join(output_dir, output_file)
        
        print(f"编译 {input_path} -> {output_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        wasm_bytes = compile_yan_to_wasm(code, output_path)
        print(f"  大小: {len(wasm_bytes)} 字节")
        print(f"  格式验证: {'通过' if wasm_bytes[:4] == b'\\x00asm' else '失败'}")
        print()
    
    print("编译完成！")

if __name__ == '__main__':
    compile_example()