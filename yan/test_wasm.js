const fs = require('fs');
const path = require('path');

const wasmPath = 'wasm_output/tower_of_hanoi.wasm';

try {
    const wasmBytes = fs.readFileSync(wasmPath);
    console.log(`WASM 文件大小: ${wasmBytes.length} 字节`);
    console.log(`前 32 字节 (hex): ${wasmBytes.slice(0, 32).toString('hex')}`);

    const importObject = {
        env: {
            print: (ptr) => console.log(`[字符串@${ptr}]`),
            print_num: (num) => console.log(num),
            print_float: (num) => console.log(num)
        }
    };

    WebAssembly.instantiate(wasmBytes, importObject)
        .then(result => {
            console.log('WASM 加载成功!');
            console.log('导出函数:', Object.keys(result.instance.exports));
            result.instance.exports.main();
        })
        .catch(err => {
            console.error('WASM 加载失败:', err.message);
            console.error('错误详情:', err);
        });
} catch (e) {
    console.error('读取文件失败:', e.message);
}