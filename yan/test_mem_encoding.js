// Test different memory encodings

// Our current encoding (wrong?)
const mem1 = new Uint8Array([0x05, 0x02, 0x01, 0x01]);
console.log('mem1 (01 01):', mem1.length);
console.log('  Valid:', WebAssembly.validate(mem1) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(mem1)) {
    WebAssembly.compile(mem1).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}

// Correct encoding: flags=0, initial=1 (LEB128)
const mem2 = new Uint8Array([0x05, 0x02, 0x00, 0x01]);
console.log('mem2 (00 01):', mem2.length);
console.log('  Valid:', WebAssembly.validate(mem2) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(mem2)) {
    WebAssembly.compile(mem2).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}

// What about with Type section?
const mem3 = new Uint8Array([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00, 0x01, 0x04, 0x01, 0x60, 0x00, 0x00, 0x05, 0x02, 0x01, 0x01]);
console.log('mem3 with Type (01 01):', mem3.length);
console.log('  Valid:', WebAssembly.validate(mem3) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(mem3)) {
    WebAssembly.compile(mem3).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}

const mem4 = new Uint8Array([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00, 0x01, 0x04, 0x01, 0x60, 0x00, 0x00, 0x05, 0x02, 0x00, 0x01]);
console.log('mem4 with Type (00 01):', mem4.length);
console.log('  Valid:', WebAssembly.validate(mem4) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(mem4)) {
    WebAssembly.compile(mem4).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}