# 创建一个最简单的测试，不调用任何导入函数

# WASM 魔数和版本
wasm = b'\x00asm\x01\x00\x00\x00'

# Type section: 1 种类型（main 函数）
type_content = (
    b'\x01'  # type count
    # Type 0: (func)
    b'\x60\x00\x00'
)
type_section = b'\x01' + bytes([len(type_content)]) + type_content
wasm += type_section

# Function section: 定义 main 函数
function_content = (
    b'\x01'  # function count
    b'\x00'  # type index 0
)
function_section = b'\x03' + bytes([len(function_content)]) + function_content
wasm += function_section

# Memory section: 1 页内存
memory_content = (
    b'\x01'  # memory count
    b'\x00'  # flags
    b'\x01'  # initial pages
)
memory_section = b'\x05' + bytes([len(memory_content)]) + memory_content
wasm += memory_section

# Export section: 导出 main 和 memory
export_content = (
    b'\x02'  # export count
    b'\x04main\x00\x00'  # main function, index 0
    b'\x06memory\x02\x00'  # memory, index 0
)
export_section = b'\x07' + bytes([len(export_content)]) + export_content
wasm += export_section

# Code section: main 函数体（空函数）
code_content = (
    b'\x01'  # function body count
    b'\x02'  # function body size (2 bytes: locals count + end)
    b'\x00'  # locals count
    b'\x0b'  # end
)
code_section = b'\x0a' + bytes([len(code_content)]) + code_content
wasm += code_section

# Data section: 字符串数据
data_content = (
    b'\x01'  # segment count
    b'\x01'  # flags (active, memory 0)
    b'\x41\x00'  # i32.const 0
    b'\x0b'      # end
    b'\x06'      # data length
    b'Hello\x00' # data
)
data_section = b'\x0b' + bytes([len(data_content)]) + data_content
wasm += data_section

print(f'Simple WASM: {len(wasm)} bytes')

with open('simple.wasm', 'wb') as f:
    f.write(wasm)

# 测试
print()
print('=== Testing simple.wasm ===')
import subprocess
result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('simple.wasm');

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
    }
  }
};

WebAssembly.instantiate(wasm, importObject).then(result => {
  console.log('WASM loaded successfully');
  result.instance.exports.main();
  console.log('Main function called');
}).catch(e => {
  console.error('Error:', e.message);
});
'''], capture_output=True, text=True, cwd='g:\\dumategithub\\newlisp\\yan')

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('Return code:', result.returncode)