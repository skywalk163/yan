import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 修改代码生成器，强制添加一个全局变量
class TestWASMCodeGen(WASMCodeGen):
    def _gen_globals(self):
        # 强制添加一个全局变量，即使没有实际需要
        globals_data = []
        # 添加一个初始值为 0 的可变 i32 全局变量
        global_type = b'\x7f\x01'  # i32, mutable
        init_expr = self._i32_const(0) + b'\x0b'  # i32.const 0 + end
        globals_data.append(global_type + init_expr)
        return self._encode_varuint(len(globals_data)) + b''.join(globals_data)

# 测试：只有字符串打印
print('=== Test: Print string with forced global ===')
code = '印"Hello"。'
lexer = Lexer()
tokens = lexer.tokenize(code)
print('Tokens:', tokens)
parser = Parser()
ast = parser.parse(tokens)
print('AST:', ast)

codegen = TestWASMCodeGen()
wasm = codegen.generate(ast)
print(f'Generated {len(wasm)} bytes')

with open('str_with_global.wasm', 'wb') as f:
    f.write(wasm)

# 测试这个 WASM 是否能运行
print()
print('=== Testing str_with_global.wasm ===')
import subprocess
result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('str_with_global.wasm');

const importObject = {
  env: {
    print: function(ptr) {
      const memory = new Uint8Array(this.memory.buffer);
      let str = '';
      let i = 0;
      while (memory[ptr + i] !== 0 && i < 100) {
        str += String.fromCharCode(memory[ptr + i]);
        i++;
      }
      console.log('Printed:', str);
    },
    print_num: function(n) { console.log('Number:', n); },
    print_float: function(f) { console.log('Float:', f); }
  }
};

WebAssembly.instantiate(wasm, importObject).then(result => {
  console.log('WASM loaded successfully');
  result.instance.exports.main();
}).catch(e => {
  console.error('Error:', e.message);
});
'''], capture_output=True, text=True, cwd='g:\\dumategithub\\newlisp\\yan')

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('Return code:', result.returncode)