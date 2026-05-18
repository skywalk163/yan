import * as vscode from 'vscode';

export class YanCompletionItemProvider implements vscode.CompletionItemProvider {
    
    private keywords: vscode.CompletionItem[] = [];
    private verbs: vscode.CompletionItem[] = [];
    private standardLibrary: Map<string, vscode.CompletionItem[]> = new Map();
    
    constructor() {
        this.initKeywords();
        this.initVerbs();
        this.initStandardLibrary();
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
            { label: '引', detail: '导入模块', snippet: '引 ${1:模块名}。' },
            { label: '导出', detail: '导出符号', snippet: '导出 ${1:名称}。' },
            { label: '出', detail: '导出符号', snippet: '出 ${1:名称}。' },
            { label: '结构', detail: '定义结构体', snippet: '结构 ${1:名称}\n  ${2:字段} ${3:类型}。\n。' },
            { label: '类型', detail: '类型声明' },
            { label: '字段', detail: '字段声明' },
            { label: '套', detail: '测试套件', snippet: '套 \"${1:套件名称}\"\n  ${2:测试}\n。' },
            { label: '测', detail: '测试用例', snippet: '测 \"${1:测试名称}\":\n  ${2:断言}\n。' },
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
            { label: '绝对', detail: '绝对值', snippet: '绝对 ${1:a}' },
            { label: '负', detail: '负数', snippet: '负 ${1:a}' },
            
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
            { label: '序', detail: '创建序列', snippet: '序 ${1:元素1} ${2:元素2}' },
            { label: '首', detail: '列表首元素', snippet: '首 ${1:列表}' },
            { label: '余', detail: '列表剩余', snippet: '余 ${1:列表}' },
            { label: '入', detail: '列表索引', snippet: '入 ${1:列表} ${2:索引}' },
            { label: '长', detail: '列表长度', snippet: '长 ${1:列表}' },
            { label: '长度', detail: '长度', snippet: '长度 ${1:序列}' },
            { label: '添', detail: '添加元素', snippet: '添 ${1:列表} ${2:元素}' },
            { label: '连', detail: '连接列表', snippet: '连 ${1:列表1} ${2:列表2}' },
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
            { label: '潜', detail: '延迟计算', snippet: '潜 ${1:表达式}' },
            
            // 输入输出
            { label: '印', detail: '打印输出', snippet: '印 ${1:值}。' },
            { label: '读', detail: '读取输入', snippet: '读' },
            { label: '写', detail: '写入输出', snippet: '写 ${1:值}' },
            { label: '行', detail: '换行', snippet: '行' },
            
            // 字典操作
            { label: '典', detail: '创建字典', snippet: '典 ${1:键1} ${2:值1} ${3:键2} ${4:值2}' },
            { label: '键', detail: '获取键', snippet: '键 ${1:字典}' },
            { label: '值', detail: '获取值', snippet: '值 ${1:字典}' },
            { label: '项', detail: '获取键值对', snippet: '项 ${1:字典}' },
            { label: '删键', detail: '删除键', snippet: '删键 ${1:字典} ${2:键}' },
            { label: '含', detail: '包含键', snippet: '含 ${1:字典} ${2:键}' },
            
            // 字符串操作
            { label: '连接', detail: '连接字符串', snippet: '连接 ${1:a} ${2:b}' },
            { label: '分割', detail: '分割字符串', snippet: '分割 ${1:字符串} ${2:分隔符}' },
            { label: '替换', detail: '替换字符串', snippet: '替换 ${1:字符串} ${2:旧} ${3:新}' },
            { label: '截取', detail: '截取子串', snippet: '截取 ${1:字符串} ${2:开始} ${3:结束}' },
            { label: '小写', detail: '转小写', snippet: '小写 ${1:字符串}' },
            { label: '大写', detail: '转大写', snippet: '大写 ${1:字符串}' },
            { label: '查找', detail: '查找子串', snippet: '查找 ${1:字符串} ${2:子串}' },
            { label: '包含', detail: '包含子串', snippet: '包含 ${1:字符串} ${2:子串}' },
            { label: '去空', detail: '去空格', snippet: '去空 ${1:字符串}' },
            { label: '开头是', detail: '开头匹配', snippet: '开头是 ${1:字符串} ${2:前缀}' },
            { label: '结尾是', detail: '结尾匹配', snippet: '结尾是 ${1:字符串} ${2:后缀}' },
            
            // 数学函数
            { label: '正弦', detail: '正弦函数', snippet: '正弦 ${1:x}' },
            { label: '余弦', detail: '余弦函数', snippet: '余弦 ${1:x}' },
            { label: '正切', detail: '正切函数', snippet: '正切 ${1:x}' },
            { label: '反正弦', detail: '反正弦', snippet: '反正弦 ${1:x}' },
            { label: '反余弦', detail: '反余弦', snippet: '反余弦 ${1:x}' },
            { label: '反正切', detail: '反正切', snippet: '反正切 ${1:x}' },
            { label: '指数', detail: '指数函数', snippet: '指数 ${1:x}' },
            { label: '对数', detail: '自然对数', snippet: '对数 ${1:x}' },
            { label: '对数10', detail: '常用对数', snippet: '对数10 ${1:x}' },
            { label: '开方', detail: '平方根', snippet: '开方 ${1:x}' },
            { label: '取整', detail: '向下取整', snippet: '取整 ${1:x}' },
            { label: '进位', detail: '向上取整', snippet: '进位 ${1:x}' },
            { label: '四舍五入', detail: '四舍五入', snippet: '四舍五入 ${1:x}' },
            
            // 随机数
            { label: '随机', detail: '随机数 [0,1)', snippet: '随机' },
            { label: '随机整数', detail: '随机整数', snippet: '随机整数 ${1:最小值} ${2:最大值}' },
            
            // 常量
            { label: '圆周率', detail: 'π ≈ 3.14159' },
            { label: '自然常数', detail: 'e ≈ 2.71828' },
            
            // 时间函数
            { label: '当前时间', detail: '当前时间戳', snippet: '当前时间' },
            { label: '日期', detail: '当前日期', snippet: '日期' },
            { label: '时间', detail: '当前时间', snippet: '时间' },
            { label: '日期时间', detail: '当前日期时间', snippet: '日期时间' },
            { label: '格式化时间', detail: '格式化时间', snippet: '格式化时间 ${1:格式}' },
            { label: '睡眠', detail: '暂停执行', snippet: '睡眠 ${1:毫秒}' },
            
            // 文件操作
            { label: '读文件', detail: '读取文件', snippet: '读文件 \"${1:文件名}\"' },
            { label: '写文件', detail: '写入文件', snippet: '写文件 \"${1:文件名}\" ${2:内容}' },
            { label: '追加文件', detail: '追加文件', snippet: '追加文件 \"${1:文件名}\" ${2:内容}' },
            { label: '存在', detail: '文件存在', snippet: '存在 \"${1:路径}\"' },
            { label: '是文件', detail: '是文件', snippet: '是文件 \"${1:路径}\"' },
            { label: '是目录', detail: '是目录', snippet: '是目录 \"${1:路径}\"' },
            { label: '列目录', detail: '列出目录', snippet: '列目录 \"${1:路径}\"' },
            { label: '建目录', detail: '创建目录', snippet: '建目录 \"${1:路径}\"' },
            { label: '删文件', detail: '删除文件', snippet: '删文件 \"${1:路径}\"' },
            { label: '删目录', detail: '删除目录', snippet: '删目录 \"${1:路径}\"' },
            { label: '当前目录', detail: '当前目录', snippet: '当前目录' },
            { label: '文件名', detail: '获取文件名', snippet: '文件名 \"${1:路径}\"' },
            { label: '目录名', detail: '获取目录名', snippet: '目录名 \"${1:路径}\"' },
            { label: '扩展名', detail: '获取扩展名', snippet: '扩展名 \"${1:路径}\"' },
            
            // 类型检查
            { label: '是数', detail: '是数字', snippet: '是数 ${1:值}' },
            { label: '是串', detail: '是字符串', snippet: '是串 ${1:值}' },
            { label: '是表', detail: '是列表', snippet: '是表 ${1:值}' },
            { label: '是函', detail: '是函数', snippet: '是函 ${1:值}' },
            { label: '是真', detail: '是真', snippet: '是真 ${1:值}' },
            { label: '是空', detail: '是空', snippet: '是空 ${1:值}' },
            { label: '类型', detail: '获取类型', snippet: '类型 ${1:值}' },
            
            // 范围操作
            { label: '范围', detail: '生成范围', snippet: '范围 ${1:开始} ${2:结束}' }
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
    
    private initStandardLibrary() {
        // JSON模块
        const jsonModule = [
            { label: '解析', detail: '解析JSON字符串', snippet: 'JSON.解析 ${1:字符串}' },
            { label: '生成', detail: '生成JSON字符串', snippet: 'JSON.生成 ${1:对象}' },
            { label: '格式化', detail: '格式化JSON', snippet: 'JSON.格式化 ${1:对象} ${2:缩进}' },
            { label: '从文件读取', detail: '从文件读取JSON', snippet: 'JSON.从文件读取 \"${1:文件名}\"' },
            { label: '写入文件', detail: '写入JSON到文件', snippet: 'JSON.写入文件 ${1:对象} \"${2:文件名}\"' },
            { label: '验证', detail: '验证JSON格式', snippet: 'JSON.验证 ${1:字符串}' },
            { label: '美化', detail: '美化JSON', snippet: 'JSON.美化 ${1:字符串}' },
            { label: '压缩', detail: '压缩JSON', snippet: 'JSON.压缩 ${1:字符串}' },
            { label: '深拷贝', detail: '深拷贝对象', snippet: 'JSON.深拷贝 ${1:对象}' },
            { label: '合并', detail: '合并字典', snippet: 'JSON.合并 ${1:字典1} ${2:字典2}' },
            { label: '提取路径', detail: 'JSONPath提取', snippet: 'JSON.提取路径 ${1:对象} \"${2:路径}\"' }
        ];
        
        // 正则模块
        const regexModule = [
            { label: '匹配', detail: '匹配开头', snippet: '正则.匹配 \"${1:模式}\" ${2:字符串}' },
            { label: '搜索', detail: '搜索', snippet: '正则.搜索 \"${1:模式}\" ${2:字符串}' },
            { label: '查找全部', detail: '查找全部', snippet: '正则.查找全部 \"${1:模式}\" ${2:字符串}' },
            { label: '替换', detail: '替换', snippet: '正则.替换 \"${1:模式}\" \"${2:替换}\" ${3:字符串}' },
            { label: '替换一次', detail: '替换一次', snippet: '正则.替换一次 \"${1:模式}\" \"${2:替换}\" ${3:字符串}' },
            { label: '分割', detail: '分割', snippet: '正则.分割 \"${1:模式}\" ${2:字符串}' },
            { label: '分割最大', detail: '分割指定次数', snippet: '正则.分割最大 \"${1:模式}\" ${2:字符串} ${3:次数}' },
            { label: '分组', detail: '获取分组', snippet: '正则.分组 \"${1:模式}\" ${2:字符串}' },
            { label: '命名分组', detail: '获取命名分组', snippet: '正则.命名分组 \"${1:模式}\" ${2:字符串}' },
            { label: '转义', detail: '转义特殊字符', snippet: '正则.转义 ${1:字符串}' },
            { label: '全匹配', detail: '完全匹配', snippet: '正则.全匹配 \"${1:模式}\" ${2:字符串}' },
            { label: '查找迭代', detail: '迭代查找', snippet: '正则.查找迭代 \"${1:模式}\" ${2:字符串}' }
        ];
        
        // 日期模块
        const dateModule = [
            { label: '当前时间戳', detail: '当前时间戳', snippet: '日期.当前时间戳' },
            { label: '当前时间', detail: '当前时间', snippet: '日期.当前时间' },
            { label: '当前日期', detail: '当前日期', snippet: '日期.当前日期' },
            { label: '格式化', detail: '格式化日期', snippet: '日期.格式化 ${1:日期} \"${2:格式}\"' },
            { label: '解析', detail: '解析日期', snippet: '日期.解析 ${1:字符串} \"${2:格式}\"' },
            { label: '日期差', detail: '计算日期差', snippet: '日期.日期差 ${1:日期1} ${2:日期2}' },
            { label: '加天数', detail: '加天数', snippet: '日期.加天数 ${1:日期} ${2:天数}' },
            { label: '加小时', detail: '加小时', snippet: '日期.加小时 ${1:日期} ${2:小时}' },
            { label: '加分钟', detail: '加分钟', snippet: '日期.加分钟 ${1:日期} ${2:分钟}' },
            { label: '加秒', detail: '加秒', snippet: '日期.加秒 ${1:日期} ${2:秒}' },
            { label: '年', detail: '获取年', snippet: '日期.年 ${1:日期}' },
            { label: '月', detail: '获取月', snippet: '日期.月 ${1:日期}' },
            { label: '日', detail: '获取日', snippet: '日期.日 ${1:日期}' },
            { label: '时', detail: '获取时', snippet: '日期.时 ${1:日期}' },
            { label: '分', detail: '获取分', snippet: '日期.分 ${1:日期}' },
            { label: '秒', detail: '获取秒', snippet: '日期.秒 ${1:日期}' },
            { label: '是闰年', detail: '是闰年', snippet: '日期.是闰年 ${1:年}' },
            { label: '星期几', detail: '星期几', snippet: '日期.星期几 ${1:日期}' }
        ];
        
        // 网络模块
        const networkModule = [
            { label: '获取', detail: 'GET请求', snippet: '网络.获取 \"${1:URL}\"' },
            { label: '获取二进制', detail: '获取二进制内容', snippet: '网络.获取二进制 \"${1:URL}\"' },
            { label: '获取状态码', detail: '获取状态码', snippet: '网络.获取状态码 \"${1:URL}\"' },
            { label: '获取响应头', detail: '获取响应头', snippet: '网络.获取响应头 \"${1:URL}\"' },
            { label: '发布', detail: 'POST请求', snippet: '网络.发布 \"${1:URL}\" ${2:数据}' },
            { label: '发布JSON', detail: 'POST JSON', snippet: '网络.发布JSON \"${1:URL}\" ${2:对象}' },
            { label: '发布表单', detail: 'POST表单', snippet: '网络.发布表单 \"${1:URL}\" ${2:数据}' },
            { label: '下载', detail: '下载文件', snippet: '网络.下载 \"${1:URL}\" \"${2:文件名}\"' },
            { label: '下载进度', detail: '下载带进度', snippet: '网络.下载进度 \"${1:URL}\" \"${2:文件名}\"' },
            { label: '编码', detail: 'URL编码', snippet: '网络.编码 ${1:字符串}' },
            { label: '解码', detail: 'URL解码', snippet: '网络.解码 ${1:字符串}' },
            { label: '设置代理', detail: '设置代理', snippet: '网络.设置代理 \"${1:代理URL}\"' },
            { label: '获取Cookie', detail: '获取Cookie', snippet: '网络.获取Cookie \"${1:URL}\"' }
        ];
        
        // 加密模块
        const cryptoModule = [
            { label: 'MD5', detail: 'MD5哈希', snippet: '加密.MD5 ${1:数据}' },
            { label: 'SHA1', detail: 'SHA1哈希', snippet: '加密.SHA1 ${1:数据}' },
            { label: 'SHA256', detail: 'SHA256哈希', snippet: '加密.SHA256 ${1:数据}' },
            { label: 'SHA512', detail: 'SHA512哈希', snippet: '加密.SHA512 ${1:数据}' },
            { label: '消息摘要', detail: '消息摘要', snippet: '加密.消息摘要 ${1:数据} \"${2:算法}\"' },
            { label: 'Base64编码', detail: 'Base64编码', snippet: '加密.Base64编码 ${1:数据}' },
            { label: 'Base64解码', detail: 'Base64解码', snippet: '加密.Base64解码 ${1:字符串}' },
            { label: 'Base64URL编码', detail: 'Base64URL编码', snippet: '加密.Base64URL编码 ${1:数据}' },
            { label: 'Base64URL解码', detail: 'Base64URL解码', snippet: '加密.Base64URL解码 ${1:字符串}' },
            { label: 'URL编码', detail: 'URL编码', snippet: '加密.URL编码 ${1:字符串}' },
            { label: 'URL解码', detail: 'URL解码', snippet: '加密.URL解码 ${1:字符串}' },
            { label: 'HMAC', detail: 'HMAC签名', snippet: '加密.HMAC ${1:数据} \"${2:密钥}\" \"${3:算法}\"' },
            { label: 'HMACSHA256', detail: 'HMAC-SHA256', snippet: '加密.HMACSHA256 ${1:数据} \"${2:密钥}\"' },
            { label: '生成随机字符串', detail: '随机字符串', snippet: '加密.生成随机字符串 ${1:长度}' },
            { label: '生成UUID', detail: '生成UUID', snippet: '加密.生成UUID ${1:版本}' },
            { label: 'UUID1', detail: 'UUID v1', snippet: '加密.UUID1' },
            { label: 'UUID4', detail: 'UUID v4', snippet: '加密.UUID4' },
            { label: 'CRC32', detail: 'CRC32校验', snippet: '加密.CRC32 ${1:数据}' },
            { label: '校验和', detail: '简单校验和', snippet: '加密.校验和 ${1:数据}' },
            { label: '安全比较', detail: '安全比较', snippet: '加密.安全比较 ${1:a} ${2:b}' }
        ];
        
        // 数据库模块
        const databaseModule = [
            { label: '连接SQLite', detail: '连接SQLite', snippet: '数据库.连接SQLite \"${1:数据库路径}\"' },
            { label: '创建表', detail: '创建表', snippet: '数据库.创建表 ${1:连接} \"${2:SQL}\"' },
            { label: '查询', detail: '查询', snippet: '数据库.查询 ${1:连接} \"${2:SQL}\" ${3:参数}' },
            { label: '查询单行', detail: '查询单行', snippet: '数据库.查询单行 ${1:连接} \"${2:SQL}\" ${3:参数}' },
            { label: '查询单个值', detail: '查询单个值', snippet: '数据库.查询单个值 ${1:连接} \"${2:SQL}\" ${3:参数}' },
            { label: '执行', detail: '执行SQL', snippet: '数据库.执行 ${1:连接} \"${2:SQL}\" ${3:参数}' },
            { label: '批量执行', detail: '批量执行', snippet: '数据库.批量执行 ${1:连接} \"${2:SQL}\" ${3:参数列表}' },
            { label: '关闭连接', detail: '关闭连接', snippet: '数据库.关闭连接 ${1:连接}' },
            { label: '开始事务', detail: '开始事务', snippet: '数据库.开始事务 ${1:连接}' },
            { label: '提交事务', detail: '提交事务', snippet: '数据库.提交事务 ${1:连接}' },
            { label: '回滚事务', detail: '回滚事务', snippet: '数据库.回滚事务 ${1:连接}' },
            { label: '获取表列表', detail: '获取表列表', snippet: '数据库.获取表列表 ${1:连接}' },
            { label: '获取表结构', detail: '获取表结构', snippet: '数据库.获取表结构 ${1:连接} \"${2:表名}\"' },
            { label: '插入', detail: '插入数据', snippet: '数据库.插入 ${1:连接} \"${2:表名}\" ${3:数据}' },
            { label: '更新', detail: '更新数据', snippet: '数据库.更新 ${1:连接} \"${2:表名}\" ${3:数据} \"${4:条件}\" ${5:参数}' },
            { label: '删除', detail: '删除数据', snippet: '数据库.删除 ${1:连接} \"${2:表名}\" \"${3:条件}\" ${4:参数}' },
            { label: '计数', detail: '计数', snippet: '数据库.计数 ${1:连接} \"${2:表名}\" ${3:条件} ${4:参数}' },
            { label: '存在', detail: '存在检查', snippet: '数据库.存在 ${1:连接} \"${2:表名}\" \"${3:条件}\" ${4:参数}' },
            { label: '创建索引', detail: '创建索引', snippet: '数据库.创建索引 ${1:连接} \"${2:索引名}\" \"${3:表名}\" \"${4:列名}\"' },
            { label: '删除索引', detail: '删除索引', snippet: '数据库.删除索引 ${1:连接} \"${2:索引名}\"' },
            { label: '备份数据库', detail: '备份数据库', snippet: '数据库.备份数据库 ${1:连接} \"${2:备份路径}\"' }
        ];
        
        this.standardLibrary.set('JSON', jsonModule.map(this.createCompletionItem));
        this.standardLibrary.set('正则', regexModule.map(this.createCompletionItem));
        this.standardLibrary.set('日期', dateModule.map(this.createCompletionItem));
        this.standardLibrary.set('网络', networkModule.map(this.createCompletionItem));
        this.standardLibrary.set('加密', cryptoModule.map(this.createCompletionItem));
        this.standardLibrary.set('数据库', databaseModule.map(this.createCompletionItem));
    }
    
    private createCompletionItem = (item: any): vscode.CompletionItem => {
        const completionItem = new vscode.CompletionItem(item.label, vscode.CompletionItemKind.Method);
        completionItem.detail = item.detail;
        if (item.snippet) {
            completionItem.insertText = new vscode.SnippetString(item.snippet);
        }
        return completionItem;
    };
    
    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): vscode.ProviderResult<vscode.CompletionItem[] | vscode.CompletionList> {
        const line = document.lineAt(position);
        const lineText = line.text.substring(0, position.character);
        
        // 检查是否在成员访问后面（如 JSON.）
        const dotMatch = lineText.match(/([A-Za-z\u4e00-\u9fa5]+)\.$/);
        if (dotMatch) {
            const moduleName = dotMatch[1];
            const moduleItems = this.standardLibrary.get(moduleName);
            if (moduleItems) {
                return moduleItems;
            }
        }
        
        // 返回所有补全项
        return [...this.keywords, ...this.verbs];
    }
}
