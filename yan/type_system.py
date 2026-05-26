"""
言语言静态类型系统
支持类型检查、类型推断和类型注解
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable, Generic, TypeVar
from dataclasses import dataclass, field
from enum import Enum
import ast


class YanTypeKind(Enum):
    """言语言类型种类"""
    # 基本类型
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    NIL = "nil"
    ANY = "any"
    
    # 复合类型
    ARRAY = "array"
    MAP = "map"
    TUPLE = "tuple"
    STRUCT = "struct"
    UNION = "union"
    OPTIONAL = "optional"
    
    # 函数类型
    FUNCTION = "function"
    
    # 用户定义类型
    CLASS = "class"
    ENUM = "enum"
    
    # 元类型
    TYPE = "type"


@dataclass
class YanType:
    """言语言类型基类"""
    kind: YanTypeKind
    name: str = ""
    nullable: bool = False
    
    def __str__(self) -> str:
        name = self.name or self.kind.value
        if self.nullable:
            return f"{name}?"
        return name
    
    def __repr__(self) -> str:
        return f"YanType({self.kind.value}, name={self.name})"
    
    def is_assignable_to(self, target: 'YanType') -> bool:
        """检查当前类型是否可赋值给目标类型"""
        if self.kind == YanTypeKind.ANY or target.kind == YanTypeKind.ANY:
            return True
        
        # nullable 类型不能赋值给 non-nullable
        if self.nullable and not target.nullable:
            return False
        
        # non-nullable 可以赋值给 nullable
        if not self.nullable and target.nullable:
            return self.kind == target.kind
        
        return self.kind == target.kind
    
    def equals(self, other: 'YanType') -> bool:
        """检查类型是否相等"""
        if self.kind != other.kind:
            return False
        if self.nullable != other.nullable:
            return False
        return True


@dataclass
class IntType(YanType):
    """整数类型"""
    def __init__(self, nullable: bool = False):
        super().__init__(YanTypeKind.INT, "整数", nullable)


@dataclass
class FloatType(YanType):
    """浮点数类型"""
    def __init__(self, nullable: bool = False):
        super().__init__(YanTypeKind.FLOAT, "浮点数", nullable)


@dataclass
class StringType(YanType):
    """字符串类型"""
    def __init__(self, nullable: bool = False):
        super().__init__(YanTypeKind.STRING, "字符串", nullable)


@dataclass
class BoolType(YanType):
    """布尔类型"""
    def __init__(self, nullable: bool = False):
        super().__init__(YanTypeKind.BOOL, "布尔", nullable)


@dataclass
class NilType(YanType):
    """空值类型"""
    def __init__(self):
        super().__init__(YanTypeKind.NIL, "空值", False)


@dataclass
class AnyType(YanType):
    """任意类型"""
    def __init__(self):
        super().__init__(YanTypeKind.ANY, "任意", False)
    
    def is_assignable_to(self, target: 'YanType') -> bool:
        return True


@dataclass
class ArrayType(YanType):
    """数组类型"""
    element_type: YanType = field(default_factory=IntType)
    
    def __init__(self, element_type: YanType, nullable: bool = False):
        super().__init__(YanTypeKind.ARRAY, f"数组<{element_type}>", nullable)
        self.element_type = element_type
    
    def equals(self, other: 'YanType') -> bool:
        if not super().equals(other):
            return False
        if isinstance(other, ArrayType):
            return self.element_type.equals(other.element_type)
        return False


@dataclass
class MapType(YanType):
    """映射类型"""
    key_type: YanType = field(default_factory=StringType)
    value_type: YanType = field(default_factory=AnyType)
    
    def __init__(self, key_type: YanType, value_type: YanType, nullable: bool = False):
        super().__init__(YanTypeKind.MAP, f"映射<{key_type}, {value_type}>", nullable)
        self.key_type = key_type
        self.value_type = value_type
    
    def equals(self, other: 'YanType') -> bool:
        if not super().equals(other):
            return False
        if isinstance(other, MapType):
            return self.key_type.equals(other.key_type) and self.value_type.equals(other.value_type)
        return False


@dataclass
class TupleType(YanType):
    """元组类型"""
    element_types: List[YanType] = field(default_factory=list)
    
    def __init__(self, element_types: List[YanType], nullable: bool = False):
        name = f"元组<{', '.join(str(t) for t in element_types)}>"
        super().__init__(YanTypeKind.TUPLE, name, nullable)
        self.element_types = element_types
    
    def equals(self, other: 'YanType') -> bool:
        if not super().equals(other):
            return False
        if isinstance(other, TupleType):
            if len(self.element_types) != len(other.element_types):
                return False
            return all(a.equals(b) for a, b in zip(self.element_types, other.element_types))
        return False


@dataclass
class StructType(YanType):
    """结构体类型"""
    fields: Dict[str, YanType] = field(default_factory=dict)
    
    def __init__(self, name: str, fields: Dict[str, YanType], nullable: bool = False):
        super().__init__(YanTypeKind.STRUCT, name, nullable)
        self.fields = fields
    
    def equals(self, other: 'YanType') -> bool:
        if not super().equals(other):
            return False
        if isinstance(other, StructType):
            if set(self.fields.keys()) != set(other.fields.keys()):
                return False
            return all(self.fields[k].equals(other.fields[k]) for k in self.fields)
        return False


@dataclass
class UnionType(YanType):
    """联合类型"""
    types: List[YanType] = field(default_factory=list)
    
    def __init__(self, types: List[YanType], nullable: bool = False):
        name = " | ".join(str(t) for t in types)
        super().__init__(YanTypeKind.UNION, name, nullable)
        self.types = types
    
    def is_assignable_to(self, target: 'YanType') -> bool:
        """联合类型可赋值给任意成员类型"""
        return any(t.is_assignable_to(target) for t in self.types)
    
    def equals(self, other: 'YanType') -> bool:
        if not super().equals(other):
            return False
        if isinstance(other, UnionType):
            if len(self.types) != len(other.types):
                return False
            return all(a.equals(b) for a, b in zip(self.types, other.types))
        return False


class OptionalType(YanType):
    """可选类型"""
    
    def __init__(self, base_type: YanType):
        # 避免重复添加 ?，提取基础名称（去掉已有的 ?）
        if base_type.nullable and base_type.name.endswith('?'):
            base_name = base_type.name[:-1]
        else:
            base_name = base_type.name
        # 传递不带 ? 的名称给基类，因为基类 __str__ 会根据 nullable 添加
        super().__init__(YanTypeKind.OPTIONAL, base_name, True)
        self.base_type = base_type


@dataclass
class FunctionType(YanType):
    """函数类型"""
    param_types: List[YanType] = field(default_factory=list)
    return_type: YanType = field(default_factory=IntType)
    
    def __init__(self, param_types: List[YanType], return_type: YanType, nullable: bool = False):
        params = ", ".join(str(p) for p in param_types)
        name = f"函数<({params}) -> {return_type}>"
        super().__init__(YanTypeKind.FUNCTION, name, nullable)
        self.param_types = param_types
        self.return_type = return_type
    
    def equals(self, other: 'YanType') -> bool:
        if not super().equals(other):
            return False
        if isinstance(other, FunctionType):
            if len(self.param_types) != len(other.param_types):
                return False
            if not self.return_type.equals(other.return_type):
                return False
            return all(a.equals(b) for a, b in zip(self.param_types, other.param_types))
        return False


class TypeRegistry:
    """类型注册表"""
    
    def __init__(self):
        self._types: Dict[str, YanType] = {}
        self._aliases: Dict[str, str] = {}
        self._init_builtin_types()
    
    def _init_builtin_types(self):
        """初始化内置类型"""
        # 基本类型
        self.register_type(IntType())
        self.register_type(FloatType())
        self.register_type(StringType())
        self.register_type(BoolType())
        self.register_type(NilType())
        self.register_type(AnyType())
    
    def register_type(self, type_obj: YanType, alias: str = None):
        """注册类型"""
        self._types[type_obj.name] = type_obj
        if alias:
            self._aliases[alias] = type_obj.name
    
    def get_type(self, name: str) -> Optional[YanType]:
        """获取类型"""
        if name in self._types:
            return self._types[name]
        if name in self._aliases:
            type_name = self._aliases[name]
            return self._types.get(type_name)
        return None
    
    def list_types(self) -> List[str]:
        """列出所有类型"""
        return list(self._types.keys())


class TypeEnvironment:
    """类型环境"""
    
    def __init__(self, parent: Optional['TypeEnvironment'] = None):
        self.parent = parent
        self._variables: Dict[str, YanType] = {}
        self._functions: Dict[str, FunctionType] = {}
    
    def define_variable(self, name: str, type_obj: YanType):
        """定义变量"""
        self._variables[name] = type_obj
    
    def get_variable(self, name: str) -> Optional[YanType]:
        """获取变量类型"""
        if name in self._variables:
            return self._variables[name]
        if self.parent:
            return self.parent.get_variable(name)
        return None
    
    def define_function(self, name: str, func_type: FunctionType):
        """定义函数"""
        self._functions[name] = func_type
    
    def get_function(self, name: str) -> Optional[FunctionType]:
        """获取函数类型"""
        if name in self._functions:
            return self._functions[name]
        if self.parent:
            return self.parent.get_function(name)
        return None
    
    def push_scope(self) -> 'TypeEnvironment':
        """进入新作用域"""
        return TypeEnvironment(parent=self)
    
    def pop_scope(self):
        """退出作用域"""
        pass


class TypeChecker:
    """类型检查器"""
    
    def __init__(self, registry: TypeRegistry = None):
        self.registry = registry or TypeRegistry()
        self.env = TypeEnvironment()
        self._errors: List[TypeError] = []
        self._warnings: List[str] = []
    
    def check(self, node) -> Optional[YanType]:
        """检查节点类型"""
        node_type = type(node).__name__
        
        check_method = getattr(self, f'_check_{node_type}', None)
        if check_method:
            return check_method(node)
        
        return AnyType()
    
    def _check_Num(self, node) -> YanType:
        """检查数字节点"""
        return IntType()
    
    def _check_Str(self, node) -> YanType:
        """检查字符串节点"""
        return StringType()
    
    def _check_Bool(self, node) -> YanType:
        """检查布尔节点"""
        return BoolType()
    
    def _check_Nil(self, node) -> YanType:
        """检查空值节点"""
        return NilType()
    
    def _check_Word(self, node) -> YanType:
        """检查标识符节点"""
        var_type = self.env.get_variable(node.name)
        if var_type:
            return var_type
        self._errors.append(TypeError(f"未定义的变量: {node.name}"))
        return AnyType()
    
    def _check_Call(self, node) -> YanType:
        """检查函数调用"""
        # 获取函数类型
        func_type = self.env.get_function(node.verb.name)
        if not func_type:
            self._errors.append(TypeError(f"未定义的函数: {node.verb.name}"))
            return AnyType()
        
        # 检查参数类型
        for i, arg in enumerate(node.args):
            arg_type = self.check(arg)
            if i < len(func_type.param_types):
                param_type = func_type.param_types[i]
                if not arg_type.is_assignable_to(param_type):
                    self._errors.append(TypeError(
                        f"参数类型不匹配: 期望 {param_type}, 实际 {arg_type}"
                    ))
        
        return func_type.return_type
    
    def _check_BinaryOp(self, node) -> YanType:
        """检查二元运算"""
        left_type = self.check(node.args[0])
        right_type = self.check(node.args[1])
        
        # 算术运算
        if node.verb.name in ['+', '-', '*', '/', '%']:
            if left_type.kind in [YanTypeKind.INT, YanTypeKind.FLOAT] and \
               right_type.kind in [YanTypeKind.INT, YanTypeKind.FLOAT]:
                if left_type.kind == YanTypeKind.FLOAT or right_type.kind == YanTypeKind.FLOAT:
                    return FloatType()
                return IntType()
            self._errors.append(TypeError(f"算术运算类型错误: {left_type} 和 {right_type}"))
            return AnyType()
        
        # 比较运算
        if node.verb.name in ['==', '!=', '<', '>', '<=', '>=']:
            return BoolType()
        
        # 逻辑运算
        if node.verb.name in ['&&', '||', '!']:
            return BoolType()
        
        return AnyType()
    
    def _check_Define(self, node) -> YanType:
        """检查定义语句"""
        value_type = self.check(node.value)
        self.env.define_variable(node.name, value_type)
        return NilType()
    
    def _check_Function(self, node) -> YanType:
        """检查函数定义"""
        # 创建函数作用域
        func_env = self.env.push_scope()
        
        # 参数类型
        param_types = []
        for param in node.value.params:
            param_type = IntType()  # 默认类型
            func_env.define_variable(param, param_type)
            param_types.append(param_type)
        
        # 返回类型
        return_type = IntType()  # 默认类型
        
        # 检查函数体
        for stmt in node.value.body.statements:
            self.env = func_env
            self.check(stmt)
        
        func_type = FunctionType(param_types, return_type)
        self.env.define_function(node.name, func_type)
        
        return NilType()
    
    def _check_If(self, node) -> YanType:
        """检查条件语句"""
        cond_type = self.check(node.cond)
        if cond_type.kind != YanTypeKind.BOOL:
            self._warnings.append(f"条件表达式应为布尔类型，实际为 {cond_type}")
        
        self.check(node.then_branch)
        if node.else_branch:
            self.check(node.else_branch)
        
        return NilType()
    
    def _check_Return(self, node) -> YanType:
        """检查返回语句"""
        return self.check(node.value)
    
    def get_errors(self) -> List[TypeError]:
        """获取错误列表"""
        return self._errors
    
    def get_warnings(self) -> List[str]:
        """获取警告列表"""
        return self._warnings
    
    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self._errors) > 0


class TypeError(Exception):
    """类型错误"""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        if self.line > 0:
            return f"类型错误 (行 {self.line}): {self.message}"
        return f"类型错误: {self.message}"


class TypeInferrer:
    """类型推断器"""
    
    def __init__(self):
        self.registry = TypeRegistry()
        self.env = TypeEnvironment()
    
    def infer(self, node) -> YanType:
        """推断节点类型"""
        return self._infer_node(node)
    
    def _infer_node(self, node) -> YanType:
        """推断节点类型"""
        if node is None:
            return NilType()
        
        node_type = type(node).__name__
        
        if node_type == 'Num':
            return IntType()
        elif node_type == 'Str':
            return StringType()
        elif node_type == 'Bool':
            return BoolType()
        elif node_type == 'Nil':
            return NilType()
        elif node_type == 'Word':
            var_type = self.env.get_variable(node.name)
            return var_type or AnyType()
        elif node_type == 'ListLiteral':
            if node.elements:
                element_type = self.infer(node.elements[0])
                return ArrayType(element_type)
            return ArrayType(AnyType())
        elif node_type == 'Call':
            return self._infer_call(node)
        else:
            return AnyType()
    
    def _infer_call(self, node) -> YanType:
        """推断函数调用"""
        func_type = self.env.get_function(node.verb.name)
        if func_type:
            return func_type.return_type
        return AnyType()


# 类型工具函数
def make_optional(base_type: YanType) -> YanType:
    """创建可选类型"""
    return OptionalType(base_type)


def make_array(element_type: YanType) -> ArrayType:
    """创建数组类型"""
    return ArrayType(element_type)


def make_map(key_type: YanType, value_type: YanType) -> MapType:
    """创建映射类型"""
    return MapType(key_type, value_type)


def make_union(types: List[YanType]) -> UnionType:
    """创建联合类型"""
    return UnionType(types)


def make_function(param_types: List[YanType], return_type: YanType) -> FunctionType:
    """创建函数类型"""
    return FunctionType(param_types, return_type)


def common_type(types: List[YanType]) -> YanType:
    """计算类型的公共父类型"""
    if not types:
        return AnyType()
    
    # 如果有any，返回any
    if any(t.kind == YanTypeKind.ANY for t in types):
        return AnyType()
    
    # 检查是否都是数字类型
    numeric_types = {YanTypeKind.INT, YanTypeKind.FLOAT}
    if all(t.kind in numeric_types for t in types):
        if any(t.kind == YanTypeKind.FLOAT for t in types):
            return FloatType()
        return IntType()
    
    # 检查是否都是布尔类型
    if all(t.kind == YanTypeKind.BOOL for t in types):
        return BoolType()
    
    # 检查是否都是字符串类型
    if all(t.kind == YanTypeKind.STRING for t in types):
        return StringType()
    
    # 返回第一个类型作为默认
    return types[0]


def is_numeric_type(type_obj: YanType) -> bool:
    """检查是否为数值类型"""
    return type_obj.kind in {YanTypeKind.INT, YanTypeKind.FLOAT}


def is_truthy_type(type_obj: YanType) -> bool:
    """检查是否为真值类型"""
    return type_obj.kind != YanTypeKind.NIL


# 全局类型注册表
_global_registry = TypeRegistry()


def get_global_registry() -> TypeRegistry:
    """获取全局类型注册表"""
    return _global_registry


def get_builtin_type(name: str) -> Optional[YanType]:
    """获取内置类型"""
    return _global_registry.get_type(name)


# 示例使用
if __name__ == "__main__":
    # 创建类型
    int_type = IntType()
    float_type = FloatType()
    string_type = StringType()
    bool_type = BoolType()
    
    print(f"整数类型: {int_type}")
    print(f"浮点类型: {float_type}")
    print(f"字符串类型: {string_type}")
    print(f"布尔类型: {bool_type}")
    
    # 数组类型
    array_type = ArrayType(IntType())
    print(f"整数数组: {array_type}")
    
    # 映射类型
    map_type = MapType(StringType(), IntType())
    print(f"字符串到整数的映射: {map_type}")
    
    # 函数类型
    func_type = FunctionType([IntType(), IntType()], IntType())
    print(f"函数类型: {func_type}")
    
    # 联合类型
    union_type = UnionType([IntType(), FloatType()])
    print(f"联合类型: {union_type}")
    
    # 类型检查
    print(f"\n类型赋值检查:")
    print(f"整数 -> 整数: {IntType().is_assignable_to(IntType())}")
    print(f"整数 -> 浮点: {IntType().is_assignable_to(FloatType())}")
    print(f"浮点 -> 整数: {FloatType().is_assignable_to(IntType())}")
    
    # 类型推断
    print(f"\n类型推断:")
    inferrer = TypeInferrer()
    
    class MockNode:
        pass
    
    num_node = MockNode()
    num_node.__class__.__name__ = 'Num'
    print(f"数字节点: {inferrer.infer(num_node)}")
    
    str_node = MockNode()
    str_node.__class__.__name__ = 'Str'
    print(f"字符串节点: {inferrer.infer(str_node)}")
    
    # 类型注册表
    print(f"\n内置类型:")
    for type_name in _global_registry.list_types():
        print(f"  - {type_name}")