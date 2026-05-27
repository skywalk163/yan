// Minimal valid WASM with correct Memory encoding
const wasm = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d, // magic
    0x01, 0x00, 0x00, 0x00, // version
    // Type section
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00, // Type: () -> ()
    // Function section
    0x03, 0x02, 0x01, 0x00, // Function: 1 func, type 0
    // Memory section: 1 page, no maximum
    // flags=0 (00), initial=1 (01)
    0x05, 0x02, 0x00, 0x01,
    // Export section
    0x07, 0x08, 0x01, 0x04, 0x6d, 0x61, 0x69, 0x6e, 0x00, 0x00, // Export: "main", func, 0
    // Code section
    0x0a, 0x04, 0x01, 0x02, 0x00, 0x0b, // Code: 1 body, size 2, 0 locals, end
]);

console.log('wasm length:', wasm.length);
console.log('Hex:', wasm.toString('hex'));
console.log();
console.log('Valid:', WebAssembly.validate(wasm) ? 'Valid' : 'Invalid');
WebAssembly.compile(wasm).then(m => {
    console.log('Compile OK');
    const inst = new WebAssembly.Instance(m);
    console.log('Instance OK');
    console.log('Exports:', Object.keys(inst.exports));
}).catch(e => console.log('Error:', e.message));