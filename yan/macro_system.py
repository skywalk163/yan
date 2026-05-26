"""
言语言宏系统 - 编译时元编程
支持语法扩展、代码生成和编译时计算
"""

import re
import ast
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class MacroType(Enum):
    """宏类型"""
    FUNCTION = "function"      # 函数宏
    TEMPLATE = "template"      # 模板宏
    CONDITIONAL = "conditional" # 条件宏
    REPEAT = "repeat"          # 重复宏
    QUOTE = "quote"           # 引用宏
    UNQUOTE = "unquote"       # 反引用宏


@dataclass
class MacroArg:
    """宏参数"""
    name: str
    value: Any
    is_variadic: bool = False
    
    def __repr__(self):
        return f"MacroArg({self.name}={self.value})"


@dataclass
class Macro:
    """宏定义"""
    name: str
    macro_type: MacroType
    args: List[str]
    body: str
    is_variadic: bool = False
    doc: str = ""
    
    def __repr__(self):
        return f"Macro({self.name}, type={self.macro_type.value}, args={self.args})"


@dataclass
class ExpansionResult:
    """宏展开结果"""
    code: str
    success: bool
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        status = "成功" if self.success else f"失败: {self.error}"
        return f"ExpansionResult({status})"


class MacroContext:
    """宏展开上下文"""
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.macros: Dict[str, Macro] = {}
        self.call_stack: List[str] = []
        self.metadata: Dict[str, Any] = {}
    
    def push_scope(self):
        """进入新作用域"""
        self.variables = {**self.variables}
    
    def pop_scope(self):
        """退出作用域"""
        # 在实际实现中需要父作用域引用
        pass
    
    def define_variable(self, name: str, value: Any):
        """定义变量"""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Optional[Any]:
        """获取变量"""
        return self.variables.get(name)
    
    def enter_macro(self, macro_name: str):
        """进入宏调用"""
        self.call_stack.append(macro_name)
    
    def exit_macro(self):
        """退出宏调用"""
        if self.call_stack:
            self.call_stack.pop()


class MacroTransformer:
    """宏转换器基类"""
    
    @abstractmethod
    def transform(self, code: str, context: MacroContext) -> ExpansionResult:
        """转换代码"""
        pass


class FunctionMacroTransformer(MacroTransformer):
    """函数宏转换器"""
    
    def __init__(self, macro: Macro):
        self.macro = macro
    
    def transform(self, code: str, context: MacroContext) -> ExpansionResult:
        """展开函数宏"""
        try:
            # 解析参数
            args = self._parse_args(code)
            
            # 创建展开上下文
            expand_context = MacroContext()
            expand_context.variables.update(context.variables)
            
            # 设置宏参数
            for i, arg_name in enumerate(self.macro.args):
                if i < len(args):
                    expand_context.define_variable(arg_name, args[i])
                elif not self.macro.is_variadic:
                    expand_context.define_variable(arg_name, None)
            
            # 处理可变参数
            if self.macro.is_variadic and len(self.macro.args) > 0:
                last_arg = self.macro.args[-1]
                expand_context.define_variable(last_arg, args[len(self.macro.args)-1:])
            
            # 展开宏体
            expanded = self._expand_body(self.macro.body, expand_context)
            
            return ExpansionResult(code=expanded, success=True)
        
        except Exception as e:
            return ExpansionResult(code=code, success=False, error=str(e))
    
    def _parse_args(self, code: str) -> List[str]:
        """解析参数"""
        # 简单的参数解析（实际实现需要更复杂的解析器）
        code = code.strip()
        if not code:
            return []
        
        # 按逗号分割，但考虑括号
        args = []
        depth = 0
        current = ""
        
        for char in code:
            if char in '（(':
                depth += 1
                current += char
            elif char in '）)':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                args.append(current.strip())
                current = ""
            else:
                current += char
        
        if current.strip():
            args.append(current.strip())
        
        return args
    
    def _expand_body(self, body: str, context: MacroContext) -> str:
        """展开宏体"""
        result = body
        
        # 替换变量引用
        for name, value in context.variables.items():
            result = result.replace(f"@{name}", str(value))
        
        # 处理反引用
        result = self._process_unquotes(result, context)
        
        return result
    
    def _process_unquotes(self, body: str, context: MacroContext) -> str:
        """处理反引用"""
        # 简单的反引用处理
        pattern = r'\$\{(\w+)\}'
        
        def replacer(match):
            var_name = match.group(1)
            value = context.get_variable(var_name)
            if value is not None:
                return str(value)
            return match.group(0)
        
        return re.sub(pattern, replacer, body)


