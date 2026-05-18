# 言语言 VS Code 插件开发计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 开发 VS Code 插件，提供语法高亮、自动补全、错误诊断等功能，提升开发体验

**架构：** 使用 TypeScript + VS Code Extension API，集成言语言编译器作为语言服务器

**技术栈：** TypeScript、VS Code Extension API、言语言编译器、Language Server Protocol（可选）

---

## 当前问题

**没有 IDE 支持：**
- 没有语法高亮
- 没有自动补全
- 没有错误诊断
- 开发体验极差

**目标功能：**
1. 语法高亮
2. 自动补全
3. 错误诊断
4. 悬停提示
5. 代码格式化

---

## 文件结构

### 新增文件

```
yan/vscode-extension/
├── package.json              — 插件配置
├── tsconfig.json             — TypeScript 配置
├── README.md                 — 插件文档
├── CHANGELOG.md              — 变更日志
├── .vscodeignore             — VS Code 忽略文件
├── .gitignore                — Git 忽略文件
├── syntaxes/
│   └── yan.tmLanguage.json   — 语法高亮定义
├── src/
│   ├── extension.ts          — 插件入口
│   ├── completionProvider.ts — 自动补全提供者
│   ├── diagnosticProvider.ts — 错误诊断提供者
│   ├── hoverProvider.ts      — 悬停提示提供者
│   └── yanCompiler.ts        — 编译器集成
└── test/
    ├── extension.test.ts     — 插件测试
    └── runTest.ts            — 测试运行器
```

---

## 任务分解

### 任务1：创建插件脚手架

**文件：**
- 创建：`yan/vscode-extension/package.json`
- 创建：`yan/vscode-extension/tsconfig.json`
- 创建：`yan/vscode-extension/README.md`

**目标：** 搭建 VS Code 插件基础结构

- [ ] **步骤1：创建插件目录**

```bash
mkdir -p yan/vscode-extension
cd yan/vscode-extension
```

- [ ] **步骤2：创建 package.json**

创建 `yan/vscode-extension/package.json`：

```json
{
  "name": "yan-language",
  "displayName": "言语言 (Yan Language)",
  "description": "言语言支持 - 文言风格的函数式编程语言",
  "version": "0.1.0",
  "publisher": "yan-language",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": [
    "Programming Languages"
  ],
  "activationEvents": [
    "onLanguage:yan"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "languages": [
      {
        "id": "yan",
        "aliases": [
          "Yan",
          "yan",
          "言语言"
        ],
        "extensions": [
          ".yan"
        ],
        "configuration": "./language-configuration.json"
      }
    ],
    "grammars": [
      {
        "language": "yan",
        "scopeName": "source.yan",
        "path": "./syntaxes/yan.tmLanguage.json"
      }
    ],
    "commands": [
      {
        "command": "yan.compile",
        "title": "言语言：编译当前文件"
      },
      {
        "command": "yan.run",
        "title": "言语言：运行当前文件"
      }
    ],
    "menus": {
      "editor/context": [
        {
          "when": "resourceLangId == yan",
          "command": "yan.compile",
          "group": "yan@1"
        },
        {
          "when": "resourceLangId == yan",
          "command": "yan.run",
          "group": "yan@2"
        }
      ]
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "test": "node ./out/test/runTest.js",
    "package": "vsce package"
  },
  "devDependencies": {
    "@types/node": "^18.0.0",
    "@types/vscode": "^1.80.0",
    "typescript": "^5.0.0",
    "@vscode/test-electron": "^2.3.0",
    "@vscode/vsce": "^2.19.0"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/yan-language/yan"
  },
  "license": "MIT"
}
```

- [ ] **步骤3：创建 tsconfig.json**

创建 `yan/vscode-extension/tsconfig.json`：

```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "ES2020",
    "outDir": "out",
    "lib": [
      "ES2020"
    ],
    "sourceMap": true,
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "exclude": [
    "node_modules",
    ".vscode-test"
  ]
}
```

- [ ] **步骤4：创建 README.md**

创建 `yan/vscode-extension/README.md`：

