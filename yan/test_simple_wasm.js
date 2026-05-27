// Test 1: Just header + Type + Memory (no Function)
const wasm1 = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d, // magic
    0x01, 0x00, 0x00, 0x00, // version
    // Type section
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00,
    // Memory section
    0x05, 0x02, 0x00, 0x01,
]);

console.log('Test 1 (Type + Memory):');
console.log('  Length:', wasm1.length);
console.log('  Valid:', WebAssembly.validate(wasm1) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm1)) {
    WebAssembly.compile(wasm1).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}

// Test 2: Add Function section
const wasm2 = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d,
    0x01, 0x00, 0x00, 0x00,
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00, // Type
    0x03, 0x02, 0x01, 0x00, // Function: 1 func, type 0
    0x05, 0x02, 0x00, 0x01, // Memory
]);

console.log('\\nTest 2 (Type + Function + Memory):');
console.log('  Length:', wasm2.length);
console.log('  Valid:', WebAssembly.validate(wasm2) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm2)) {
    WebAssembly.compile(wasm2).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}

// Test 3: Add Export section
const wasm3 = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d,
    0x01, 0x00, 0x00, 0x00,
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00, // Type
    0x03, 0x02, 0x01, 0x00, // Function
    0x05, 0x02, 0x00, 0x01, // Memory
    0x07, 0x08, 0x01, 0x04, 0x6d, 0x61, 0x69, 0x6e, 0x00, 0x00, // Export
]);

console.log('\\nTest 3 (+ Export):');
console.log('  Length:', wasm3.length);
console.log('  Valid:', WebAssembly.validate(wasm3) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm3)) {
    WebAssembly.compile(wasm3).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}

// Test 4: Add Code section
const wasm4 = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d,
    0x01, 0x00, 0x00, 0x00,
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00, // Type
    0x03, 0x02, 0x01, 0x00, // Function
    0x05, 0x02, 0x00, 0x01, // Memory
    0x07, 0x08, 0x01, 0x04, 0x6d, 0x61, 0x69, 0x6e, 0x00, 0x00, // Export
    0x0a, 0x04, 0x01, 0x02, 0x00, 0x0b, // Code
]);

console.log('\\nTest 4 (+ Code):');
console.log('  Length:', wasm4.length);
console.log('  Valid:', WebAssembly.validate(wasm4) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm4)) {
    WebAssembly.compile(wasm4).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}