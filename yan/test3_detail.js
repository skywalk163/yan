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

const wasm3 = Buffer.concat([header, typeSec, importSec, funcSec]);

console.log('Test 3 (Type + Import + Function):');
console.log('Total size:', wasm3.length);
console.log('Hex:', wasm3.toString('hex'));
console.log();

// Parse sections
let pos = 8;
while (pos < wasm3.length) {
    const id = wasm3[pos];
    pos++;
    const size = wasm3[pos];
    pos++;
    console.log(`Section ID ${id}: size=${size}, content at ${pos}`);
    console.log(`  Content: ${wasm3.slice(pos, pos + size).toString('hex')}`);
    pos += size;
}

console.log();
console.log('Validation:', WebAssembly.validate(wasm3) ? 'Valid' : 'Invalid');
if (!WebAssembly.validate(wasm3)) {
    WebAssembly.compile(wasm3).catch(e => console.log('Error:', e.message));
}