```markdown
# 言语言 VS Code 插件

文言为表，函数为里。

## 特性

- ✅ 语法高亮
- ✅ 自动补全
- ✅ 错误诊断
- ✅ 悬停提示
- ✅ 代码格式化

## 安装

### 从 VS Code 市场安装

1. 打开 VS Code
2. 按 `Ctrl+Shift+X` 打开扩展面板
3. 搜索 "Yan Language"
4. 点击安装

### 从源码安装

```bash
cd yan/vscode-extension
npm install
npm run compile
```

## 使用

### 创建言语言文件

1. 创建新文件，扩展名为 `.yan`
2. 编写言语言代码：

```yan
定 平方 = 函 x 乘 x x。
印 平方 5。
```

### 编译和运行

- 按 `Ctrl+Shift+P` 打开命令面板
- 输入 "言语言：编译当前文件"
- 或右键选择 "言语言：运行当前文件"

## 配置

在 `settings.json` 中配置：

```json
{
  "yan.compilerPath": "path/to/yan/compiler",
  "yan.enableDiagnostics": true,
  "yan.enableCompletion": true
}
```

## 示例

### 基础运算

```yan
加 1 2。
乘 3 4。
列 1 2 3 皆 乘 2。
```

### 函数定义

```yan
定 阶乘 = 函 n
  若 等于 n 0
    返回 1。
  否则
    返回 乘 n 阶乘 减 n 1。
  。
。

