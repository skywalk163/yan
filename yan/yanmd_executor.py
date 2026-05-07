"""
言语言 Markdown 执行器 v2
支持作用域系统和多语言代码块执行
"""

import sys
import io
import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

from yanmd_parser import (
    YanMDDocument, YanMDNode, YanMDText, YanMDHeading,
    YanMDCodeBlock, YanMDInlineCode, YanMDMath,
    YanMDBlockquote, YanMDList, YanMDScope,
    build_scope_tree, parse_yanmd
)
from main import run, run_repl


@dataclass
class Scope:
    """作用域"""
    name: str
    level: int
    env: Dict[str, Any] = field(default_factory=dict)
    parent: Optional['Scope'] = None

    def get(self, name: str) -> Any:
        """获取变量（向上查找）"""
        if name in self.env:
            return self.env[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"变量 '{name}' 未定义")

    def set(self, name: str, value: Any):
        """设置变量（当前作用域）"""
        self.env[name] = value

    def has(self, name: str) -> bool:
        """检查变量是否存在"""
        if name in self.env:
            return True
        if self.parent:
            return self.parent.has(name)
        return False

    def all_vars(self) -> Dict[str, Any]:
        """获取所有可访问的变量"""
        result = {}
        if self.parent:
            result.update(self.parent.all_vars())
        result.update(self.env)
        return result


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    output: str = ""
    error: str = ""
    return_value: Any = None


class LanguageAdapter:
    """语言适配器基类"""

    def execute(self, code: str, env: Dict[str, Any]) -> Tuple[Dict[str, Any], ExecutionResult]:
        """执行代码，返回 (更新后的环境, 执行结果)"""
        raise NotImplementedError


