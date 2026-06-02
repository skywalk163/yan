#!/usr/bin/env python3
"""
言语言 - Python 转译器
"""

import sys
from pathlib import Path
from typing import Any, Optional, Dict, List
from lexer import Lexer, LexerError
from parser import Parser, ParserError, process_adverbs, add_global_user_verb, _global_user_verbs
from codegen import PythonCodeGen, CodeGenError
from module_system import ModuleSystem, ModuleError, ImportNode
from runtime import (
    _add, _sub, _mul, _div, _mod, _pow, _abs, _neg,
    _gt, _gte, _lt, _lte, _eq, _ne,
    _and, _or, _not,
    _list, _head, _tail, _nth, _set_nth, _len, _append, _concat, _contains, _empty,
    _range, _eval,
    _map, _filter, _reduce,
    BUILTINS, ALL_BUILTINS,
    # 数学库
    _sin, _cos, _tan, _asin, _acos, _atan, _exp, _log, _log10, _sqrt,
    _floor, _ceil, _round, _random, _randint, _pi, _e,
    # 字符串库
    _strlen, _strcat, _strsplit, _strreplace, _strslice, _strlower, _strupper,
    _strfind, _strcontains, _strstrip, _strstartswith, _strendswith,
    # 文件库
    _readfile, _writefile, _appendfile, _fileexists, _isfile, _isdir,
    _listdir, _mkdir, _removefile, _removedir, _getcwd, _basename, _dirname, _extname,
    # 时间库
    _now, _date, _time, _datetime, _strftime, _sleep,
    # 类型检查
    _isnum, _isstr, _islist, _isfunc, _isbool, _isnone, _typeof,
    # 字典操作
    _dict, _keys, _values, _items, _get, _delkey,
)

# 全局环境，用于交互模式（延迟初始化，避免启动时占用内存）
_global_env: Optional[Dict[str, Any]] = None

# 模块系统实例（不使用全局单例，每次需要时创建或使用上下文管理）
# 注意：使用全局单例会导致内存无限增长，改为按需创建
_module_system: Optional[ModuleSystem] = None


def _get_module_system() -> ModuleSystem:
    """获取或创建模块系统实例"""
    global _module_system
    if _module_system is None:
        _module_system = ModuleSystem()
    return _module_system


def _reset_module_system():
    """重置模块系统，释放内存"""
    global _module_system
    if _module_system is not None:
        _module_system.clear_cache()
        _module_system = None


def _reset_global_env():
    """重置全局环境，释放内存"""
    global _global_env
    _global_env = None


def create_env() -> Dict[str, Any]:
    """创建新的执行环境"""
    env = {}
    
    # 添加中文动词名称
    for name, (func, arity) in ALL_BUILTINS.items():
        env[name] = func
    
    # 添加内部函数引用
    env.update({
        '_add': _add,
        '_sub': _sub,
        '_mul': _mul,
        '_div': _div,
        '_mod': _mod,
        '_pow': _pow,
        '_abs': _abs,
        '_neg': _neg,
        '_gt': _gt,
        '_gte': _gte,
        '_lt': _lt,
        '_lte': _lte,
        '_eq': _eq,
        '_ne': _ne,
        '_and': _and,
        '_or': _or,
        '_not': _not,
        '_list': _list,
        '_head': _head,
        '_tail': _tail,
        '_nth': _nth,
        '_set_nth': _set_nth,
        '_len': _len,
        '_append': _append,
        '_concat': _concat,
        '_contains': _contains,
        '_empty': _empty,
        '_range': _range,
        '_eval': _eval,
        '_map': _map,
        '_filter': _filter,
        '_reduce': _reduce,
        '_sin': _sin,
        '_cos': _cos,
        '_tan': _tan,
        '_asin': _asin,
        '_acos': _acos,
        '_atan': _atan,
        '_exp': _exp,
        '_log': _log,
        '_log10': _log10,
        '_sqrt': _sqrt,
        '_floor': _floor,
        '_ceil': _ceil,
        '_round': _round,
        '_random': _random,
        '_randint': _randint,
        '_pi': _pi,
        '_e': _e,
        '_strlen': _strlen,
        '_strcat': _strcat,
        '_strsplit': _strsplit,
        '_strreplace': _strreplace,
        '_strslice': _strslice,
        '_strlower': _strlower,
        '_strupper': _strupper,
        '_strfind': _strfind,
        '_strcontains': _strcontains,
        '_strstrip': _strstrip,
        '_strstartswith': _strstartswith,
        '_strendswith': _strendswith,
        '_readfile': _readfile,
        '_writefile': _writefile,
        '_appendfile': _appendfile,
        '_fileexists': _fileexists,
        '_isfile': _isfile,
        '_isdir': _isdir,
        '_listdir': _listdir,
        '_mkdir': _mkdir,
        '_removefile': _removefile,
        '_removedir': _removedir,
        '_getcwd': _getcwd,
        '_basename': _basename,
        '_dirname': _dirname,
        '_extname': _extname,
        '_now': _now,
        '_date': _date,
        '_time': _time,
        '_datetime': _datetime,
        '_strftime': _strftime,
        '_sleep': _sleep,
        '_isnum': _isnum,
        '_isstr': _isstr,
        '_islist': _islist,
        '_isfunc': _isfunc,
        '_isbool': _isbool,
        '_isnone': _isnone,
        '_typeof': _typeof,
        '_dict': _dict,
        '_keys': _keys,
        '_values': _values,
        '_items': _items,
        '_get': _get,
        '_delkey': _delkey,
        'BUILTINS': BUILTINS,
        'ALL_BUILTINS': ALL_BUILTINS,
    })
    import math
    env['math'] = math
    import random
    env['random'] = random
    import time
    env['time'] = time
    import os
    env['os'] = os
    return env


