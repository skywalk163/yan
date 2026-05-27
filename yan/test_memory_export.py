import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

code = '印"Hello"。'
lexer = Lexer()
tokens = lexer.tokenize(code)
parser = Parser()
ast = parser.parse(tokens)
codegen = WASMCodeGen()
wasm = codegen.generate(ast)

# 检查导出的内容
print('Exports:', codegen._gen_exports().hex())

# 测试
print()
print('=== Testing with proper memory import ===')
import subprocess
result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('str_only.wasm');

const importObject = {
  env: {
    print: function(ptr) {
      const memory = new Uint8Array(wasm.instance.exports.memory.buffer);
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
  wasm.instance = result.instance;
  result.instance.exports.main();
}).catch(e => {
  console.error('Error:', e.message);
});
'''], capture_output=True, text=True, cwd='g:\\dumategithub\\newlisp\\yan')

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('Return code:', result.returncode)