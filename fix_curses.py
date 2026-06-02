def fix_curses_import():
    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/runtime.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 将直接导入改为 try-except
    old_imports = '''# 更多标准库扩展
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
import email.iterators'''
    
    new_imports = '''# 更多标准库扩展
try:
    import curses
except ImportError:
    curses = None

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
import email.iterators'''
    
    content = content.replace(old_imports, new_imports)
    
    # 修改模块映射部分，添加条件导入
    old_mapping = '''    # 终端界面
    env.update({"终端界面": curses, "curses": curses})

    # 数据库管理'''
    
    new_mapping = '''    # 终端界面（平台特定）
    if curses is not None:
        env.update({"终端界面": curses, "curses": curses})

    # 数据库管理'''
    
    content = content.replace(old_mapping, new_mapping)
    
    with open('g:/dumategithub/newlisp/.worktrees/v2-syntax/yan/v2/runtime.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已修复 curses 导入问题")

if __name__ == "__main__":
    fix_curses_import()
