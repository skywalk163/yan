// Test with correct section order: Type, Function, Memory, Export, Code
const wasm = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d,
    0x01, 0x00, 0x00, 0x00,
    // Type
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00,
    // Function
    0x03, 0x02, 0x01, 0x00,
    // Memory
    0x05, 0x02, 0x00, 0x01,
    // Export
    0x07, 0x08, 0x01, 0x04, 0x6d, 0x61, 0x69, 0x6e, 0x00, 0x00,
    // Code
    0x0a, 0x04, 0x01, 0x02, 0x00, 0x0b,
]);

console.log('Correct order:');
console.log('  Length:', wasm.length);
console.log('  Valid:', WebAssembly.validate(wasm) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm)) {
    WebAssembly.compile(wasm).catch(e => console.log('  Error:', e.message.split('\n')[0]));
} else {
    WebAssembly.compile(wasm).then(m => {
        console.log('  Compile OK');
        const inst = new WebAssembly.Instance(m);
        console.log('  Instance OK');
        console.log('  Exports:', Object.keys(inst.exports));
    });
}