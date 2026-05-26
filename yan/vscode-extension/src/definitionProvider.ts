import * as vscode from 'vscode';

export class YanDefinitionProvider implements vscode.DefinitionProvider {
    
    private definitions: Map<string, vscode.Location[]> = new Map();
    
    provideDefinition(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.Definition> {
        const wordRange = document.getWordRangeAtPosition(position);
        if (!wordRange) {
            return undefined;
        }
        
        const word = document.getText(wordRange);
        
        const locations: vscode.Location[] = [];
        
        // 搜索当前文档中的定义
        this.findDefinitionsInDocument(document, word, locations);
        
        // 搜索其他已打开的文档
        this.findDefinitionsInOtherDocuments(word, locations);
        
        return locations.length > 0 ? locations : undefined;
    }
    
    private findDefinitionsInDocument(document: vscode.TextDocument, word: string, locations: vscode.Location[]): void {
        const text = document.getText();
        const lines = text.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // 查找变量定义：定 名称 =
            const defineMatch = line.match(new RegExp(`定\\s+(${word})\\s*=`));
            if (defineMatch) {
                const startCol = line.indexOf(defineMatch[1]);
                const range = new vscode.Range(i, startCol, i, startCol + word.length);
                locations.push(new vscode.Location(document.uri, range));
                continue;
            }
            
            // 查找函数定义：函 参数名
            const funcMatch = line.match(new RegExp(`函\\s+(${word})`));
            if (funcMatch) {
                const startCol = line.indexOf(funcMatch[1]);
                const range = new vscode.Range(i, startCol, i, startCol + word.length);
                locations.push(new vscode.Location(document.uri, range));
                continue;
            }
            
            // 查找结构定义：结构 名称
            const structMatch = line.match(new RegExp(`结构\\s+(${word})`));
            if (structMatch) {
                const startCol = line.indexOf(structMatch[1]);
                const range = new vscode.Range(i, startCol, i, startCol + word.length);
                locations.push(new vscode.Location(document.uri, range));
                continue;
            }
        }
    }
    
    private findDefinitionsInOtherDocuments(word: string, locations: vscode.Location[]): void {
        for (const doc of vscode.workspace.textDocuments) {
            if (doc.languageId !== 'yan') {
                continue;
            }
            
            const text = doc.getText();
            const lines = text.split('\n');
            
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                
                // 查找变量定义
                const defineMatch = line.match(new RegExp(`定\\s+(${word})\\s*=`));
                if (defineMatch) {
                    const startCol = line.indexOf(defineMatch[1]);
                    const range = new vscode.Range(i, startCol, i, startCol + word.length);
                    locations.push(new vscode.Location(doc.uri, range));
                    continue;
                }
                
                // 查找函数定义
                const funcMatch = line.match(new RegExp(`函\\s+(${word})`));
                if (funcMatch) {
                    const startCol = line.indexOf(funcMatch[1]);
                    const range = new vscode.Range(i, startCol, i, startCol + word.length);
                    locations.push(new vscode.Location(doc.uri, range));
                    continue;
                }
                
                // 查找结构定义
                const structMatch = line.match(new RegExp(`结构\\s+(${word})`));
                if (structMatch) {
                    const startCol = line.indexOf(structMatch[1]);
                    const range = new vscode.Range(i, startCol, i, startCol + word.length);
                    locations.push(new vscode.Location(doc.uri, range));
                    continue;
                }
            }
        }
    }
}