class YanAdapter(LanguageAdapter):
    """言语言适配器"""

    def execute(self, code: str, env: Dict[str, Any]) -> Tuple[Dict[str, Any], ExecutionResult]:
        # 导入所有运行时函数
        from runtime import (
            _add, _sub, _mul, _div, _mod, _pow, _abs, _neg,
            _gt, _lt, _eq, _ne,
            _and, _or, _not,
            _list, _head, _tail, _nth, _len, _append, _concat, _contains, _empty,
            _range, _map, _filter, _reduce,
            ALL_BUILTINS,
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
        from parser import add_global_user_verb, clear_global_user_verbs
        
        # 收集用户定义的函数名（可调用的变量）
        user_verbs = set()
        for name, value in env.items():
            if callable(value) and name not in ALL_BUILTINS:
                user_verbs.add(name)
        
        # 注册用户动词
        for name in user_verbs:
            add_global_user_verb(name)
        
        # 创建执行环境
        exec_env = {}
        
        # 添加所有运行时函数（使用函数名，如 _mul）
        runtime_funcs = {
            '_add': _add, '_sub': _sub, '_mul': _mul, '_div': _div, '_mod': _mod,
            '_pow': _pow, '_abs': _abs, '_neg': _neg,
            '_gt': _gt, '_lt': _lt, '_eq': _eq, '_ne': _ne,
            '_and': _and, '_or': _or, '_not': _not,
            '_list': _list, '_head': _head, '_tail': _tail, '_nth': _nth,
            '_len': _len, '_append': _append, '_concat': _concat,
            '_contains': _contains, '_empty': _empty, '_range': _range,
            '_map': _map, '_filter': _filter, '_reduce': _reduce,
            '_sin': _sin, '_cos': _cos, '_tan': _tan,
            '_asin': _asin, '_acos': _acos, '_atan': _atan,
            '_exp': _exp, '_log': _log, '_log10': _log10, '_sqrt': _sqrt,
            '_floor': _floor, '_ceil': _ceil, '_round': _round,
            '_random': _random, '_randint': _randint, '_pi': _pi, '_e': _e,
            '_strlen': _strlen, '_strcat': _strcat, '_strsplit': _strsplit,
            '_strreplace': _strreplace, '_strslice': _strslice,
            '_strlower': _strlower, '_strupper': _strupper,
            '_strfind': _strfind, '_strcontains': _strcontains, '_strstrip': _strstrip,
            '_strstartswith': _strstartswith, '_strendswith': _strendswith,
            '_readfile': _readfile, '_writefile': _writefile, '_appendfile': _appendfile,
            '_fileexists': _fileexists, '_isfile': _isfile, '_isdir': _isdir,
            '_listdir': _listdir, '_mkdir': _mkdir, '_removefile': _removefile,
            '_removedir': _removedir, '_getcwd': _getcwd, '_basename': _basename,
            '_dirname': _dirname, '_extname': _extname,
            '_now': _now, '_date': _date, '_time': _time, '_datetime': _datetime,
            '_strftime': _strftime, '_sleep': _sleep,
            '_isnum': _isnum, '_isstr': _isstr, '_islist': _islist,
            '_isfunc': _isfunc, '_isbool': _isbool, '_isnone': _isnone, '_typeof': _typeof,
        }
        exec_env.update(runtime_funcs)
        
        # 添加内置函数（中文名）
        for name, (func, _) in ALL_BUILTINS.items():
            exec_env[name] = func
        
        # 添加传入的环境变量
        exec_env.update(env)

        # 捕获输出
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            # 执行代码（使用全局用户动词）
            result = run(code, debug=False, env=exec_env, use_global_verbs=True)
            output = sys.stdout.getvalue()
            
            # 提取新定义的变量
            new_env = {}
            builtin_names = set(ALL_BUILTINS.keys())
            runtime_names = set(runtime_funcs.keys())
            excluded_names = {'__builtins__', '__name__', '__doc__', '__package__', '__loader__', '__spec__'}
            
            for name, value in exec_env.items():
                if name not in env and name not in builtin_names and name not in runtime_names and name not in excluded_names:
                    new_env[name] = value

            return new_env, ExecutionResult(
                success=True,
                output=output,
                return_value=result
            )

        except Exception as e:
            return {}, ExecutionResult(
                success=False,
                error=str(e)
            )

        finally:
            sys.stdout = old_stdout


class PythonAdapter(LanguageAdapter):
    """Python 适配器"""

    def execute(self, code: str, env: Dict[str, Any]) -> Tuple[Dict[str, Any], ExecutionResult]:
        # 创建执行环境
        exec_env = env.copy()

        # 捕获输出
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            exec(code, exec_env, exec_env)
            output = sys.stdout.getvalue()

            # 提取新定义的变量
            new_env = {}
            for name, value in exec_env.items():
                if name not in env and not name.startswith('_'):
                    new_env[name] = value

            return new_env, ExecutionResult(
                success=True,
                output=output
            )

        except Exception as e:
            return {}, ExecutionResult(
                success=False,
                error=str(e)
            )

        finally:
            sys.stdout = old_stdout


class ShellAdapter(LanguageAdapter):
    """Shell/Bash 适配器"""

    def execute(self, code: str, env: Dict[str, Any]) -> Tuple[Dict[str, Any], ExecutionResult]:
        try:
            result = subprocess.run(
                ['bash', '-c', code],
                capture_output=True,
                text=True,
                timeout=30
            )

            return {}, ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr
            )

        except subprocess.TimeoutExpired:
            return {}, ExecutionResult(
                success=False,
                error="执行超时"
            )
        except Exception as e:
            return {}, ExecutionResult(
                success=False,
                error=str(e)
            )


class JavaScriptAdapter(LanguageAdapter):
    """JavaScript 适配器"""

    def execute(self, code: str, env: Dict[str, Any]) -> Tuple[Dict[str, Any], ExecutionResult]:
        try:
            # 使用 node 执行
            result = subprocess.run(
                ['node', '-e', code],
                capture_output=True,
                text=True,
                timeout=30
            )

            return {}, ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr
            )

        except FileNotFoundError:
            return {}, ExecutionResult(
                success=False,
                error="未安装 Node.js"
            )
        except subprocess.TimeoutExpired:
            return {}, ExecutionResult(
                success=False,
                error="执行超时"
            )
        except Exception as e:
            return {}, ExecutionResult(
                success=False,
                error=str(e)
            )


