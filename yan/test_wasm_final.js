const fs = require('fs');

const wasmBytes = fs.readFileSync('wasm_output/tower_of_hanoi.wasm');

console.log(`WASM 文件大小: ${wasmBytes.length} 字节`);

const importObject = {
    env: {
        print: (ptr) => console.log(`[字符串@${ptr}]`),
        print_num: (num) => console.log(num),
        print_float: (num) => console.log(num)
    }
};

console.log('\n尝试加载 WASM...\n');

WebAssembly.instantiate(wasmBytes, importObject)
    .then(result => {
        console.log('✓ WASM 加载成功!');
        console.log('导出函数:', Object.keys(result.instance.exports));

        if (result.instance.exports.main) {
            console.log('\n执行 main()...\n');
            result.instance.exports.main();
        } else {
            console.log('没有找到 main 函数');
        }
    })
    .catch(err => {
        console.error('✗ WASM 加载失败:');
        console.error('  错误:', err.message);

        // 解析错误位置
        const match = err.message.match(/@\+(\d+)/);
        if (match) {
            const offset = parseInt(match[1]);
            console.error(`\n  错误位置: offset ${offset}`);
            console.error(`  该位置字节: 0x${wasmBytes[offset].toString(16).padStart(2, '0')} (${wasmBytes[offset]})`);
            if (32 <= wasmBytes[offset] && wasmBytes[offset] < 127) {
                console.error(`  ASCII: "${String.fromCharCode(wasmBytes[offset])}"`);
            }

            // 显示周围字节
            const start = Math.max(0, offset - 5);
            const end = Math.min(wasmBytes.length, offset + 10);
            console.error('\n  周围字节:');
            for (let i = start; i < end; i++) {
                const prefix = i === offset ? ' --> ' : '      ';
                const byte = wasmBytes[i];
                const char = (32 <= byte && byte < 127) ? String.fromCharCode(byte) : '.';
                console.error(`${prefix}offset ${i}: 0x${byte.toString(16).padStart(2, '0')} (${byte.toString().padStart(3)}) "${char}"`);
            }
        }
    });