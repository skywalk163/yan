def update_module_names():
    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/codegen.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加新模块到 module_names 集合
    new_modules = '''                '终端界面', 'curses', '数据库管理', 'dbm', 'MIME类型', 'mimetypes',
                'Python编译', 'py_compile', '文档生成', 'pydoc', '系统配置', 'sysconfig',
                '浏览器', 'webbrowser', 'XMLRPC客户端', 'xmlrpc.client', 'XMLRPC服务器', 'xmlrpc.server',
                '时区', 'zoneinfo', '邮件MIME', 'email.mime', '邮件标题', 'email.header',
                '邮件工具', 'email.utils', '邮件解析器', 'email.parser', '邮件策略', 'email.policy',
                '邮件消息', 'email.message', '邮件迭代器', 'email.iterators',
'''
    
    # 找到 module_names 的位置并添加新模块
    # 在 '属性列表', 'plistlib' 后面添加
    content = content.replace("                'SSL', 'ssl', 'XDR', 'xdrlib', '属性列表', 'plistlib'\n            }", 
                            "                'SSL', 'ssl', 'XDR', 'xdrlib', '属性列表', 'plistlib',\n" + new_modules + "            }")
    
    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/codegen.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已更新模块名称列表")

if __name__ == "__main__":
    update_module_names()
