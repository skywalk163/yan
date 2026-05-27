# 测试不同的 Data section flags

data = open('num_test.wasm', 'rb').read()

# 找到 Code section 的结束位置
pos = 8
while pos < len(data):
    section_id = data[pos]
    if section_id == 10:  # Code section
        p = pos + 1
        size = 0
        shift = 0
        while True:
            b = data[p]
            size |= (b & 0x7f) << shift
            p += 1
            if not (b & 0x80):
                break
            shift += 7
        code_end = p + size
        break
    p = pos + 1
    size = 0
    shift = 0
    while True:
        b = data[p]
        size |= (b & 0x7f) << shift
        p += 1
        if not (b & 0x80):
            break
        shift += 7
    pos = p + size

# 测试不同的 flags
for flags in [0, 1, 2]:
    print(f'=== Testing flags = {flags} ===')
    
    if flags == 0:
        # Passive segment (no memory index, no offset expr)
        data_content = bytes([
            0x01,  # segment count = 1
            0x00,  # flags = 0 (passive)
            0x06,  # data length = 6
            0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x00  # "Hello\0"
        ])
    elif flags == 1:
        # Active segment with implicit memory index 0
        data_content = bytes([
            0x01,  # segment count = 1
            0x01,  # flags = 1 (active, memory 0)
            0x41, 0x00,  # i32.const 0
            0x0b,  # end
            0x06,  # data length = 6
            0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x00  # "Hello\0"
        ])
    elif flags == 2:
        # Active segment with explicit memory index
        data_content = bytes([
            0x01,  # segment count = 1
            0x02,  # flags = 2 (active, explicit memory index)
            0x00,  # memory index = 0
            0x41, 0x00,  # i32.const 0
            0x0b,  # end
            0x06,  # data length = 6
            0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x00  # "Hello\0"
        ])
    
    data_section = b'\x0b' + bytes([len(data_content)]) + data_content
    
    # 在 Code section 之后添加 Data section
    new_wasm = data[:code_end] + data_section
    
    filename = f'test_flags_{flags}.wasm'
    with open(filename, 'wb') as f:
        f.write(new_wasm)
    
    print(f'Generated {len(new_wasm)} bytes')
    
    # 测试
    import subprocess
    result = subprocess.run(['node', '-e', f'''
const fs = require('fs');
const wasm = fs.readFileSync('{filename}');

const importObject = {{
  env: {{
    print: function(ptr) {{
      const memory = new Uint8Array(this.memory.buffer);
      let str = '';
      let i = 0;
      while (memory[ptr + i] !== 0 && i < 100) {{
        str += String.fromCharCode(memory[ptr + i]);
        i++;
      }}
      console.log('Printed:', str);
    }},
    print_num: function(n) {{ console.log('Number:', n); }},
    print_float: function(f) {{ console.log('Float:', f); }}
  }}
}};

WebAssembly.instantiate(wasm, importObject).then(result => {{
  console.log('WASM loaded successfully');
  result.instance.exports.main();
}}).catch(e => {{
  console.error('Error:', e.message);
}});
'''], capture_output=True, text=True, cwd='g:\\dumategithub\\newlisp\\yan')
    
    print(f'STDOUT: {result.stdout.strip()}')
    print(f'STDERR: {result.stderr.strip()}')
    print()