def _process_imports(statements: List, current_file: Optional[Path] = None, visited_modules: Optional[set] = None, module_system: Optional[ModuleSystem] = None) -> List:
    """递归处理导入语句，检测循环依赖"""
    if visited_modules is None:
        visited_modules = set()
    
    if module_system is None:
        module_system = _get_module_system()
    
    processed_statements = []
    
    for stmt in statements:
        if isinstance(stmt, ImportNode):
            # 检查循环依赖
            module_path = stmt.path
            resolved_path = module_system.resolve_module(module_path, current_file)
            
            if resolved_path:
                module_key = str(resolved_path.resolve())
                if module_key in visited_modules:
                    raise ModuleError(f"循环依赖检测：{module_path} 已在导入链中", module_path)
                
                visited_modules.add(module_key)
                
                # 加载模块
                try:
                    module = module_system.load_module(module_path, current_file)
                    
                    # 递归处理模块的导入
                    if module.source:
                        # 解析模块内容
                        lexer = Lexer()
                        tokens = lexer.tokenize(module.source)
                        parser = Parser()
                        module_ast = parser.parse(tokens, module.source)
                        
                        # 递归处理模块的导入
                        if hasattr(module_ast, 'statements'):
                            processed_imports = _process_imports(
                                module_ast.statements, 
                                module.path, 
                                visited_modules.copy(),
                                module_system
                            )
                            processed_statements.extend(processed_imports)
                    
                    visited_modules.remove(module_key)
                except ModuleError as e:
                    raise e
        
        processed_statements.append(stmt)
    
    return processed_statements


