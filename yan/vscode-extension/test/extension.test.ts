import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Start all tests.');

    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('yan-language.yan-language'));
    });

    test('Extension should activate', async () => {
        const extension = vscode.extensions.getExtension('yan-language.yan-language');
        if (extension) {
            await extension.activate();
            assert.ok(extension.isActive);
        }
    });

    test('Yan language should be registered', async () => {
        const doc = await vscode.workspace.openTextDocument({
            content: '定 x = 42。',
            language: 'yan'
        });
        
        assert.strictEqual(doc.languageId, 'yan');
    });
});
