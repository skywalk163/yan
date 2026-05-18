import * as vscode from 'vscode';
import { exec } from 'child_process';
import * as path from 'path';

export class YanDiagnosticsProvider {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private debounceTimer: NodeJS.Timeout | undefined;
    
    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('yan');
    }
    
    activate(context: vscode.ExtensionContext) {
        // 监听文档变化
        context.subscriptions.push(
            vscode.workspace.onDidChangeTextDocument(event => {
                this.debounceDiagnostics(event.document);
            })
        );
        
        // 监听文档打开
        context.subscriptions.push(
            vscode.workspace.onDidOpenTextDocument(document => {
                if (document.languageId === 'yan') {
                    this.updateDiagnostics(document);
                }
            })
        );
        
        // 监听文档保存
        context.subscriptions.push(
            vscode.workspace.onDidSaveTextDocument(document => {
                if (document.languageId === 'yan') {
                    this.updateDiagnostics(document);
                }
            })
        );
        
        // 初始化当前打开的文档
        if (vscode.window.activeTextEditor) {
            this.updateDiagnostics(vscode.window.activeTextEditor.document);
        }
    }
    
    deactivate() {
        this.diagnosticCollection.dispose();
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
    }
    
    private debounceDiagnostics(document: vscode.TextDocument) {
        if (document.languageId !== 'yan') {
            return;
        }
        
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        this.debounceTimer = setTimeout(() => {
            this.updateDiagnostics(document);
        }, 500); // 500ms 防抖
    }
    
    private updateDiagnostics(document: vscode.TextDocument) {
        const diagnostics: vscode.Diagnostic[] = [];
        
        // 简单的语法检查
        const text = document.getText();
        const lines = text.split('\n');
        
        lines.forEach((line, lineIndex) => {
            // 检查未闭合的字符串
            const stringMatches = line.match(/"/g);
            if (stringMatches && stringMatches.length % 2 !== 0) {
                const startPos = new vscode.Position(lineIndex, 0);
                const endPos = new vscode.Position(lineIndex, line.length);
                const range = new vscode.Range(startPos, endPos);
                
                const diagnostic = new vscode.Diagnostic(
                    range,
                    '字符串未闭合',
                    vscode.DiagnosticSeverity.Error
                );
                diagnostics.push(diagnostic);
            }
            
            // 检查未闭合的括号
            // TODO: 实现更复杂的括号匹配
        });
        
        this.diagnosticCollection.set(document.uri, diagnostics);
    }
    
    private async compileWithYanCompiler(document: vscode.TextDocument): Promise<vscode.Diagnostic[]> {
        // TODO: 调用言语言编译器进行编译
        // 返回编译错误
        return [];
    }
}
