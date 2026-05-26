import * as vscode from 'vscode';
import * as path from 'path';
import * as child_process from 'child_process';
import { YanCompletionItemProvider } from './completionProvider';
import { YanDiagnosticsProvider } from './diagnosticProvider';
import { YanHoverProvider } from './hoverProvider';
import { YanDefinitionProvider } from './definitionProvider';
import { YanReferencesProvider } from './referencesProvider';

let diagnosticProvider: YanDiagnosticsProvider;
let yanLanguagePath: string;

export function activate(context: vscode.ExtensionContext) {
    console.log('言语言插件已激活');

    // 确定言语言项目路径
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    yanLanguagePath = workspaceFolder ? workspaceFolder.uri.fsPath : '';

    // 注册自动补全提供者
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        'yan',
        new YanCompletionItemProvider(),
        '.', ' ', '\t'
    );
    context.subscriptions.push(completionProvider);

    // 注册悬停提示提供者
    const hoverProvider = vscode.languages.registerHoverProvider(
        'yan',
        new YanHoverProvider()
    );
    context.subscriptions.push(hoverProvider);

    // 注册定义跳转提供者
    const definitionProvider = vscode.languages.registerDefinitionProvider(
        'yan',
        new YanDefinitionProvider()
    );
    context.subscriptions.push(definitionProvider);

    // 注册引用查找提供者
    const referencesProvider = vscode.languages.registerReferenceProvider(
        'yan',
        new YanReferencesProvider()
    );
    context.subscriptions.push(referencesProvider);

    // 注册代码格式化提供者
    const formatProvider = vscode.languages.registerDocumentFormattingEditProvider(
        'yan',
        {
            provideDocumentFormattingEdits: formatDocument
        }
    );
    context.subscriptions.push(formatProvider);

    // 初始化错误诊断提供者
    diagnosticProvider = new YanDiagnosticsProvider();
    diagnosticProvider.activate(context);

    // 注册编译命令
    const compileCommand = vscode.commands.registerCommand('yan.compile', () => {
        compileCurrentFile();
    });
    context.subscriptions.push(compileCommand);

    // 注册运行命令
    const runCommand = vscode.commands.registerCommand('yan.run', () => {
        runCurrentFile();
    });
    context.subscriptions.push(runCommand);

    // 注册格式化命令
    const formatCommand = vscode.commands.registerCommand('yan.format', () => {
        formatCurrentFile();
    });
    context.subscriptions.push(formatCommand);

    // 注册调试器
    const debugAdapterFactory = {
        createDebugAdapterDescriptor: (session: vscode.DebugSession, executable: vscode.DebugAdapterExecutable) => {
            // 使用服务器模式
            return new vscode.DebugAdapterServer(4711);
        }
    };
    context.subscriptions.push(
        vscode.debug.registerDebugAdapterDescriptorFactory('yan', debugAdapterFactory)
    );
}

export function deactivate() {
    if (diagnosticProvider) {
        diagnosticProvider.deactivate();
    }
}

/**
 * 格式化文档
 */
function formatDocument(
    document: vscode.TextDocument,
    options: vscode.FormattingOptions,
    token: vscode.CancellationToken
): vscode.ProviderResult<vscode.TextEdit[]> {
    const edits: vscode.TextEdit[] = [];
    const text = document.getText();
    const formatted = formatCode(text, options);
    
    const fullRange = new vscode.Range(
        document.positionAt(0),
        document.positionAt(text.length)
    );
    
    edits.push(vscode.TextEdit.replace(fullRange, formatted));
    return edits;
}

/**
 * 格式化代码
 */