def run(source: str, debug: bool = False, env: Optional[Dict[str, Any]] = None, use_global_verbs: bool = False, current_file: Optional[Path] = None, clear_cache: bool = True, syntax_version: int = 2) -> Any:
    """运行言语言代码
    
    Args:
        source: 言语言源代码
        debug: 是否显示调试信息
        env: 执行环境（可选，用于保持全局变量）
        use_global_verbs: 是否使用全局用户动词集合（交互模式）
        current_file: 当前文件路径（用于模块路径解析）
        clear_cache: 是否在执行完成后清理缓存（避免内存泄漏）
        syntax_version: 语法版本（1 或 2，默认为 2）
    
    Returns:
        执行结果
    """
    # 为单次执行创建独立的模块系统，避免全局污染
    local_module_system = ModuleSystem()
    result = None
    
    try:
        # 1. 词法分析
        user_words = _global_user_verbs if use_global_verbs else None
        lexer = Lexer(user_words=user_words)
        tokens = lexer.tokenize(source)
        if debug:
            print("=== Tokens ===")
            for tok in tokens:
                print(f"  {tok}")
            print()

        # 2. 语法分析
        parser = Parser(use_global_verbs=use_global_verbs, syntax_version=syntax_version)
        ast = parser.parse(tokens)
        ast = process_adverbs(ast)
        if debug:
            print("=== AST ===")
            print(f"  {ast}")
            print()

        # 3. 处理模块导入（包括循环依赖检测）
        if hasattr(ast, 'statements'):
            try:
                ast.statements = _process_imports(ast.statements, current_file, module_system=local_module_system)
            except ModuleError as e:
                print(f"模块错误: {e}", file=sys.stderr)
                return None

        # 4. 生成 Python 代码
        codegen = PythonCodeGen()
        py_code = codegen.generate(ast)
        if debug:
            print("=== Python ===")
            print(py_code)
            print()

        # 5. 执行
        if env is None:
            env = create_env()

        # 对于单表达式，使用 eval
        if '\n' not in py_code:
            try:
                result = eval(py_code, env)
            except SyntaxError:
                pass

        # 多语句：使用 exec，使用同一个命名空间以支持递归
        try:
            # 使用同一个字典作为 globals 和 locals，这样递归函数可以找到自己
            exec(py_code, env, env)
            # 检查是否有 _result 变量（由代码生成器设置）
            if '_result' in env:
                result = env['_result']
            # 尝试获取最后一个表达式的结果
            # 但不要重新执行函数调用
            lines = py_code.strip().split('\n')
            if lines and result is None:
                last_line = lines[-1].strip()
                # 如果最后一行是表达式（不是赋值，不是 print 调用，不是函数调用），计算它
                if ('=' not in last_line or last_line.count('=') == last_line.count('==')) and not last_line.startswith('print') and '(' not in last_line:
                    try:
                        result = eval(last_line, env)
                    except:
                        pass
        except SyntaxError as e:
            print(f"Python 语法错误: {e}", file=sys.stderr)
            print(f"生成的代码:\n{py_code}", file=sys.stderr)
            return None

    except LexerError as e:
        print(f"词法错误: {e}", file=sys.stderr)
        return None
    except ParserError as e:
        print(f"语法错误: {e}", file=sys.stderr)
        return None
    except CodeGenError as e:
        print(f"代码生成错误: {e}", file=sys.stderr)
        return None
    except ModuleError as e:
        print(f"模块错误: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"运行时错误: {e}", file=sys.stderr)
        return None
    finally:
        # 清理缓存避免内存泄漏
        if clear_cache:
            local_module_system.clear_cache()
    
    return result


def run_repl(source: str, debug: bool = False) -> Any:
    """在交互模式下运行（保持全局变量和用户定义的函数）"""
    global _global_env
    
    if _global_env is None:
        _global_env = create_env()
    
    return run(source, debug=debug, env=_global_env, use_global_verbs=True)


def repl():
    """交互式环境"""
    global _global_env
    
    print("言语言 v0.2")
    print("输入代码，以空行结束。输入 'quit' 或 '退出' 退出。")
    print("提示：变量和函数会保持在当前会话中。")
    print()

    while True:
        try:
            print("言> ", end="", flush=True)
            lines = []
            while True:
                try:
                    line = input()
                    if line.lower() in ('quit', '退出'):
                        print("再见！")
                        return
                    if not line:
                        break
                    lines.append(line)
                except EOFError:
                    print("\n再见！")
                    return

            if not lines:
                continue

            source = ''.join(lines)
            result = run_repl(source, debug=False)
            if result is not None:
                print(f"  => {result}")

        except KeyboardInterrupt:
            print("\n再见！")
            return


def main():
    """主入口"""
    if len(sys.argv) < 2:
        repl()
        return

    # 检查是否是从stdin读取代码（Playground使用）
    if sys.argv[1] == "-c" or sys.argv[1] == "--code":
        try:
            # 使用 utf-8 编码读取 stdin，确保正确处理中文
            source = sys.stdin.read()
            if not source:
                # 尝试以二进制方式读取并解码
                import io
                source = sys.stdin.buffer.read().decode('utf-8')
            if source.strip():
                result = run(source, debug=False, use_global_verbs=False, clear_cache=True)
                if result is not None:
                    print(result)
            return
        except Exception as e:
            print(f"执行错误: {e}", file=sys.stderr)
            return

    # 检查是否是包管理器命令
    if sys.argv[1] == "包":
        from yan_package_manager import PackageManager
        
        pm = PackageManager()
        command = sys.argv[2] if len(sys.argv) > 2 else ""
        args = sys.argv[3:]
        
        if command == "安装":
            if not args:
                print("错误：请指定包名")
                return
            package_name = args[0]
            version = args[1] if len(args) > 1 else None
            pm.install(package_name, version)
        elif command == "卸载":
            if not args:
                print("错误：请指定包名")
                return
            pm.uninstall(args[0])
        elif command == "列表":
            pm.list_packages()
        elif command == "搜索":
            if not args:
                print("错误：请指定搜索关键词")
                return
            pm.search(args[0])
        elif command == "初始化":
            project_name = args[0] if args else None
            pm.init(project_name)
        elif command == "链接":
            if not args:
                print("错误：请指定本地路径")
                return
            pm.link(args[0])
        elif command == "发布":
            pm.publish()
        elif command == "帮助" or not command:
            pm.help()
        else:
            print(f"未知命令: {command}")
            print("使用 'yan 包 帮助' 查看所有命令")
        return

    filename = sys.argv[1]
    debug = '--debug' in sys.argv
    
    # 检查语法版本参数
    syntax_version = 2
    if '--v1' in sys.argv:
        syntax_version = 1
    elif '--v2' in sys.argv:
        syntax_version = 2
    
    # 从 --syntax 参数读取版本
    for i, arg in enumerate(sys.argv):
        if arg == '--syntax' and i + 1 < len(sys.argv):
            syntax_version = int(sys.argv[i + 1])
            break

    # 检查是否是 .ymd 文件
    if filename.endswith('.ymd'):
        from md_executor import run_ymd
        # 自动生成输出文件名
        output_file = filename[:-4] + '_output.md'
        run_ymd(filename, output_file, debug=debug)
        return

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"文件不存在: {filename}", file=sys.stderr)
        return

    # 传递当前文件路径用于模块路径解析
    current_file = Path(filename)
    result = run(source, debug=debug, use_global_verbs=True, current_file=current_file, syntax_version=syntax_version)
    if result is not None:
        print(result)


if __name__ == "__main__":
    main()
