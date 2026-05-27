import sys
sys.path.insert(0, '.')

from lexer import Lexer
from parser import Parser
from codegen_wasm import WASMCodeGen

print('=== Test 1: Simple string ===')
code = '印"Hello"。'
lexer = Lexer()
tokens = lexer.tokenize(code)
parser = Parser()
ast = parser.parse(tokens)
codegen = WASMCodeGen()
wasm = codegen.generate(ast)

with open('test_string.wasm', 'wb') as f:
    f.write(wasm)

import subprocess
result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('test_string.wasm');

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
  wasm.instance = result.instance;
  result.instance.exports.main();
}).catch(e => {
  console.error('Error:', e.message);
});
'''], capture_output=True, text=True, cwd='g:\\dumategithub\\newlisp\\yan')

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)

print()
print('=== Test 2: Number ===')
code = '令 a 为 42。印数 a。'
lexer = Lexer()
tokens = lexer.tokenize(code)
parser = Parser()
ast = parser.parse(tokens)
codegen = WASMCodeGen()
wasm = codegen.generate(ast)

with open('test_number.wasm', 'wb') as f:
    f.write(wasm)

result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('test_number.wasm');

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
  wasm.instance = result.instance;
  result.instance.exports.main();
}).catch(e => {
  console.error('Error:', e.message);
});
'''], capture_output=True, text=True, cwd='g:\\dumategithub\\newlisp\\yan')

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)

print()
print('=== Test 3: Multiple strings ===')
code = '印"Hello"。印"World"。'
lexer = Lexer()
tokens = lexer.tokenize(code)
parser = Parser()
ast = parser.parse(tokens)
codegen = WASMCodeGen()
wasm = codegen.generate(ast)

with open('test_multi.wasm', 'wb') as f:
    f.write(wasm)

result = subprocess.run(['node', '-e', '''
const fs = require('fs');
const wasm = fs.readFileSync('test_multi.wasm');

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
  wasm.instance = result.instance;
  result.instance.exports.main();
}).catch(e => {
  console.error('Error:', e.message);
});
'''], capture_output=True, text=True, cwd='g:\\dumategithub\\newlisp\\yan')

print('STDOUT:', result.stdout)
print('STDERR:', result.stderr)