"""
类型系统测试
"""

import pytest
import sys

sys.path.insert(0, 'g:/dumategithub/newlisp/yan')

from type_system import (
    YanTypeKind,
    YanType,
    IntType,
    FloatType,
    StringType,
    BoolType,
    NilType,
    AnyType,
    ArrayType,
    MapType,
    TupleType,
    StructType,
    UnionType,
    OptionalType,
    FunctionType,
    TypeRegistry,
    TypeEnvironment,
    TypeChecker,
    TypeError,
    TypeInferrer,
    make_optional,
    make_array,
    make_map,
    make_union,
    make_function,
    common_type,
    is_numeric_type,
    is_truthy_type,
    get_global_registry,
    get_builtin_type
)


class TestBasicTypes:
    """基本类型测试"""
    
    def test_int_type(self):
        """测试整数类型"""
        t = IntType()
        assert t.kind == YanTypeKind.INT
        assert str(t) == "整数"
    
    def test_float_type(self):
        """测试浮点类型"""
        t = FloatType()
        assert t.kind == YanTypeKind.FLOAT
        assert str(t) == "浮点数"
    
    def test_string_type(self):
        """测试字符串类型"""
        t = StringType()
        assert t.kind == YanTypeKind.STRING
        assert str(t) == "字符串"
    
    def test_bool_type(self):
        """测试布尔类型"""
        t = BoolType()
        assert t.kind == YanTypeKind.BOOL
        assert str(t) == "布尔"
    
    def test_nil_type(self):
        """测试空值类型"""
        t = NilType()
        assert t.kind == YanTypeKind.NIL
        assert str(t) == "空值"
    
    def test_any_type(self):
        """测试任意类型"""
        t = AnyType()
        assert t.kind == YanTypeKind.ANY
        assert str(t) == "任意"


class TestNullableTypes:
    """可空类型测试"""
    
    def test_nullable_int(self):
        """测试可空整数"""
        t = IntType(nullable=True)
        assert t.nullable is True
        assert str(t) == "整数?"


class TestComplexTypes:
    """复合类型测试"""
    
    def test_array_type(self):
        """测试数组类型"""
        element_type = IntType()
        t = ArrayType(element_type)
        assert t.kind == YanTypeKind.ARRAY
        assert t.element_type.equals(IntType())
        assert "整数" in str(t)
    
    def test_map_type(self):
        """测试映射类型"""
        key_type = StringType()
        value_type = IntType()
        t = MapType(key_type, value_type)
        assert t.kind == YanTypeKind.MAP
        assert t.key_type.equals(StringType())
        assert t.value_type.equals(IntType())
    
    def test_tuple_type(self):
        """测试元组类型"""
        types = [IntType(), StringType(), BoolType()]
        t = TupleType(types)
        assert t.kind == YanTypeKind.TUPLE
        assert len(t.element_types) == 3
        assert t.element_types[0].equals(IntType())
    
    def test_struct_type(self):
        """测试结构体类型"""
        fields = {
            "name": StringType(),
            "age": IntType()
        }
        t = StructType("Person", fields)
        assert t.kind == YanTypeKind.STRUCT
        assert t.name == "Person"
        assert len(t.fields) == 2
    
    def test_union_type(self):
        """测试联合类型"""
        types = [IntType(), FloatType()]
        t = UnionType(types)
        assert t.kind == YanTypeKind.UNION
        assert len(t.types) == 2
    
    def test_optional_type(self):
        """测试可选类型"""
        base_type = IntType()
        t = OptionalType(base_type)
        assert t.kind == YanTypeKind.OPTIONAL
        assert t.nullable is True
        assert str(t) == "整数?"
    
    def test_function_type(self):
        """测试函数类型"""
        param_types = [IntType(), IntType()]
        return_type = IntType()
        t = FunctionType(param_types, return_type)
        assert t.kind == YanTypeKind.FUNCTION
        assert len(t.param_types) == 2
        assert t.return_type.equals(IntType())


