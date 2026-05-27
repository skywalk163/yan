const fs = require('fs');
const hanoi = fs.readFileSync('wasm_output/tower_of_hanoi.wasm');

function getSection(buf, sectionId) {
    let pos = 8;
    while (pos < buf.length) {
        if (buf[pos] === sectionId) {
            const size = buf[pos + 1];
            return buf.slice(pos, pos + 2 + size);
        }
        pos++;
        const size = buf[pos];
        pos += 1 + size;
    }
    return null;
}

// Test 1: Only Type section
const typeSec = getSection(hanoi, 1);
const header = Buffer.from([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00]);
const wasm1 = Buffer.concat([header, typeSec]);
console.log('Test 1 (Type only):', wasm1.length, WebAssembly.validate(wasm1) ? 'Valid' : 'Invalid');

// Test 2: Type + Import
const importSec = getSection(hanoi, 2);
const wasm2 = Buffer.concat([header, typeSec, importSec]);
console.log('Test 2 (Type + Import):', wasm2.length, WebAssembly.validate(wasm2) ? 'Valid' : 'Invalid');

// Test 3: Type + Import + Function
const funcSec = getSection(hanoi, 3);
const wasm3 = Buffer.concat([header, typeSec, importSec, funcSec]);
console.log('Test 3 (Type + Import + Function):', wasm3.length, WebAssembly.validate(wasm3) ? 'Valid' : 'Invalid');

// Test 4: Type + Import + Function + Memory
const memorySec = getSection(hanoi, 5);
const wasm4 = Buffer.concat([header, typeSec, importSec, funcSec, memorySec]);
console.log('Test 4 (Type + Import + Function + Memory):', wasm4.length, WebAssembly.validate(wasm4) ? 'Valid' : 'Invalid');

// Test 5: Type + Import + Function + Memory + Export (no Code)
const exportSec = getSection(hanoi, 7);
const wasm5 = Buffer.concat([header, typeSec, importSec, funcSec, memorySec, exportSec]);
console.log('Test 5 (without Code):', wasm5.length, WebAssembly.validate(wasm5) ? 'Valid' : 'Invalid');

// Test 6: Add Code section
const codeSec = getSection(hanoi, 10);
const wasm6 = Buffer.concat([header, typeSec, importSec, funcSec, memorySec, exportSec, codeSec]);
console.log('Test 6 (full):', wasm6.length, WebAssembly.validate(wasm6) ? 'Valid' : 'Invalid');

if (!WebAssembly.validate(wasm6)) {
    // Try to compile to see the specific error
    WebAssembly.compile(wasm6).catch(e => console.log('Compile error:', e.message));
}

// Test 7: Replace Export with a minimal one
const minimalExport = Buffer.from([0x07, 0x08, 0x01, 0x04, 0x6d, 0x61, 0x69, 0x6e, 0x00, 0x00]);
const wasm7 = Buffer.concat([header, typeSec, importSec, funcSec, memorySec, minimalExport, codeSec]);
console.log('Test 7 (minimal Export):', wasm7.length, WebAssembly.validate(wasm7) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm7)) {
    WebAssembly.compile(wasm7).catch(e => console.log('Compile error:', e.message));
}