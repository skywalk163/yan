import * as vscode from 'vscode';

export class YanReferencesProvider implements vscode.ReferenceProvider {
    
    provideReferences(
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.ReferenceContext,
        token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.Location[]> {
        const wordRange = document.getWordRangeAtPosition(position);
        if (!wordRange) {
            return undefined;
        }
        
        const word = document.getText(wordRange);
        const locations: vscode.Location[] = [];
        
        // 搜索当前文档中的引用
        this.findReferencesInDocument(document, word, locations, context.includeDeclaration);
        
        // 搜索其他已打开的文档
        this.findReferencesInOtherDocuments(word, locations);
        
        return locations.length > 0 ? locations : undefined;
    }
    
    private findReferencesInDocument(document: vscode.TextDocument, word: string, locations: vscode.Location[], includeDeclaration: boolean): void {
        const text = document.getText();
        const lines = text.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const pattern = new RegExp(`\\b(${word})\\b`, 'g');
            let match;
            
            while ((match = pattern.exec(line)) !== null) {
                const startCol = match.index;
                const range = new vscode.Range(i, startCol, i, startCol + word.length);
                
                // 检查是否是定义
                const isDefinition = line.match(new RegExp(`定\\s+${word}\\s*=`)) ||
                                    line.match(new RegExp(`函\\s+${word}`)) ||
                                    line.match(new RegExp(`结构\\s+${word}`));
                
                if (isDefinition && !includeDeclaration) {
                    continue;
                }
                
                locations.push(new vscode.Location(document.uri, range));
            }
        }
    }
    
    private findReferencesInOtherDocuments(word: string, locations: vscode.Location[]): void {
        for (const doc of vscode.workspace.textDocuments) {
            if (doc.languageId !== 'yan') {
                continue;
            }
            
            const text = doc.getText();
            const lines = text.split('\n');
            
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const pattern = new RegExp(`\\b(${word})\\b`, 'g');
                let match;
                
                while ((match = pattern.exec(line)) !== null) {
                    const startCol = match.index;
                    const range = new vscode.Range(i, startCol, i, startCol + word.length);
                    locations.push(new vscode.Location(doc.uri, range));
                }
            }
        }
    }
}