function formatCode(code: string, options: vscode.FormattingOptions): string {
    const lines = code.split('\n');
    const formattedLines: string[] = [];
    let currentIndent = 0;
    const indentSize = vscode.workspace.getConfiguration('yan.format').get<number>('indentSize', 2);
    
    for (let line of lines) {
        const trimmed = line.trim();
        
        if (trimmed === '') {
            formattedLines.push('');
            continue;
        }
        
        // 计算缩进级别
        if (trimmed.startsWith('函') || trimmed.startsWith('若') || 
            trimmed.startsWith('遍历') || trimmed.startsWith('当') ||
            trimmed.startsWith('结构') || trimmed.startsWith('套') ||
            trimmed.startsWith('测')) {
            currentIndent++;
        } else if (trimmed.startsWith('否则') || trimmed.startsWith('则')) {
            // 不改变缩进，保持当前级别
        } else if (trimmed === '。') {
            // 块结束，减少缩进
            currentIndent = Math.max(0, currentIndent - 1);
        }
        
        // 应用缩进
        const indent = ' '.repeat(currentIndent * indentSize);
        formattedLines.push(indent + trimmed);
    }
    
    return formattedLines.join('\n');
}

/**
 * 格式化当前文件
 */
async function formatCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('没有打开的文件');
        return;
    }
    
    if (editor.document.languageId !== 'yan') {
        vscode.window.showErrorMessage('当前文件不是言语言文件');
        return;
    }
    
    try {
        await vscode.commands.executeCommand('editor.action.formatDocument');
        vscode.window.showInformationMessage('格式化完成');
    } catch (error) {
        vscode.window.showErrorMessage(`格式化失败：${error}`);
    }
}

/**
 * 编译当前文件
 */
async function compileCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('没有打开的文件');
        return;
    }

    const document = editor.document;
    if (document.languageId !== 'yan') {
        vscode.window.showErrorMessage('当前文件不是言语言文件');
        return;
    }

    await document.save();
    
    try {
        const pythonPath = vscode.workspace.getConfiguration('yan').get<string>('pythonPath', 'python');
        const mainPyPath = path.join(yanLanguagePath, 'yan', 'main.py');
        
        if (yanLanguagePath) {
            const result = await runYanCommand(pythonPath, mainPyPath, document.uri.fsPath);
            if (result.success) {
                vscode.window.showInformationMessage('编译成功！');
            } else {
                vscode.window.showErrorMessage(`编译失败：${result.output}`);
            }
        } else {
            vscode.window.showWarningMessage('请在工作区中打开言语言项目');
        }
    } catch (error) {
        vscode.window.showErrorMessage(`编译失败：${error}`);
    }
}

/**
 * 运行当前文件
 */
async function runCurrentFile() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('没有打开的文件');
        return;
    }

    const document = editor.document;
    if (document.languageId !== 'yan') {
        vscode.window.showErrorMessage('当前文件不是言语言文件');
        return;
    }

    await document.save();
    
    try {
        const pythonPath = vscode.workspace.getConfiguration('yan').get<string>('pythonPath', 'python');
        const mainPyPath = path.join(yanLanguagePath, 'yan', 'main.py');
        
        if (yanLanguagePath) {
            // 在终端中运行
            const terminal = vscode.window.createTerminal('言语言');
            terminal.show();
            terminal.sendText(`cd "${yanLanguagePath}"`, true);
            terminal.sendText(`${pythonPath} "${mainPyPath}" "${document.uri.fsPath}"`, true);
        } else {
            vscode.window.showWarningMessage('请在工作区中打开言语言项目');
        }
    } catch (error) {
        vscode.window.showErrorMessage(`运行失败：${error}`);
    }
}

/**
 * 运行言语言命令
 */
async function runYanCommand(pythonPath: string, mainPy: string, file: string): Promise<{success: boolean, output: string}> {
    return new Promise((resolve, reject) => {
        child_process.execFile(
            pythonPath,
            [mainPy, file],
            { cwd: yanLanguagePath },
            (error, stdout, stderr) => {
                if (error) {
                    resolve({ success: false, output: stderr || error.message });
                } else if (stderr) {
                    resolve({ success: false, output: stderr });
                } else {
                    resolve({ success: true, output: stdout });
                }
            }
        );
    });
}