class TemplateMacroTransformer(MacroTransformer):
    """模板宏转换器"""
    
    def __init__(self, template: str):
        self.template = template
    
    def transform(self, code: str, context: MacroContext) -> ExpansionResult:
        """展开模板"""
        try:
            result = self.template
            
            # 替换变量
            for name, value in context.variables.items():
                result = result.replace(f"{{{name}}}", str(value))
            
            return ExpansionResult(code=result, success=True)
        
        except Exception as e:
            return ExpansionResult(code=code, success=False, error=str(e))


class QuoteTransformer:
    """引用转换器"""
    
    def __init__(self):
        self.quoted = []
    
    def quote(self, code: str) -> str:
        """引用代码（阻止展开）"""
        # 返回带标记的引用代码
        quoted_id = len(self.quoted)
        self.quoted.append(code)
        return f"__quote__{quoted_id}__"
    
    def unquote(self, code: str, context: MacroContext) -> str:
        """反引用（允许在引用中展开）"""
        # 处理反引用
        pattern = r'\$\{(\w+)\}'
        
        def replacer(match):
            var_name = match.group(1)
            value = context.get_variable(var_name)
            return str(value) if value is not None else match.group(0)
        
        return re.sub(pattern, replacer, code)
    
    def expand_quotes(self, code: str) -> str:
        """展开所有引用"""
        result = code
        
        for i, quoted in enumerate(self.quoted):
            result = result.replace(f"__quote__{i}__", quoted)
        
        self.quoted.clear()
        return result


class RepeatMacroTransformer(MacroTransformer):
    """重复宏转换器"""
    
    def transform(self, code: str, context: MacroContext) -> ExpansionResult:
        """展开重复宏"""
        try:
            # 解析重复次数和内容
            # 格式: #重复(次数, 内容)
            pattern = r'#重复\((\d+),\s*(.+)\)'
            match = re.search(pattern, code)
            
            if not match:
                return ExpansionResult(code=code, success=False, error="无效的重复语法")
            
            count = int(match.group(1))
            content = match.group(2)
            
            # 展开重复
            expanded_parts = []
            for i in range(count):
                # 替换特殊变量
                part = content.replace("@index", str(i))
                expanded_parts.append(part)
            
            expanded = "\n".join(expanded_parts)
            
            # 替换原始代码
            result = code[:match.start()] + expanded + code[match.end():]
            
            return ExpansionResult(code=result, success=True)
        
        except Exception as e:
            return ExpansionResult(code=code, success=False, error=str(e))


class ConditionalMacroTransformer(MacroTransformer):
    """条件宏转换器"""
    
    def transform(self, code: str, context: MacroContext) -> ExpansionResult:
        """展开条件宏"""
        try:
            # 解析条件
            # 格式: #如果(条件, 真值分支, 假值分支)
            pattern = r'#如果\((.+),\s*(.+?),\s*(.+)\)'
            match = re.search(pattern, code)
            
            if not match:
                return ExpansionResult(code=code, success=False, error="无效的条件语法")
            
            condition_str = match.group(1)
            true_branch = match.group(2)
            false_branch = match.group(3)
            
            # 评估条件
            condition = self._evaluate_condition(condition_str, context)
            
            # 选择分支
            result_code = true_branch if condition else false_branch
            
            # 替换原始代码
            result = code[:match.start()] + result_code + code[match.end():]
            
            return ExpansionResult(code=result, success=True)
        
        except Exception as e:
            return ExpansionResult(code=code, success=False, error=str(e))
    
    def _evaluate_condition(self, condition: str, context: MacroContext) -> bool:
        """评估条件"""
        # 简单条件评估
        condition = condition.strip()
        
        # 检查变量
        if condition in context.variables:
            return bool(context.variables[condition])
        
        # 评估表达式
        try:
            return bool(eval(condition, {}, context.variables))
        except:
            return False


