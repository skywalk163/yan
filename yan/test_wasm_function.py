#!/usr/bin/env python3
"""
测试包含函数定义的 WASM 生成
"""

import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

def test_wasm_with_function():
    """测试包含函数定义的代码"""
    print("🔧 测试包含函数定义的 WASM...")
    
    # 包含函数定义的代码
    code = '''定 问候 = 函 名
  连 "你好，" 名 "！"。

印 问候 "世界"。'''
    
    try:
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        print("✅ Lexer 完成")
        
        parser = Parser()
        ast = parser.parse(tokens)
        print("✅ Parser 完成")
        
        codegen = WASMCodeGen()
        wasm_bytes = codegen.generate(ast)
        print(f"✅ Codegen 完成，WASM 大小: {len(wasm_bytes)} bytes")
        
        # 验证 WASM
        if wasm_bytes[:4] != b'\x00asm':
            print("❌ WASM 魔法字节错误")
            return False
        print("✅ WASM 魔法字节正确")
        
        # 使用 Node.js 测试
        import subprocess
        import tempfile
        import os
        
        test_js = '''
const fs = require('fs');
const wasmBytes = fs.readFileSync('test.wasm');

const memory = new WebAssembly.Memory({ initial: 1 });

const importObject = {
    env: {
        memory: memory,
        print: function(ptr) {
            const view = new Uint8Array(memory.buffer);
            let str = '';
            let i = 0;
            while (view[ptr + i] !== 0 && i < 1000) {
                str += String.fromCharCode(view[ptr + i]);
                i++;
            }
            console.log('print:', str);
        },
        print_num: function(n) { console.log('print_num:', n); },
        print_float: function(f) { console.log('print_float:', f); }
    }
};

WebAssembly.instantiate(wasmBytes, importObject).then(result => {
    if (result.instance.exports.main) {
        result.instance.exports.main();
    }
    console.log('\\n✅ WASM 执行完成');
}).catch(err => {
    console.error('❌ WASM 执行错误:', err);
    process.exit(1);
});
'''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            wasm_path = os.path.join(tmpdir, 'test.wasm')
            js_path = os.path.join(tmpdir, 'test.js')
            
            with open(wasm_path, 'wb') as f:
                f.write(wasm_bytes)
            
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(test_js)
            
            result = subprocess.run(['node', js_path], capture_output=True, text=False, cwd=tmpdir)
            
            print(f"Node.js 输出:")
            if result.stdout:
                try:
                    print(result.stdout.decode('utf-8'))
                except:
                    print(result.stdout.decode('gbk', errors='replace'))
            
            if result.stderr:
                print(f"Node.js 错误:")
                try:
                    print(result.stderr.decode('utf-8'))
                except:
                    print(result.stderr.decode('gbk', errors='replace'))
            
            if result.returncode == 0:
                print("✅ WASM 执行成功！")
                return True
            else:
                print("❌ WASM 执行失败")
                return False
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("    测试包含函数定义的 WASM")
    print("=" * 60)
    
    success = test_wasm_with_function()
    
    if success:
        print("\n🎉 测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)