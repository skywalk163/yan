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

const header = Buffer.from([0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00]);
const typeSec = getSection(hanoi, 1);
const importSec = getSection(hanoi, 2);
const funcSec = getSection(hanoi, 3);
const memorySec = getSection(hanoi, 5);
const exportSec = getSection(hanoi, 7);
const codeSec = getSection(hanoi, 10);
const dataSec = getSection(hanoi, 11);

// Build in correct order: Type, Import, Function, Memory, Code, Export, Data
const wasm = Buffer.concat([header, typeSec, importSec, funcSec, memorySec, codeSec, exportSec, dataSec]);

console.log('Full WASM (reordered):');
console.log('Total size:', wasm.length);

// Manual parsing
console.log();
console.log('Sections:');
let pos = 8;
let secNum = 0;
while (pos < wasm.length) {
    secNum++;
    const id = wasm[pos];
    pos++;
    const size = wasm[pos];
    pos++;
    const name = ['???','Type','Import','Function','Table','Memory','Global','Export','Start','Element','Code','Data'][id] || '???';
    console.log(`  ${secNum}. ${name} (ID=${id}): size=${size} at offset ${pos-2}`);
    pos += size;
}

console.log();
console.log('Validation:', WebAssembly.validate(wasm) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm)) {
    WebAssembly.compile(wasm).catch(e => console.log('Compile error:', e.message));
}

// Compare with original
console.log();
console.log('Original hanoi WASM size:', hanoi.length);
console.log('Reordered WASM size:', wasm.length);
console.log('Are they equal?', wasm.equals(hanoi) ? 'YES' : 'NO');

if (!wasm.equals(hanoi)) {
    console.log('First difference at:');
    for (let i = 0; i < Math.min(wasm.length, hanoi.length); i++) {
        if (wasm[i] !== hanoi[i]) {
            console.log(`  offset ${i}: wasm=${wasm[i]}, hanoi=${hanoi[i]}`);
            break;
        }
    }
    if (wasm.length !== hanoi.length) {
        console.log(`  Length difference: wasm=${wasm.length}, hanoi=${hanoi.length}`);
    }
}