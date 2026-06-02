import re

def add_more_modules():
    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/runtime.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加更多标准库导入
    additional_imports = '''
# 更多标准库扩展
import curses
import dbm
import mimetypes
import py_compile
import pydoc
import sysconfig
import webbrowser
import xmlrpc.client
import xmlrpc.server
import zoneinfo
import email.mime
import email.header
import email.utils
import email.parser
import email.policy
import email.message
import email.iterators
'''
    
    # 在 platform特定模块 之前插入新的导入
    content = content.replace('# 平台特定模块', additional_imports + '\n\n# 平台特定模块')
    
    # 添加新模块的中文名称映射
    additional_mappings = '''\n    # 终端界面
    env.update({"终端界面": curses, "curses": curses})

    # 数据库管理
    env.update({"数据库管理": dbm, "dbm": dbm})

    # MIME类型
    env.update({"MIME类型": mimetypes, "mimetypes": mimetypes})

    # Python编译
    env.update({"Python编译": py_compile, "py_compile": py_compile})

    # 文档生成
    env.update({"文档生成": pydoc, "pydoc": pydoc})

    # 系统配置
    env.update({"系统配置": sysconfig, "sysconfig": sysconfig})

    # 浏览器控制
    env.update({"浏览器": webbrowser, "webbrowser": webbrowser})

    # XML-RPC
    env.update({"XMLRPC客户端": xmlrpc.client, "xmlrpc.client": xmlrpc.client})
    env.update({"XMLRPC服务器": xmlrpc.server, "xmlrpc.server": xmlrpc.server})

    # 时区信息
    env.update({"时区": zoneinfo, "zoneinfo": zoneinfo})

    # 邮件扩展
    env.update({"邮件MIME": email.mime, "email.mime": email.mime})
    env.update({"邮件标题": email.header, "email.header": email.header})
    env.update({"邮件工具": email.utils, "email.utils": email.utils})
    env.update({"邮件解析器": email.parser, "email.parser": email.parser})
    env.update({"邮件策略": email.policy, "email.policy": email.policy})
    env.update({"邮件消息": email.message, "email.message": email.message})
    env.update({"邮件迭代器": email.iterators, "email.iterators": email.iterators})

'''
    
    # 在 return env 之前添加新的模块映射
    content = content.replace('    return env', additional_mappings + '    return env')
    
    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/runtime.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已添加更多标准库模块")

if __name__ == "__main__":
    add_more_modules()
