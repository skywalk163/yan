import * as vscode from 'vscode';

export class YanHoverProvider implements vscode.HoverProvider {
    
    private documentation: Map<string, string> = new Map();
    
    constructor() {
        this.initDocumentation();
    }
    
    private initDocumentation() {
        // 关键字文档
        this.documentation.set('定', '**定** - 定义变量或函数\n\n用于定义变量或函数。\n\n示例：\n```yan\n定 x = 42。\n定 平方 = 函 x 乘 x x。\n```');
        this.documentation.set('函', '**函** - 定义函数\n\n用于定义函数。\n\n示例：\n```yan\n定 平方 = 函 x\n  返回 乘 x x。\n。\n```');
        this.documentation.set('若', '**若** - 条件语句\n\n用于条件判断。\n\n示例：\n```yan\n若 大 x 0\n  印 "正数"。\n否则\n  印 "非正数"。\n。\n```');
        this.documentation.set('当', '**当** - 当循环\n\n当条件为真时循环。\n\n示例：\n```yan\n定 i = 0。\n当 小 i 10\n  印 i。\n  定 i = 加 i 1。\n。\n```');
        this.documentation.set('遍历', '**遍历** - 遍历循环\n\n遍历列表中的每个元素。\n\n示例：\n```yan\n遍历 x 于 列 1 2 3\n  印 x。\n。\n```');
        
        // 内置动词文档
        this.documentation.set('加', '**加** - 加法\n\n返回两个数的和。\n\n```yan\n加 1 2。  -- 返回 3\n```');
        this.documentation.set('减', '**减** - 减法\n\n返回两个数的差。\n\n```yan\n减 5 3。  -- 返回 2\n```');
        this.documentation.set('乘', '**乘** - 乘法\n\n返回两个数的积。\n\n```yan\n乘 3 4。  -- 返回 12\n```');
        this.documentation.set('除', '**除** - 除法\n\n返回两个数的商。\n\n```yan\n除 10 2。  -- 返回 5\n```');
        
        this.documentation.set('列', '**列** - 创建列表\n\n创建一个列表。\n\n```yan\n列 1 2 3。  -- 返回 [1, 2, 3]\n```');
        this.documentation.set('首', '**首** - 列表首元素\n\n返回列表的第一个元素。\n\n```yan\n首 列 1 2 3。  -- 返回 1\n```');
        this.documentation.set('余', '**余** - 列表剩余\n\n返回列表除第一个元素外的剩余部分。\n\n```yan\n余 列 1 2 3。  -- 返回 [2, 3]\n```');
        this.documentation.set('入', '**入** - 列表索引\n\n返回列表中指定索引的元素。\n\n```yan\n入 列 1 2 3 0。  -- 返回 1\n```');
        this.documentation.set('长', '**长** - 列表长度\n\n返回列表的长度。\n\n```yan\n长 列 1 2 3。  -- 返回 3\n```');
        
        this.documentation.set('皆', '**皆** - 映射（map）\n\n对列表中的每个元素应用函数。\n\n```yan\n皆 平方 列 1 2 3。  -- 返回 [1, 4, 9]\n```');
        this.documentation.set('只', '**只** - 过滤（filter）\n\n过滤列表中满足条件的元素。\n\n```yan\n只 函 x 大 x 1 列 1 2 3。  -- 返回 [2, 3]\n```');
        this.documentation.set('归', '**归** - 归约（reduce）\n\n将列表归约为单个值。\n\n```yan\n归 加 0 列 1 2 3。  -- 返回 6\n```');
        
        this.documentation.set('印', '**印** - 打印输出\n\n打印值到标准输出。\n\n```yan\n印 "你好，世界！"。  -- 输出：你好，世界！\n```');
    }
    
    provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.Hover> {
        const range = document.getWordRangeAtPosition(position);
        if (!range) {
            return undefined;
        }
        
        const word = document.getText(range);
        const doc = this.documentation.get(word);
        
        if (doc) {
            return new vscode.Hover(doc, range);
        }
        
        return undefined;
    }
}
