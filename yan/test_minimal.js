// Minimal WASM module with just memory
const wasmMinimal = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d, // magic
    0x01, 0x00, 0x00, 0x00, // version
    0x05, // Memory section ID
    0x02, // Section size
    0x01, // memory count
    0x01, // flags=0, initial=1 page
]);

console.log('Minimal WASM length:', wasmMinimal.length);
WebAssembly.compile(wasmMinimal).then(m => console.log('Minimal: OK')).catch(e => console.error('Minimal Error:', e.message));

// Add Type section
const wasmWithType = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d,
    0x01, 0x00, 0x00, 0x00,
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00, // Type section: 1 type, () -> ()
    0x05, 0x02, 0x01, 0x01,              // Memory section
]);

console.log('With Type WASM length:', wasmWithType.length);
WebAssembly.compile(wasmWithType).then(m => console.log('With Type: OK')).catch(e => console.error('With Type Error:', e.message));

// Add Function section
const wasmWithFunc = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d,
    0x01, 0x00, 0x00, 0x00,
    0x01, 0x04, 0x01, 0x60, 0x00, 0x00, // Type
    0x03, 0x01, 0x00,                    // Function: 1 function, type 0
    0x05, 0x02, 0x01, 0x01,              // Memory
    0x07, 0x07, 0x01, 0x03, 0x6d, 0x61, 0x69, 0x6e, 0x00, 0x00, // Export: 1 export, "main", func, idx 0
    0x0a, 0x04, 0x01, 0x01, 0x0b,        // Code: 1 body, size 1, end
]);

console.log('With Function WASM length:', wasmWithFunc.length);
WebAssembly.compile(wasmWithFunc).then(m => console.log('With Function: OK')).catch(e => console.error('With Function Error:', e.message));