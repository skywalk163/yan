import * as vscode from 'vscode';

export class YanCompletionItemProvider implements vscode.CompletionItemProvider {
    
    private keywords: vscode.CompletionItem[] = [];
    private verbs: vscode.CompletionItem[] = [];
    
    constructor() {
        this.initKeywords();
        this.initVerbs();
    }
    
    private initKeywords() {
        const keywords = [
            { label: '定', detail: '定义变量或函数', snippet: '定 ${1:名称} = ${2:值}。' },
            { label: '函', detail: '定义函数', snippet: '函 ${1:参数}\n  ${2:函数体}\n。' },
            { label: '若', detail: '条件语句', snippet: '若 ${1:条件}\n  ${2:真分支}\n否则\n  ${3:假分支}\n。' },
            { label: '则', detail: '条件分支' },
            { label: '否则', detail: '条件分支' },
            { label: '当', detail: '当循环', snippet: '当 ${1:条件}\n  ${2:循环体}\n。' },
            { label: '遍历', detail: '遍历循环', snippet: '遍历 ${1:变量} 于 ${2:列表}\n  ${3:循环体}\n。' },
            { label: '于', detail: '遍历范围' },
            { label: '返回', detail: '返回值', snippet: '返回 ${1:值}。' },
            { label: '导入', detail: '导入模块', snippet: '导入 ${1:模块名}。' },
            { label: '导出', detail: '导出符号', snippet: '导出 ${1:名称}。' },
            { label: '结构', detail: '定义结构体', snippet: '结构 ${1:名称}\n  ${2:字段} ${3:类型}。\n。' },
            { label: '类型', detail: '类型声明' },
            { label: '字段', detail: '字段声明' },
            { label: '真', detail: '布尔值真' },
            { label: '假', detail: '布尔值假' },
            { label: '空', detail: '空值' },
            { label: '无', detail: '无返回值' }
        ];
        
        this.keywords = keywords.map(k => {
            const item = new vscode.CompletionItem(k.label, vscode.CompletionItemKind.Keyword);
            item.detail = k.detail;
            if (k.snippet) {
                item.insertText = new vscode.SnippetString(k.snippet);
            }
            return item;
        });
    }
    
    private initVerbs() {
        const verbs = [
            // 算术运算
            { label: '加', detail: '加法', snippet: '加 ${1:a} ${2:b}' },
            { label: '减', detail: '减法', snippet: '减 ${1:a} ${2:b}' },
            { label: '乘', detail: '乘法', snippet: '乘 ${1:a} ${2:b}' },
            { label: '除', detail: '除法', snippet: '除 ${1:a} ${2:b}' },
            { label: '模', detail: '取模', snippet: '模 ${1:a} ${2:b}' },
            { label: '幂', detail: '幂运算', snippet: '幂 ${1:a} ${2:b}' },
            
            // 比较运算
            { label: '大', detail: '大于', snippet: '大 ${1:a} ${2:b}' },
            { label: '小', detail: '小于', snippet: '小 ${1:a} ${2:b}' },
            { label: '等', detail: '等于', snippet: '等 ${1:a} ${2:b}' },
            { label: '不等', detail: '不等于', snippet: '不等 ${1:a} ${2:b}' },
            
            // 逻辑运算
            { label: '且', detail: '逻辑与', snippet: '且 ${1:a} ${2:b}' },
            { label: '或', detail: '逻辑或', snippet: '或 ${1:a} ${2:b}' },
            { label: '非', detail: '逻辑非', snippet: '非 ${1:a}' },
            
            // 列表操作
            { label: '列', detail: '创建列表', snippet: '列 ${1:元素1} ${2:元素2} ${3:元素3}' },
            { label: '首', detail: '列表首元素', snippet: '首 ${1:列表}' },
            { label: '余', detail: '列表剩余', snippet: '余 ${1:列表}' },
            { label: '入', detail: '列表索引', snippet: '入 ${1:列表} ${2:索引}' },
            { label: '长', detail: '列表长度', snippet: '长 ${1:列表}' },
            { label: '添', detail: '添加元素', snippet: '添 ${1:列表} ${2:元素}' },
            { label: '反', detail: '反转列表', snippet: '反 ${1:列表}' },
            { label: '排', detail: '排序列表', snippet: '排 ${1:列表}' },
            { label: '最大', detail: '最大值', snippet: '最大 ${1:列表}' },
            { label: '最小', detail: '最小值', snippet: '最小 ${1:列表}' },
            { label: '求和', detail: '求和', snippet: '求和 ${1:列表}' },
            { label: '计数', detail: '计数', snippet: '计数 ${1:列表} ${2:值}' },
            
            // 高阶函数
            { label: '皆', detail: '映射（map）', snippet: '皆 ${1:函数} ${2:列表}' },
            { label: '只', detail: '过滤（filter）', snippet: '只 ${1:函数} ${2:列表}' },
            { label: '归', detail: '归约（reduce）', snippet: '归 ${1:函数} ${2:初始值} ${3:列表}' },
            
            // 输入输出
            { label: '印', detail: '打印输出', snippet: '印 ${1:值}。' },
            { label: '读', detail: '读取输入', snippet: '读' },
            { label: '写', detail: '写入输出', snippet: '写 ${1:值}' },
            
            // 字典操作
            { label: '典', detail: '创建字典', snippet: '典 ${1:键1} ${2:值1} ${3:键2} ${4:值2}' },
            { label: '键', detail: '获取键', snippet: '键 ${1:字典}' },
            { label: '值', detail: '获取值', snippet: '值 ${1:字典}' },
            { label: '项', detail: '获取键值对', snippet: '项 ${1:字典}' },
            { label: '删键', detail: '删除键', snippet: '删键 ${1:字典} ${2:键}' }
        ];
        
        this.verbs = verbs.map(v => {
            const item = new vscode.CompletionItem(v.label, vscode.CompletionItemKind.Function);
            item.detail = v.detail;
            if (v.snippet) {
                item.insertText = new vscode.SnippetString(v.snippet);
            }
            return item;
        });
    }
    
    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): vscode.ProviderResult<vscode.CompletionItem[] | vscode.CompletionList> {
        // 返回所有补全项
        return [...this.keywords, ...this.verbs];
    }
}