class MacroSystem:
    """宏系统主类"""
    
    def __init__(self):
        self.macros: Dict[str, Macro] = {}
        self.context = MacroContext()
        self.quote_transformer = QuoteTransformer()
        self._init_builtin_macros()
    
    def _init_builtin_macros(self):
        """初始化内置宏"""
        # 调试宏
        self.define_macro(Macro(
            name="调试",
            macro_type=MacroType.FUNCTION,
            args=["message"],
            body='打印("调试: " + @message)',
            doc="打印调试信息"
        ))
        
        # 断言宏
        self.define_macro(Macro(
            name="断言",
            macro_type=MacroType.FUNCTION,
            args=["condition", "message"],
            body='如果 非 @condition 则 抛出("断言失败: " + @message)',
            doc="断言条件为真"
        ))
        
        # 时间测量宏
        self.define_macro(Macro(
            name="计时",
            macro_type=MacroType.FUNCTION,
            args=["block"],
            body='定义 开始 = 时间.现在(); @block; 打印("耗时: " + (时间.现在() - 开始) + "秒")',
            doc="测量代码块执行时间"
        ))
    
    def define_macro(self, macro: Macro):
        """定义宏"""
        self.macros[macro.name] = macro
        self.context.macros[macro.name] = macro
    
    def undefine_macro(self, name: str) -> bool:
        """取消宏定义"""
        if name in self.macros:
            del self.macros[name]
            return True
        return False
    
    def get_macro(self, name: str) -> Optional[Macro]:
        """获取宏"""
        return self.macros.get(name)
    
    def list_macros(self) -> List[str]:
        """列出所有宏"""
        return list(self.macros.keys())
    
    def expand(self, code: str) -> ExpansionResult:
        """展开代码中的所有宏"""
        try:
            original_code = code
            max_iterations = 100  # 防止无限循环
            iteration = 0
            changed = True
            
            while changed and iteration < max_iterations:
                changed = False
                iteration += 1
                
                # 展开函数宏
                code, did_change = self._expand_function_macros(code)
                changed = changed or did_change
                
                # 展开条件宏
                code, did_change = self._expand_conditional_macros(code)
                changed = changed or did_change
                
                # 展开重复宏
                code, did_change = self._expand_repeat_macros(code)
                changed = changed or did_change
            
            if iteration >= max_iterations:
                return ExpansionResult(
                    code=code,
                    success=False,
                    error="宏展开可能存在无限循环"
                )
            
            # 展开引用
            code = self.quote_transformer.expand_quotes(code)
            
            return ExpansionResult(
                code=code,
                success=True,
                stats={
                    "iterations": iteration,
                    "original_length": len(original_code),
                    "expanded_length": len(code)
                }
            )
        
        except Exception as e:
            return ExpansionResult(code=code, success=False, error=str(e))
    
    def _expand_function_macros(self, code: str) -> Tuple[str, bool]:
        """展开函数宏"""
        changed = False
        
        for name, macro in self.macros.items():
            if macro.macro_type != MacroType.FUNCTION:
                continue
            
            # 查找宏调用
            # 格式: @宏名(参数)
            pattern = rf'@{name}\((.*?)\)'
            
            def replacer(match):
                nonlocal changed
                changed = True
                
                args_str = match.group(1)
                transformer = FunctionMacroTransformer(macro)
                result = transformer.transform(args_str, self.context)
                
                if result.success:
                    return result.code
                else:
                    return match.group(0)  # 保持原样
            
            code = re.sub(pattern, replacer, code)
        
        return code, changed
    
    def _expand_conditional_macros(self, code: str) -> Tuple[str, bool]:
        """展开条件宏"""
        transformer = ConditionalMacroTransformer()
        result = transformer.transform(code, self.context)
        
        if result.success and result.code != code:
            return result.code, True
        
        return code, False
    
    def _expand_repeat_macros(self, code: str) -> Tuple[str, bool]:
        """展开重复宏"""
        transformer = RepeatMacroTransformer()
        result = transformer.transform(code, self.context)
        
        if result.success and result.code != code:
            return result.code, True
        
        return code, False
    
    def expand_macro(self, name: str, args: List[Any]) -> ExpansionResult:
        """展开指定的宏"""
        macro = self.get_macro(name)
        
        if not macro:
            return ExpansionResult(
                code="",
                success=False,
                error=f"未定义的宏: {name}"
            )
        
        # 设置参数
        for i, arg_name in enumerate(macro.args):
            if i < len(args):
                self.context.define_variable(arg_name, args[i])
        
        # 展开宏体
        if macro.macro_type == MacroType.FUNCTION:
            transformer = FunctionMacroTransformer(macro)
            return transformer.transform("", self.context)
        
        return ExpansionResult(
            code=macro.body,
            success=True
        )


