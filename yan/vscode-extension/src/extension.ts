import * as vscode from 'vscode';
import { YanCompletionItemProvider } from './completionProvider';
import { YanDiagnosticsProvider } from './diagnosticProvider';
import { YanHoverProvider } from './hoverProvider';

let diagnosticProvider: YanDiagnosticsProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('言语言插件已激活');

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
}

export function deactivate() {
    if (diagnosticProvider) {
        diagnosticProvider.deactivate();
    }
}

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

    try {
        // TODO: 调用编译器
        vscode.window.showInformationMessage('编译成功！');
    } catch (error) {
        vscode.window.showErrorMessage(`编译失败：${error}`);
    }
}

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

    try {
        // TODO: 调用编译器并运行
        vscode.window.showInformationMessage('运行成功！');
    } catch (error) {
        vscode.window.showErrorMessage(`运行失败：${error}`);
    }
}
