#!/usr/bin/env python3
"""
独立测试 WASM 生成和执行，不依赖 Playground 服务器
"""

import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

def test_wasm_generation():
    """测试 WASM 生成"""
    print("🔧 测试 WASM 生成...")
    
    # 测试代码
    code = '''印 "Hello, WASM!"。
定 x = 42。
印数 x。'''
    
    try:
        # 编译流程
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        print("✅ Lexer 完成")
        
        parser = Parser()
        ast = parser.parse(tokens)
        print("✅ Parser 完成")
        
        codegen = WASMCodeGen()
        wasm_bytes = codegen.generate(ast)
        print(f"✅ Codegen 完成，WASM 大小: {len(wasm_bytes)} bytes")
        
        # 验证 WASM 结构
        if wasm_bytes[:4] != b'\x00asm':
            print("❌ WASM 魔法字节错误")
            return False
        print("✅ WASM 魔法字节正确")
        
        return wasm_bytes
        
    except Exception as e:
        print(f"❌ 编译错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_wasm_execution_in_node():
    """使用 Node.js 测试 WASM 执行"""
    print("\n🔧 测试 WASM 在 Node.js 中执行...")
    
    import subprocess
    import tempfile
    import os
    
    # 创建测试 JS 文件
    test_js = '''
const fs = require('fs');

// 读取 WASM 文件
const wasmBytes = fs.readFileSync('test.wasm');

// 创建内存
const memory = new WebAssembly.Memory({ initial: 1 });

// 导入对象
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
        print_num: function(n) {
            console.log('print_num:', n);
        },
        print_float: function(f) {
            console.log('print_float:', f);
        }
    }
};

// 实例化并执行
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
    
    # 获取 WASM 字节码
    wasm_bytes = test_wasm_generation()
    if wasm_bytes is None:
        return False
    
    # 写入临时文件
    with tempfile.TemporaryDirectory() as tmpdir:
        wasm_path = os.path.join(tmpdir, 'test.wasm')
        js_path = os.path.join(tmpdir, 'test.js')
        
        with open(wasm_path, 'wb') as f:
            f.write(wasm_bytes)
        
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(test_js)
        
        # 运行 Node.js
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
            print("✅ WASM 在 Node.js 中执行成功！")
            # 检查输出是否正确
            stdout_str = result.stdout.decode('utf-8') if result.stdout else ""
            if "Hello, WASM!" in stdout_str and "42" in stdout_str:
                print("✅ 输出内容正确！")
                return True
            else:
                print("❌ 输出内容不正确")
                return False
        else:
            print("❌ WASM 在 Node.js 中执行失败")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("    独立 WASM 测试")
    print("=" * 60)
    
    success = test_wasm_execution_in_node()
    
    if success:
        print("\n🎉 所有 WASM 测试通过！")
        print("现在可以启动 Playground 进行最终测试")
        sys.exit(0)
    else:
        print("\n❌ WASM 测试失败！")
        sys.exit(1)