import struct

# 手动创建一个简单的 WASM 文件
# 结构: Magic + Version + Type section + Import section + Function section + Memory section + Export section + Code section

magic = b'\x00asm'
version = b'\x01\x00\x00\x00'

# Type section: 1 function type (() -> void)
type_section = b'\x01'  # section ID
type_section += b'\x04'  # size = 4
type_section += b'\x01'  # count = 1
type_section += b'\x60'  # func type
type_section += b'\x00'  # param count = 0
type_section += b'\x00'  # result count = 0

# Import section: 1 import (print function)
import_section = b'\x02'  # section ID
import_section += b'\x0d'  # size = 13
import_section += b'\x01'  # count = 1
import_section += b'\x03env'  # module name
import_section += b'\x05print'  # field name
import_section += b'\x00'  # kind = func
import_section += b'\x00'  # type index = 0

# Function section: 1 function (main), type index 0
func_section = b'\x03'  # section ID
func_section += b'\x02'  # size = 2
func_section += b'\x01'  # count = 1
func_section += b'\x00'  # type index = 0

# Memory section: 1 page
memory_section = b'\x05'  # section ID
memory_section += b'\x03'  # size = 3
memory_section += b'\x01'  # count = 1
memory_section += b'\x00'  # flags = 0
memory_section += b'\x01'  # initial = 1

# Export section: export main and memory
export_section = b'\x07'  # section ID
export_section += b'\x11'  # size = 17
export_section += b'\x02'  # count = 2
# export main
export_section += b'\x04main'  # name
export_section += b'\x00'  # kind = func
export_section += b'\x01'  # func index = 1 (imported func is 0)
# export memory
export_section += b'\x06memory'  # name
export_section += b'\x02'  # kind = memory
export_section += b'\x00'  # memory index = 0

# Code section: main function body
code_section = b'\x0a'  # section ID
code_section += b'\x06'  # size = 6
code_section += b'\x01'  # count = 1
code_section += b'\x04'  # body size = 4
code_section += b'\x00'  # local count = 0
code_section += b'\x10\x00'  # call 0 (print)
code_section += b'\x0b'  # end

# Data section: empty
data_section = b'\x0b'  # section ID
data_section += b'\x01'  # size = 1
data_section += b'\x00'  # count = 0

# Combine all sections
wasm = magic + version + type_section + import_section + func_section + memory_section + export_section + code_section + data_section

print(f'Generated WASM: {len(wasm)} bytes')

with open('test_manual.wasm', 'wb') as f:
    f.write(wasm)

print('Saved to test_manual.wasm')