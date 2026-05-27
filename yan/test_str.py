import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 测试3: 只有字符串打印（不使用变量）
print('=== Test 3: Print string only ===')
code = '印"Hello"。'
lexer = Lexer()
tokens = lexer.tokenize(code)
print('Tokens:', tokens)
parser = Parser()
ast = parser.parse(tokens)
print('AST:', ast)
codegen = WASMCodeGen()
wasm = codegen.generate(ast)
print(f'Generated {len(wasm)} bytes')

with open('str_only.wasm', 'wb') as f:
    f.write(wasm)

# 测试4: 测试这个 WASM 是否能运行
print()
print('=== Testing str_only.wasm ===')
import subprocess
result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('str_only.wasm');

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