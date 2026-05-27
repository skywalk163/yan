import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 修改代码生成器，不生成 Data section
class NoDataWASMCodeGen(WASMCodeGen):
    def _gen_data(self):
        # 返回空的 Data section
        return b'\x00'  # 0 segments

# 测试：只有字符串打印，但不生成 Data section
print('=== Test: Print string without Data section ===')
code = '印"Hello"。'
lexer = Lexer()
tokens = lexer.tokenize(code)
parser = Parser()
ast = parser.parse(tokens)

codegen = NoDataWASMCodeGen()
wasm = codegen.generate(ast)
print(f'Generated {len(wasm)} bytes')

with open('no_data.wasm', 'wb') as f:
    f.write(wasm)

# 测试这个 WASM（应该会运行，但打印的是垃圾数据）
print()
print('=== Testing no_data.wasm ===')
import subprocess
result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('no_data.wasm');

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