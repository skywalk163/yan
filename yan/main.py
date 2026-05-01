#!/usr/bin/env python3
"""
言语言 - Python 转译器
"""

import sys
from typing import Any
from lexer import Lexer, LexerError
from parser import Parser, ParserError, process_adverbs
from codegen import PythonCodeGen, CodeGenError
from runtime import (
    _add, _sub, _mul, _div, _mod, _pow, _abs, _neg,
    _gt, _lt, _eq, _ne,
    _and, _or, _not,
    _list, _head, _tail, _nth, _len, _append, _concat, _contains, _empty,
    _range,
    _map, _filter, _reduce,
    BUILTINS
)


def run(source: str, debug: bool = False) -> Any:
    """运行言语言代码"""
    try:
        # 1. 词法分析
        lexer = Lexer()
        tokens = lexer.tokenize(source)
        if debug:
            print("=== Tokens ===")
            for tok in tokens:
                print(f"  {tok}")
            print()

        # 2. 语法分析
        parser = Parser()
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
        env = globals().copy()

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


def repl():
    """交互式环境"""
    print("言语言 v0.1")
    print("输入代码，以空行结束。输入 'quit' 或 '退出' 退出。")
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
            result = run(source, debug=False)
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
