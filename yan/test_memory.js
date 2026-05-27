// Minimal WASM with Memory
const wasmMem = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,  // header
    0x05, 0x02, 0x01, 0x01,  // Memory: 1 page
]);

console.log('Memory-only WASM:', wasmMem.length);
console.log('Valid:', WebAssembly.validate(wasmMem) ? 'Valid' : 'Invalid');
WebAssembly.compile(wasmMem).catch(e => console.log('Error:', e.message));

// With Type section
const wasmMemType = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,  // header
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00,  // Type: () -> ()
    0x05, 0x02, 0x01, 0x01,  // Memory: 1 page
]);

console.log('\\nMemory + Type:', wasmMemType.length);
console.log('Valid:', WebAssembly.validate(wasmMemType) ? 'Valid' : 'Invalid');
WebAssembly.compile(wasmMemType).catch(e => console.log('Error:', e.message));