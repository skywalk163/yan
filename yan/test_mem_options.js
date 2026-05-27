// Try memory with maximum
const wasm1 = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00, // Type
    0x03, 0x02, 0x01, 0x00, // Function
    // Memory: flags=1 (has max), initial=1, maximum=1
    0x05, 0x03, 0x01, 0x01, 0x01, // Memory: size=3, flags=1, initial=1, max=1
    0x07, 0x08, 0x01, 0x04, 0x6d, 0x61, 0x69, 0x6e, 0x00, 0x00, // Export
    0x0a, 0x04, 0x01, 0x02, 0x00, 0x0b, // Code
]);

console.log('Memory with max (01 01 01):');
console.log('  Valid:', WebAssembly.validate(wasm1) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm1)) {
    WebAssembly.compile(wasm1).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}

// Try just memory without function/export
const wasm2 = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
    0x05, 0x03, 0x01, 0x01, 0x01, // Memory only
]);

console.log('Memory only with max:');
console.log('  Valid:', WebAssembly.validate(wasm2) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm2)) {
    WebAssembly.compile(wasm2).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}

// Try with shared memory flag
const wasm3 = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
    0x05, 0x04, 0x02, 0x01, 0x01, 0x01, // Memory: flags=2 (is_shared), initial=1, max=1
]);

console.log('Memory shared:');
console.log('  Valid:', WebAssembly.validate(wasm3) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm3)) {
    WebAssembly.compile(wasm3).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}

// Try without any limits (just initial)
const wasm4 = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
    0x05, 0x02, 0x00, 0x01, // Memory
]);

console.log('Memory simple (00 01):');
console.log('  Valid:', WebAssembly.validate(wasm4) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm4)) {
    WebAssembly.compile(wasm4).catch(e => console.log('  Error:', e.message.split('\n')[0]));
}