class YanMDExecutor:
    """言语言 Markdown 执行器"""

    ADAPTERS = {
        'yan': YanAdapter(),
        'python': PythonAdapter(),
        'py': PythonAdapter(),
        'bash': ShellAdapter(),
        'shell': ShellAdapter(),
        'sh': ShellAdapter(),
        'javascript': JavaScriptAdapter(),
        'js': JavaScriptAdapter(),
    }

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.root_scope = Scope(name="root", level=0)
        self.current_scope = self.root_scope
        self.scope_stack = [self.root_scope]
        self.results: List[Tuple[str, ExecutionResult]] = []

    def execute(self, doc: YanMDDocument) -> str:
        """执行文档"""
        output = []

        for node in doc.children:
            if isinstance(node, YanMDHeading):
                output.append(self._handle_heading(node))

            elif isinstance(node, YanMDCodeBlock):
                rendered, result = self._handle_code_block(node)
                output.append(rendered)
                if result:
                    self.results.append((node.code, result))

            elif isinstance(node, YanMDText):
                output.append(node.content)

            elif isinstance(node, YanMDMath):
                output.append(self._render_math(node))

            elif isinstance(node, YanMDBlockquote):
                output.append(self._render_blockquote(node))

            elif isinstance(node, YanMDList):
                output.append(self._render_list(node))

        return ''.join(output)

    def _handle_heading(self, node: YanMDHeading) -> str:
        """处理标题（作用域切换）"""
        # 计算新作用域
        new_scope = Scope(
            name=node.content,
            level=node.level,
            parent=None
        )

        # 找到父作用域
        while len(self.scope_stack) > 1 and self.scope_stack[-1].level >= node.level:
            self.scope_stack.pop()

        new_scope.parent = self.scope_stack[-1]
        self.scope_stack.append(new_scope)
        self.current_scope = new_scope

        if self.debug:
            print(f"[作用域] 进入: {'  ' * node.level}{node.content}")

        return f"{'#' * node.level} {node.content}\n\n"

    def _handle_code_block(self, node: YanMDCodeBlock) -> Tuple[str, Optional[ExecutionResult]]:
        """处理代码块"""
        result = None

        if node.lang in self.ADAPTERS:
            adapter = self.ADAPTERS[node.lang]
            env = self.current_scope.all_vars()
            
            new_vars, result = adapter.execute(node.code, env)
            
            # 更新作用域
            for name, value in new_vars.items():
                self.current_scope.set(name, value)

        # 渲染代码块
        output = f"```{node.lang}\n{node.code}\n```\n"

        # 添加执行结果
        if result:
            if result.success and (result.output or result.return_value is not None):
                output += f"\n**执行结果：**\n\n"
                if result.output:
                    output += f"```\n{result.output.strip()}\n```\n\n"
                if result.return_value is not None:
                    output += f"**返回值：** `{result.return_value}`\n\n"
            elif not result.success:
                output += f"\n**错误：**\n\n```\n{result.error}\n```\n\n"

        return output, result

    def _render_math(self, node: YanMDMath) -> str:
        """渲染数学公式"""
        if node.inline:
            return f"${node.expr}$"
        else:
            return f"$$\n{node.expr}\n$$\n\n"

    def _render_blockquote(self, node: YanMDBlockquote) -> str:
        """渲染引用块"""
        lines = node.content.split('\n')
        return '\n'.join(f"> {line}" for line in lines) + '\n\n'

    def _render_list(self, node: YanMDList) -> str:
        """渲染列表"""
        lines = []
        for i, item in enumerate(node.items):
            if node.ordered:
                lines.append(f"{i + 1}. {item}")
            else:
                lines.append(f"- {item}")
        return '\n'.join(lines) + '\n\n'


def run_yanmd(filename: str, output_file: Optional[str] = None, debug: bool = False) -> str:
    """运行 .ymd 文件"""
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    # 解析
    doc = parse_yanmd(source)

    # 执行
    executor = YanMDExecutor(debug=debug)
    output = executor.execute(doc)

    # 输出
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"已生成: {output_file}")
    else:
        print(output)

    return output


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python yanmd_executor.py <文件.ymd> [输出文件.md]")
        sys.exit(1)

    filename = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    debug = '--debug' in sys.argv

    run_yanmd(filename, output_file, debug)