class TestTypeAssignment:
    """类型赋值测试"""
    
    def test_same_type_assignment(self):
        """测试相同类型赋值"""
        assert IntType().is_assignable_to(IntType()) is True
        assert StringType().is_assignable_to(StringType()) is True
    
    def test_int_to_float_assignment(self):
        """测试整数到浮点数赋值"""
        # 注意：在言语言中，整数和浮点数是不同类型
        assert IntType().is_assignable_to(FloatType()) is False
    
    def test_any_assignment(self):
        """测试任意类型赋值"""
        assert IntType().is_assignable_to(AnyType()) is True
        assert StringType().is_assignable_to(AnyType()) is True
        assert AnyType().is_assignable_to(IntType()) is True
    
    def test_nullable_assignment(self):
        """测试可空类型赋值"""
        nullable_int = IntType(nullable=True)
        non_nullable_int = IntType(nullable=False)
        
        # 非空类型可以赋值给可空类型
        assert non_nullable_int.is_assignable_to(nullable_int) is True
        # 可空类型不能赋值给非空类型
        assert nullable_int.is_assignable_to(non_nullable_int) is False
        assert nullable_int.is_assignable_to(nullable_int) is True


class TestTypeEquality:
    """类型相等性测试"""
    
    def test_basic_type_equality(self):
        """测试基本类型相等"""
        assert IntType().equals(IntType()) is True
        assert IntType().equals(FloatType()) is False
    
    def test_array_type_equality(self):
        """测试数组类型相等"""
        assert ArrayType(IntType()).equals(ArrayType(IntType())) is True
        assert ArrayType(IntType()).equals(ArrayType(FloatType())) is False
    
    def test_map_type_equality(self):
        """测试映射类型相等"""
        t1 = MapType(StringType(), IntType())
        t2 = MapType(StringType(), IntType())
        t3 = MapType(StringType(), FloatType())
        
        assert t1.equals(t2) is True
        assert t1.equals(t3) is False


class TestTypeRegistry:
    """类型注册表测试"""
    
    def test_init_builtin_types(self):
        """测试初始化内置类型"""
        registry = TypeRegistry()
        types = registry.list_types()
        
        assert "整数" in types
        assert "浮点数" in types
        assert "字符串" in types
        assert "布尔" in types
        assert "空值" in types
        assert "任意" in types
    
    def test_register_type(self):
        """测试注册类型"""
        registry = TypeRegistry()
        custom_type = ArrayType(IntType())
        
        registry.register_type(custom_type, "MyArray")
        
        assert registry.get_type("MyArray") is not None
        assert registry.get_type("MyArray").equals(ArrayType(IntType()))
    
    def test_get_nonexistent_type(self):
        """测试获取不存在的类型"""
        registry = TypeRegistry()
        assert registry.get_type("NonExistent") is None


class TestTypeEnvironment:
    """类型环境测试"""
    
    def test_define_variable(self):
        """测试定义变量"""
        env = TypeEnvironment()
        env.define_variable("x", IntType())
        
        assert env.get_variable("x").equals(IntType())
    
    def test_get_undefined_variable(self):
        """测试获取未定义变量"""
        env = TypeEnvironment()
        assert env.get_variable("undefined") is None
    
    def test_define_function(self):
        """测试定义函数"""
        env = TypeEnvironment()
        func_type = FunctionType([IntType(), IntType()], IntType())
        
        env.define_function("add", func_type)
        
        assert env.get_function("add").equals(func_type)
    
    def test_scope_inheritance(self):
        """测试作用域继承"""
        parent = TypeEnvironment()
        parent.define_variable("x", IntType())
        
        child = parent.push_scope()
        child.define_variable("y", StringType())
        
        assert child.get_variable("x").equals(IntType())
        assert child.get_variable("y").equals(StringType())


class TestTypeChecker:
    """类型检查器测试"""
    
    def test_init(self):
        """测试初始化"""
        checker = TypeChecker()
        assert checker.env is not None
        assert len(checker.get_errors()) == 0
    
    def test_check_int(self):
        """测试检查整数"""
        checker = TypeChecker()
        
        class MockNum:
            pass
        
        result = checker._check_Num(MockNum())
        assert result.equals(IntType())