class MacroDecorator:
    """宏装饰器"""
    
    def __init__(self, macro_system: MacroSystem):
        self.macro_system = macro_system
    
    def macro(self, name: str = None, args: List[str] = None):
        """宏装饰器"""
        def decorator(func: Callable) -> Callable:
            macro_name = name or func.__name__
            arg_names = args or []
            
            # 从函数签名提取参数
            import inspect
            if not arg_names:
                sig = inspect.signature(func)
                arg_names = [p.name for p in sig.parameters.values()]
            
            # 获取函数体（使用 __doc__ 或源代码）
            body = func.__doc__ or ""
            
            macro = Macro(
                name=macro_name,
                macro_type=MacroType.FUNCTION,
                args=arg_names,
                body=body,
                doc=func.__doc__ or ""
            )
            
            self.macro_system.define_macro(macro)
            
            return func
        
        return decorator


# 全局宏系统实例
_global_macro_system: Optional[MacroSystem] = None


def get_global_macro_system() -> MacroSystem:
    """获取全局宏系统"""
    global _global_macro_system
    if _global_macro_system is None:
        _global_macro_system = MacroSystem()
    return _global_macro_system


def expand_macros(code: str) -> str:
    """展开代码中的宏（快捷函数）"""
    system = get_global_macro_system()
    result = system.expand(code)
    if result.success:
        return result.code
    else:
        raise MacroError(result.error or "宏展开失败")


def define_macro(name: str, args: List[str], body: str, macro_type: MacroType = MacroType.FUNCTION):
    """定义宏（快捷函数）"""
    system = get_global_macro_system()
    macro = Macro(name=name, macro_type=macro_type, args=args, body=body)
    system.define_macro(macro)


class MacroError(Exception):
    """宏错误"""
    pass


# 示例使用
if __name__ == "__main__":
    system = MacroSystem()
    
    # 定义自定义宏
    system.define_macro(Macro(
        name="平方",
        macro_type=MacroType.FUNCTION,
        args=["x"],
        body="@x * @x",
        doc="计算平方"
    ))
    
    # 定义循环宏
    system.define_macro(Macro(
        name="循环3次",
        macro_type=MacroType.FUNCTION,
        args=["block"],
        body="@block\n@block\n@block",
        doc="重复执行代码块3次"
    ))
    
    print("已定义的宏:")
    for name in system.list_macros():
        macro = system.get_macro(name)
        print(f"  - {name}: {macro.doc}")
    
    # 测试展开
    test_code = "@平方(5)"
    result = system.expand(test_code)
    print(f"\n展开测试:")
    print(f"  输入: {test_code}")
    print(f"  输出: {result.code}")
    print(f"  状态: {'成功' if result.success else '失败'}")
    
    # 测试条件宏
    test_conditional = "#如果(true, '真', '假')"
    result = system.expand(test_conditional)
    print(f"\n条件宏测试:")
    print(f"  输入: {test_conditional}")
    print(f"  输出: {result.code}")
    
    # 测试重复宏
    test_repeat = "#重复(3, 输出(@index))"
    result = system.expand(test_repeat)
    print(f"\n重复宏测试:")
    print(f"  输入: {test_repeat}")
    print(f"  输出: {result.code}")
    
    # 展开统计
    print(f"\n展开统计:")
    print(f"  迭代次数: {result.stats.get('iterations', 0)}")
    print(f"  原始长度: {result.stats.get('original_length', 0)}")
    print(f"  展开后长度: {result.stats.get('expanded_length', 0)}")