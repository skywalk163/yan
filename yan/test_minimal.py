# 创建一个最小的 WASM 文件，只有 Data section

# WASM 魔数和版本
wasm = b'\x00asm\x01\x00\x00\x00'

# Type section: 2 种类型
type_content = (
    b'\x02'  # type count
    # Type 0: (func (param i32))
    b'\x60\x01\x7f\x00'
    # Type 1: (func)
    b'\x60\x00\x00'
)
type_section = b'\x01' + bytes([len(type_content)]) + type_content
wasm += type_section

# Import section: 导入 env.print
import_content = (
    b'\x01'  # import count
    b'\x03env\x05print\x00\x00'  # env.print, function, type 0
)
import_section = b'\x02' + bytes([len(import_content)]) + import_content
wasm += import_section

# Function section: 定义 main 函数
function_content = (
    b'\x01'  # function count
    b'\x01'  # type index 1
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
    b'\x04main\x00\x01'  # main function, index 1
    b'\x06memory\x02\x00'  # memory, index 0
)
export_section = b'\x07' + bytes([len(export_content)]) + export_content
wasm += export_section

# Code section: main 函数体
# 函数体 = locals count (1) + 指令 (5) = 6 bytes
code_content = (
    b'\x01'  # function body count
    b'\x06'  # function body size (6 bytes)
    b'\x00'  # locals count
    b'\x41\x00'  # i32.const 0
    b'\x10\x00'  # call 0
    b'\x0b'      # end
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

print(f'Minimal WASM: {len(wasm)} bytes')

# 打印十六进制
print('Hex dump:')
for i in range(0, len(wasm), 16):
    hex_part = ' '.join([f'{b:02x}' for b in wasm[i:i+16]])
    print(f'{i:04d}: {hex_part}')

with open('minimal.wasm', 'wb') as f:
    f.write(wasm)

# 测试
print()
print('=== Testing minimal.wasm ===')
import subprocess
result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('minimal.wasm');

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
}).catch(e => {
  console.error('Error:', e.message);
});
'''], capture_output=True, text=True, cwd='g:\\dumategithub\\newlisp\\yan')

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)
print('Return code:', result.returncode)