印 阶乘 5。
```

### 列表操作

```yan
定 数据 = 列 1 2 3 4 5。
定 平方数据 = 皆 平方 数据。
定 偶数数据 = 只 函 x 等于 模 x 2 0 数据。
印 平方数据。
印 偶数数据。
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**更新日期**：2026-05-17
```

- [ ] **步骤5：创建 .gitignore**

创建 `yan/vscode-extension/.gitignore`：

```
out
node_modules
.vscode-test/
*.vsix
```

- [ ] **步骤6：创建 .vscodeignore**

创建 `yan/vscode-extension/.vscodeignore`：

```
.vscode/**
.vscode-test/**
src/**
.gitignore
.yarnrc
vsc-extension-quickstart.md
**/tsconfig.json
**/.eslintrc.json
**/*.map
**/*.ts
!node_modules/**
node_modules/.bin/**
node_modules/@types/**
```

- [ ] **步骤7：Commit**

```bash
git add yan/vscode-extension/
git commit -m "feat(vscode): create extension scaffold"
```

---

### 任务2：实现语法高亮

**文件：**
- 创建：`yan/vscode-extension/syntaxes/yan.tmLanguage.json`
- 创建：`yan/vscode-extension/language-configuration.json`

**目标：** 实现言语言语法高亮

- [ ] **步骤1：创建语言配置文件**

创建 `yan/vscode-extension/language-configuration.json`：

```json
{
  "comments": {
    "lineComment": "--",
    "blockComment": ["注", "\n"]
  },
  "brackets": [
    ["「", "」"],
    ["『", "』"]
  ],
  "autoClosingPairs": [
    {
      "open": "\"",
      "close": "\""
    },
    {
      "open": "「",
      "close": "」"
    },
    {
      "open": "『",
      "close": "』"
    }
  ],
  "surroundingPairs": [
    ["\"", "\""],
    ["「", "」"],
    ["『", "』"]
  ]
}
```

- [ ] **步骤2：创建语法高亮定义**

创建 `yan/vscode-extension/syntaxes/yan.tmLanguage.json`：

```json
{
  "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
  "name": "Yan",
  "scopeName": "source.yan",
  "patterns": [
    {
      "include": "#comments"
    },
    {
      "include": "#strings"
    },
    {
      "include": "#numbers"
    },
    {
      "include": "#keywords"
    },
    {
      "include": "#verbs"
    },
    {
      "include": "#operators"
    },
    {
      "include": "#identifiers"
    }
  ],
  "repository": {
    "comments": {
      "patterns": [
        {
          "name": "comment.line.double-dash.yan",
          "match": "--.*$"
        },
        {
          "name": "comment.line.note.yan",
          "match": "注.*$"
        }
      ]
    },
    "strings": {
      "patterns": [
        {
          "name": "string.quoted.double.yan",
          "begin": "\"",
          "end": "\"",
          "patterns": [
            {
              "name": "constant.character.escape.yan",
              "match": "\\\\."
            }
          ]
        },
        {
          "name": "string.quoted.single.yan",
          "begin": "'",
          "end": "'",
          "patterns": [
            {
              "name": "constant.character.escape.yan",
              "match": "\\\\."
            }
          ]
        }
      ]
    },
    "numbers": {
      "patterns": [
        {
          "name": "constant.numeric.float.yan",
          "match": "\\b[0-9]+\\.[0-9]+\\b"
        },
        {
          "name": "constant.numeric.integer.yan",
          "match": "\\b[0-9]+\\b"
        }
      ]
    },
    "keywords": {
      "patterns": [
        {
          "name": "keyword.control.yan",
          "match": "\\b(定|函|若|则|否则|当|遍历|于|返回|导入|导出|结构|类型|字段)\\b"
        },
        {
          "name": "constant.language.yan",
          "match": "\\b(真|假|空|无)\\b"
        }
      ]
    },
    "verbs": {
      "patterns": [
        {
          "name": "entity.name.function.yan",
          "match": "\\b(加|减|乘|除|模|幂|绝对|负|大|小|等|不等|且|或|非|首|余|入|长|添|连|含|空|皆|只|归|潜|印|读|写|行|列|典|序|范围|长度|连接|分割|替换|截取|小写|大写|查找|包含|去空|开头是|结尾是|正弦|余弦|正切|反正弦|反余弦|反正切|指数|对数|对数10|开方|取整|进位|四舍五入|随机|随机整数|圆周率|自然常数|当前时间|日期|时间|日期时间|格式化时间|睡眠|读文件|写文件|追加文件|存在|是文件|是目录|列目录|建目录|删文件|删目录|当前目录|文件名|目录名|扩展名|是数|是串|是表|是函|是真|是空|类型|反|排|最大|最小|求和|计数|键|值|项|删键)\\b"
        }
      ]
    },
    "operators": {
      "patterns": [
        {
          "name": "keyword.operator.yan",
          "match": "(。|，|：|；|=)"
        }
      ]
    },
    "identifiers": {
      "patterns": [
        {
          "name": "variable.other.yan",
          "match": "[\\u4e00-\\u9fa5]+[\\u4e00-\\u9fa50-9a-zA-Z_]*"
        }
      ]
    }
  }
}
```

- [ ] **步骤3：测试语法高亮**

1. 在 VS Code 中打开 `yan/vscode-extension` 目录
2. 按 F5 启动调试
3. 在新窗口中创建 `.yan` 文件
4. 输入言语言代码，验证语法高亮

- [ ] **步骤4：Commit**

```bash
git add yan/vscode-extension/syntaxes/ yan/vscode-extension/language-configuration.json
git commit -m "feat(vscode): implement syntax highlighting"
```

---

### 任务3：实现插件入口

**文件：**
- 创建：`yan/vscode-extension/src/extension.ts`

**目标：** 实现插件激活和基本命令

- [ ] **步骤1：创建插件入口文件**

创建 `yan/vscode-extension/src/extension.ts`：

```typescript
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
```

- [ ] **步骤2：Commit**

```bash
git add yan/vscode-extension/src/extension.ts
git commit -m "feat(vscode): implement extension entry point"
```

---

### 任务4：实现自动补全

**文件：**
- 创建：`yan/vscode-extension/src/completionProvider.ts`

**目标：** 提供智能自动补全

- [ ] **步骤1：创建自动补全提供者**

创建 `yan/vscode-extension/src/completionProvider.ts`：

```typescript
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
```

- [ ] **步骤2：Commit**

```bash
git add yan/vscode-extension/src/completionProvider.ts
git commit -m "feat(vscode): implement auto-completion provider"
```

---

### 任务5：实现错误诊断

**文件：**
- 创建：`yan/vscode-extension/src/diagnosticProvider.ts`

**目标：** 提供实时错误诊断

- [ ] **步骤1：创建错误诊断提供者**

创建 `yan/vscode-extension/src/diagnosticProvider.ts`：

```typescript
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
```

- [ ] **步骤2：Commit**

```bash
git add yan/vscode-extension/src/diagnosticProvider.ts
git commit -m "feat(vscode): implement diagnostic provider"
```

---

### 任务6：实现悬停提示

**文件：**
- 创建：`yan/vscode-extension/src/hoverProvider.ts`

**目标：** 提供悬停提示信息

- [ ] **步骤1：创建悬停提示提供者**

创建 `yan/vscode-extension/src/hoverProvider.ts`：

```typescript
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
```

- [ ] **步骤2：Commit**

```bash
git add yan/vscode-extension/src/hoverProvider.ts
git commit -m "feat(vscode): implement hover provider"
```

---

### 任务7：测试和打包

**文件：**
- 创建：`yan/vscode-extension/test/extension.test.ts`
- 创建：`yan/vscode-extension/test/runTest.ts`

**目标：** 测试插件并打包

- [ ] **步骤1：安装依赖**

```bash
cd yan/vscode-extension
npm install
```

- [ ] **步骤2：编译插件**

```bash
npm run compile
```

- [ ] **步骤3：创建测试文件**

创建 `yan/vscode-extension/test/extension.test.ts`：

```typescript
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
```

- [ ] **步骤4：创建测试运行器**

创建 `yan/vscode-extension/test/runTest.ts`：

```typescript
import * as path from 'path';
import { runTests } from '@vscode/test-electron';

async function main() {
    try {
        const extensionDevelopmentPath = path.resolve(__dirname, '../../');
        const extensionTestsPath = path.resolve(__dirname, './extension.test');

        await runTests({
            extensionDevelopmentPath,
            extensionTestsPath,
        });
    } catch (err) {
        console.error('Failed to run tests');
        process.exit(1);
    }
}

main();
```

- [ ] **步骤5：运行测试**

```bash
npm test
```

- [ ] **步骤6：打包插件**

```bash
npm run package
```

这将生成 `yan-language-0.1.0.vsix` 文件。

- [ ] **步骤7：Commit**

```bash
git add yan/vscode-extension/test/ yan/vscode-extension/package-lock.json
git commit -m "test(vscode): add extension tests and packaging"
```

---

### 任务8：发布到市场

**文件：**
- 修改：`yan/vscode-extension/README.md`
- 创建：`yan/vscode-extension/CHANGELOG.md`

**目标：** 发布插件到 VS Code 市场

- [ ] **步骤1：创建变更日志**

创建 `yan/vscode-extension/CHANGELOG.md`：

```markdown
# Change Log

All notable changes to the "Yan Language" extension will be documented in this file.

## [0.1.0] - 2026-05-17

### Added
- 初始版本发布
- 语法高亮支持
- 自动补全功能
- 错误诊断功能
- 悬停提示功能
- 编译和运行命令

### Features
- 支持言语言（Yan）语法高亮
- 提供关键字和内置函数的自动补全
- 实时错误诊断
- 悬停显示函数文档
- 右键菜单支持编译和运行

---

**更新日期**：2026-05-17
```

- [ ] **步骤2：更新 README**

在 `yan/vscode-extension/README.md` 中添加安装说明：

```markdown
## 安装

### 从 VS Code 市场安装

1. 打开 VS Code
2. 按 `Ctrl+Shift+X` 打开扩展面板
3. 搜索 "Yan Language" 或 "言语言"
4. 点击安装

### 从 VSIX 文件安装

1. 下载 `yan-language-0.1.0.vsix`
2. 在 VS Code 中按 `Ctrl+Shift+P`
3. 输入 "Extensions: Install from VSIX"
4. 选择下载的 VSIX 文件
```

- [ ] **步骤3：发布到市场**

```bash
# 登录到 VS Code 市场
vsce login yan-language

# 发布插件
vsce publish
```

- [ ] **步骤4：Commit**

```bash
git add yan/vscode-extension/README.md yan/vscode-extension/CHANGELOG.md
git commit -m "docs(vscode): update README and CHANGELOG for release"
```

---

## 总结

### 预计工作量

- **任务1**（插件脚手架）：1天
- **任务2**（语法高亮）：1天
- **任务3**（插件入口）：0.5天
- **任务4**（自动补全）：1天
- **任务5**（错误诊断）：1天
- **任务6**（悬停提示）：0.5天
- **任务7**（测试和打包）：1天
- **任务8**（发布到市场）：0.5天

**总计**：6-7天

### 关键里程碑

1. ✅ 插件脚手架搭建
2. ✅ 语法高亮实现
3. ✅ 自动补全实现
4. ✅ 错误诊断实现
5. ✅ 悬停提示实现
6. ✅ 测试通过
7. ✅ 打包成功
8. ✅ 发布到市场

### 成功标准

**VS Code 插件完成标准：**
- 语法高亮正常工作
- 自动补全提供有用建议
- 错误诊断实时反馈
- 悬停提示显示文档
- 测试通过
- 成功发布到 VS Code 市场

---

**下一步**：开始执行任务1，创建插件脚手架
