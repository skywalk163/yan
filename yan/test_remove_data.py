import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

# 修改代码生成器，强制不生成 Data section（即使有字符串常量）
class ForceNoDataWASMCodeGen(WASMCodeGen):
    def generate(self, ast):
        # 调用父类方法
        wasm = super().generate(ast)
        
        # 移除 Data section
        # Data section 的 section id 是 11 (0x0b)
        # 找到 Data section 并移除它
        pos = 8  # 跳过魔数和版本
        result = wasm[:8]
        
        while pos < len(wasm):
            section_id = wasm[pos]
            
            # 解析大小
            p = pos + 1
            size_bytes = []
            while True:
                b = wasm[p]
                size_bytes.append(b)
                p += 1
                if not (b & 0x80):
                    break
            
            section_size = 0
            for i, b in enumerate(size_bytes):
                section_size |= (b & 0x7f) << (7 * i)
            
            section_length = 1 + len(size_bytes) + section_size  # id + size + content
            
            # 如果是 Data section，跳过它
            if section_id != 11:
                result += wasm[pos:pos+section_length]
            
            pos += section_length
        
        return result

# 测试：只有字符串打印，但移除 Data section
print('=== Test: Print string with Data section removed ===')
code = '印"Hello"。'
lexer = Lexer()
tokens = lexer.tokenize(code)
parser = Parser()
ast = parser.parse(tokens)

codegen = ForceNoDataWASMCodeGen()
wasm = codegen.generate(ast)
print(f'Generated {len(wasm)} bytes')

with open('no_data_str.wasm', 'wb') as f:
    f.write(wasm)

# 测试这个 WASM（应该会加载，但打印的是垃圾数据）
print()
print('=== Testing no_data_str.wasm ===')
import subprocess
result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('no_data_str.wasm');

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