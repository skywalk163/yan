#!/usr/bin/env python3
"""
言语言 - Python 转译器
"""

import sys
from typing import Any, Optional, Dict
from lexer import Lexer, LexerError
from parser import Parser, ParserError, process_adverbs, add_global_user_verb, _global_user_verbs
from codegen import PythonCodeGen, CodeGenError
from runtime import (
    _add, _sub, _mul, _div, _mod, _pow, _abs, _neg,
    _gt, _lt, _eq, _ne,
    _and, _or, _not,
    _list, _head, _tail, _nth, _len, _append, _concat, _contains, _empty,
    _range,
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
)

# 全局环境，用于交互模式
_global_env: Optional[Dict[str, Any]] = None


def create_env() -> Dict[str, Any]:
    """创建新的执行环境"""
    env = globals().copy()
    return env


def run(source: str, debug: bool = False, env: Optional[Dict[str, Any]] = None, use_global_verbs: bool = False) -> Any:
    """运行言语言代码
    
    Args:
        source: 言语言源代码
        debug: 是否显示调试信息
        env: 执行环境（可选，用于保持全局变量）
        use_global_verbs: 是否使用全局用户动词集合（交互模式）
    
    Returns:
        执行结果
    """
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
        parser = Parser(use_global_verbs=use_global_verbs)
        ast = parser.parse(tokens)
        ast = process_adverbs(ast)
        if debug:
            print("=== AST ===")
            print(f"  {ast}")
            print()

        # 3. 生成 Python 代码
        codegen = PythonCodeGen()
        py_code = codegen.generate(ast)
        if debug:
            print("=== Python ===")
            print(py_code)
            print()

        # 4. 执行
        if env is None:
            env = create_env()

        # 对于单表达式，使用 eval
        if '\n' not in py_code:
            try:
                result = eval(py_code, env)
                return result
            except SyntaxError:
                pass

        # 多语句：使用 exec，使用同一个命名空间以支持递归
        try:
            # 使用同一个字典作为 globals 和 locals，这样递归函数可以找到自己
            exec(py_code, env, env)
            # 检查是否有 _result 变量（由代码生成器设置）
            if '_result' in env:
                return env['_result']
            # 尝试获取最后一个表达式的结果
            lines = py_code.strip().split('\n')
            if lines:
                last_line = lines[-1].strip()
                # 如果最后一行是表达式（不是赋值，不是 print 调用），计算它
                if ('=' not in last_line or last_line.count('=') == last_line.count('==')) and not last_line.startswith('print'):
                    try:
                        result = eval(last_line, env)
                        return result
                    except:
                        pass
            return None
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
    except Exception as e:
        print(f"运行时错误: {e}", file=sys.stderr)
        return None


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

    filename = sys.argv[1]
    debug = '--debug' in sys.argv

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

    result = run(source, debug=debug)
    if result is not None:
        print(result)


if __name__ == "__main__":
    main()
