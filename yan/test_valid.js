// Minimal valid WASM with all required sections
const wasm = new Uint8Array([
    0x00, 0x61, 0x73, 0x6d,  // magic
    0x01, 0x00, 0x00, 0x00,  // version
    // Type section
    0x01,  // section ID
    0x04,  // section size
    0x01,  // type count
    0x60,  // func type
    0x00,  // param count
    0x00,  // return type count
    // Function section
    0x03,  // section ID
    0x02,  // section size (2 bytes: count + type_index)
    0x01,  // function count
    0x00,  // function 0: type index 0
    // Export section
    0x07,  // section ID
    0x08,  // section size
    0x01,  // export count
    0x04,  // name length (4)
    0x6d, 0x61, 0x69, 0x6e,  // "main"
    0x00,  // kind: function
    0x00,  // function index
    // Code section
    0x0a,  // section ID
    0x04,  // section size (4 bytes)
    0x01,  // body count
    0x02,  // body 0 size (2 bytes: 1 local decl + 1 instruction + end)
    0x00,  // local count = 0
    0x0b,  // end
]);

console.log('WASM length:', wasm.length);
WebAssembly.compile(wasm).then(m => {
    console.log('Compile OK');
    const inst = new WebAssembly.Instance(m);
    console.log('Instance OK');
    console.log('Exports:', Object.keys(inst.exports));
}).catch(e => console.error('Error:', e.message));