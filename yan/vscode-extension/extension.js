const vscode = require('vscode');
const path = require('path');
const { LanguageClient, TransportKind } = require('vscode-languageclient');

let client = null;

function activate(context) {
    const serverModule = context.asAbsolutePath(path.join('server', 'main.js'));
    const serverOptions = {
        run: {
            module: serverModule,
            transport: TransportKind.stdio,
            options: { cwd: context.extensionPath }
        },
        debug: {
            module: serverModule,
            transport: TransportKind.stdio,
            options: { cwd: context.extensionPath, execArgv: ['--nolazy', '--inspect=6009'] }
        }
    };

    const clientOptions = {
        documentSelector: [
            { scheme: 'file', language: 'yan' },
            { scheme: 'file', language: 'yanmd' }
        ],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.yan')
        },
        outputChannelName: '言语言'
    };

    client = new LanguageClient('yanLanguageServer', '言语言 LSP 服务器', serverOptions, clientOptions);

    const disposable = client.start();
    context.subscriptions.push(disposable);

    client.onReady().then(() => {
        client.sendNotification('initialized', {});
    }).catch(err => {
        vscode.window.showErrorMessage(`言语言服务器启动失败: ${err.message}`);
    });

    vscode.commands.registerCommand('yan.formatDocument', async () => {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const doc = editor.document;
            if (doc.languageId === 'yan' || doc.languageId === 'yanmd') {
                const result = await vscode.commands.executeCommand('editor.action.formatDocument');
                return result;
            }
        }
    });

    vscode.commands.registerCommand('yan.runFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }

        const doc = editor.document;
        const filePath = doc.fileName;

        if (doc.languageId !== 'yan') {
            vscode.window.showWarningMessage('当前文件不是言语言文件');
            return;
        }

        const terminal = vscode.window.createTerminal(`言语言: ${path.basename(filePath)}`);
        terminal.sendText(`python -m yan.main "${filePath}"`);
        terminal.show();
    });

    vscode.commands.registerCommand('yan.showDocumentation', async () => {
        const docs = [
            '言语言内置函数参考',
            '',
            '## 算术运算',
            '加(a, b) - 加法',
            '减(a, b) - 减法',
            '乘(a, b) - 乘法',
            '除(a, b) - 除法',
            '',
            '## 列表操作',
            '列(...) - 创建列表',
            '首(列表) - 首元素',
            '余(列表) - 剩余列表',
            '',
            '## 高阶函数',
            '皆(函数, 列表) - 映射',
            '只(谓词, 列表) - 过滤',
            '归(函数, 初始值, 列表) - 归约',
            '',
            '## 文件操作',
            '读文件(路径) - 读文件',
            '写文件(路径, 内容) - 写文件'
        ].join('\n');

        const doc = await vscode.workspace.openMarkdownString({ value: docs });
        vscode.window.showInformationMessage(doc.value, { modal: false });
    });
}

function deactivate() {
    if (client) {
        return client.stop();
    }
    return undefined;
}

module.exports = {
    activate,
    deactivate
};