class TestTypeInferrer:
    """类型推断器测试"""
    
    def test_infer_nil(self):
        """测试推断空值"""
        inferrer = TypeInferrer()
        result = inferrer._infer_node(None)
        assert result.equals(NilType())
    
    def test_infer_undefined_variable(self):
        """测试推断未定义变量"""
        inferrer = TypeInferrer()
        
        # 测试未定义的变量应返回 AnyType
        class MockWord:
            name = "undefined_var"
        
        result = inferrer._infer_node(MockWord())
        assert result.equals(AnyType())
    
    def test_infer_defined_variable(self):
        """测试推断已定义变量"""
        inferrer = TypeInferrer()
        inferrer.env.define_variable("myVar", IntType())
        
        # 测试环境变量定义功能
        var_type = inferrer.env.get_variable("myVar")
        assert var_type is not None
        assert var_type.equals(IntType())


class TestTypeUtilities:
    """类型工具函数测试"""
    
    def test_make_optional(self):
        """测试创建可选类型"""
        t = make_optional(IntType())
        assert t.kind == YanTypeKind.OPTIONAL
        assert t.nullable is True
    
    def test_make_array(self):
        """测试创建数组类型"""
        t = make_array(IntType())
        assert t.kind == YanTypeKind.ARRAY
        assert t.element_type.equals(IntType())
    
    def test_make_map(self):
        """测试创建映射类型"""
        t = make_map(StringType(), IntType())
        assert t.kind == YanTypeKind.MAP
        assert t.key_type.equals(StringType())
        assert t.value_type.equals(IntType())
    
    def test_make_union(self):
        """测试创建联合类型"""
        t = make_union([IntType(), FloatType()])
        assert t.kind == YanTypeKind.UNION
        assert len(t.types) == 2
    
    def test_make_function(self):
        """测试创建函数类型"""
        t = make_function([IntType(), IntType()], IntType())
        assert t.kind == YanTypeKind.FUNCTION
        assert len(t.param_types) == 2
        assert t.return_type.equals(IntType())


class TestCommonType:
    """公共类型测试"""
    
    def test_common_type_empty(self):
        """测试空列表的公共类型"""
        t = common_type([])
        assert t.kind == YanTypeKind.ANY
    
    def test_common_type_any(self):
        """测试包含any的公共类型"""
        t = common_type([IntType(), AnyType()])
        assert t.kind == YanTypeKind.ANY
    
    def test_common_type_numeric(self):
        """测试数值类型的公共类型"""
        t = common_type([IntType(), FloatType()])
        assert t.kind == YanTypeKind.FLOAT
    
    def test_common_type_same(self):
        """测试相同类型的公共类型"""
        t = common_type([IntType(), IntType()])
        assert t.kind == YanTypeKind.INT
    
    def test_common_type_bool(self):
        """测试布尔类型的公共类型"""
        t = common_type([BoolType(), BoolType()])
        assert t.kind == YanTypeKind.BOOL
    
    def test_common_type_string(self):
        """测试字符串类型的公共类型"""
        t = common_type([StringType(), StringType()])
        assert t.kind == YanTypeKind.STRING


class TestTypePredicates:
    """类型谓词测试"""
    
    def test_is_numeric_type(self):
        """测试数值类型检查"""
        assert is_numeric_type(IntType()) is True
        assert is_numeric_type(FloatType()) is True
        assert is_numeric_type(StringType()) is False
    
    def test_is_truthy_type(self):
        """测试真值类型检查"""
        assert is_truthy_type(IntType()) is True
        assert is_truthy_type(StringType()) is True
        assert is_truthy_type(BoolType()) is True
        assert is_truthy_type(NilType()) is False
        assert is_truthy_type(AnyType()) is True


class TestGlobalRegistry:
    """全局注册表测试"""
    
    def test_get_global_registry(self):
        """测试获取全局注册表"""
        registry = get_global_registry()
        assert registry is not None
        assert isinstance(registry, TypeRegistry)
    
    def test_get_builtin_type(self):
        """测试获取内置类型"""
        t = get_builtin_type("整数")
        assert t is not None
        assert t.equals(IntType())


class TestTypeError:
    """类型错误测试"""
    
    def test_type_error(self):
        """测试类型错误"""
        err = TypeError("类型不匹配")
        assert "类型不匹配" in str(err)
    
    def test_type_error_with_location(self):
        """测试带位置的类型错误"""
        err = TypeError("类型不匹配", line=10, column=5)
        assert "行 10" in str(err)
        assert "类型不匹配" in str(err)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])