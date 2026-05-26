"""
言语言输入验证框架
"""

import re
from typing import Dict, List, Any, Callable, Optional, Union
from dataclasses import dataclass


class ValidationError(Exception):
    """验证错误"""
    pass


class ValidationResult:
    """验证结果"""
    
    def __init__(self, valid: bool, errors: List[str] = None):
        self.valid = valid
        self.errors = errors or []
    
    def __bool__(self):
        return self.valid
    
    def __repr__(self):
        return f"ValidationResult(valid={self.valid}, errors={self.errors})"


@dataclass
class Validator:
    """验证器基类"""
    name: str
    description: str = ""
    
    def validate(self, value: Any) -> ValidationResult:
        """验证值"""
        raise NotImplementedError


class RequiredValidator(Validator):
    """必填验证器"""
    
    def __init__(self):
        super().__init__('required', '必填字段')
    
    def validate(self, value: Any) -> ValidationResult:
        if value is None or value == '' or (isinstance(value, list) and len(value) == 0):
            return ValidationResult(False, ['该字段为必填项'])
        return ValidationResult(True)


class TypeValidator(Validator):
    """类型验证器"""
    
    def __init__(self, expected_type: type):
        super().__init__('type', f'类型必须为 {expected_type.__name__}')
        self.expected_type = expected_type
    
    def validate(self, value: Any) -> ValidationResult:
        if not isinstance(value, self.expected_type):
            return ValidationResult(False, [f'类型错误，期望 {self.expected_type.__name__}，实际 {type(value).__name__}'])
        return ValidationResult(True)


class LengthValidator(Validator):
    """长度验证器"""
    
    def __init__(self, min_length: int = None, max_length: int = None):
        description = '长度验证'
        if min_length is not None and max_length is not None:
            description = f'长度必须在 {min_length} 到 {max_length} 之间'
        elif min_length is not None:
            description = f'长度至少为 {min_length}'
        elif max_length is not None:
            description = f'长度最多为 {max_length}'
        
        super().__init__('length', description)
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, value: Any) -> ValidationResult:
        if not isinstance(value, (str, list, tuple)):
            return ValidationResult(False, ['不支持的类型，仅支持字符串、列表、元组'])
        
        length = len(value)
        errors = []
        
        if self.min_length is not None and length < self.min_length:
            errors.append(f'长度不足，最少需要 {self.min_length} 个字符/元素')
        
        if self.max_length is not None and length > self.max_length:
            errors.append(f'长度超限，最多允许 {self.max_length} 个字符/元素')
        
        return ValidationResult(len(errors) == 0, errors)


class RangeValidator(Validator):
    """范围验证器"""
    
    def __init__(self, min_val: float = None, max_val: float = None):
        description = '范围验证'
        if min_val is not None and max_val is not None:
            description = f'值必须在 {min_val} 到 {max_val} 之间'
        elif min_val is not None:
            description = f'值必须大于等于 {min_val}'
        elif max_val is not None:
            description = f'值必须小于等于 {max_val}'
        
        super().__init__('range', description)
        self.min_val = min_val
        self.max_val = max_val
    
    def validate(self, value: Any) -> ValidationResult:
        if not isinstance(value, (int, float)):
            return ValidationResult(False, ['不支持的类型，仅支持数字'])
        
        errors = []
        
        if self.min_val is not None and value < self.min_val:
            errors.append(f'值太小，最小允许 {self.min_val}')
        
        if self.max_val is not None and value > self.max_val:
            errors.append(f'值太大，最大允许 {self.max_val}')
        
        return ValidationResult(len(errors) == 0, errors)


class PatternValidator(Validator):
    """正则表达式验证器"""
    
    def __init__(self, pattern: str, description: str = None):
        super().__init__('pattern', description or f'必须匹配模式 {pattern}')
        self.pattern = re.compile(pattern)
    
    def validate(self, value: Any) -> ValidationResult:
        if not isinstance(value, str):
            return ValidationResult(False, ['不支持的类型，仅支持字符串'])
        
        if not self.pattern.match(value):
            return ValidationResult(False, [f'格式不正确，{self.description}'])
        
        return ValidationResult(True)


class EmailValidator(PatternValidator):
    """邮箱验证器"""
    
    def __init__(self):
        super().__init__(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            '请输入有效的邮箱地址'
        )


class PhoneValidator(PatternValidator):
    """手机号验证器"""
    
    def __init__(self):
        super().__init__(
            r'^1[3-9]\d{9}$',
            '请输入有效的手机号码'
        )


class URLValidator(PatternValidator):
    """URL验证器"""
    
    def __init__(self):
        super().__init__(
            r'^https?://[\w.-]+(?:/[\w./?%&=-]*)?$',
            '请输入有效的URL地址'
        )


class ChoiceValidator(Validator):
    """选项验证器"""
    
    def __init__(self, choices: List[Any]):
        super().__init__('choice', f'必须是以下选项之一: {choices}')
        self.choices = choices
    
    def validate(self, value: Any) -> ValidationResult:
        if value not in self.choices:
            return ValidationResult(False, [f'值不在允许的选项中，允许的值: {self.choices}'])
        return ValidationResult(True)


class CustomValidator(Validator):
    """自定义验证器"""
    
    def __init__(self, func: Callable[[Any], ValidationResult], name: str = 'custom'):
        super().__init__(name, '自定义验证')
        self.func = func
    
    def validate(self, value: Any) -> ValidationResult:
        try:
            return self.func(value)
        except Exception as e:
            return ValidationResult(False, [f'验证失败: {str(e)}'])


class ValidatorChain:
    """验证器链"""
    
    def __init__(self, validators: List[Validator] = None):
        self.validators = validators or []
    
    def add(self, validator: Validator) -> 'ValidatorChain':
        """添加验证器"""
        self.validators.append(validator)
        return self
    
    def validate(self, value: Any) -> ValidationResult:
        """依次执行所有验证器"""
        errors = []
        
        for validator in self.validators:
            result = validator.validate(value)
            if not result.valid:
                errors.extend(result.errors)
        
        return ValidationResult(len(errors) == 0, errors)


class FieldValidator:
    """字段验证器"""
    
    def __init__(self, field_name: str, validators: List[Validator]):
        self.field_name = field_name
        self.validators = validators
    
    def validate(self, value: Any) -> ValidationResult:
        """验证字段"""
        chain = ValidatorChain(self.validators)
        result = chain.validate(value)
        
        if not result.valid:
            result.errors = [f'{self.field_name}: {error}' for error in result.errors]
        
        return result


class FormValidator:
    """表单验证器"""
    
    def __init__(self):
        self.fields: Dict[str, FieldValidator] = {}
    
    def add_field(self, field_name: str, *validators: Validator):
        """添加字段验证"""
        self.fields[field_name] = FieldValidator(field_name, list(validators))
        return self
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """验证整个表单"""
        all_errors = []
        
        for field_name, validator in self.fields.items():
            value = data.get(field_name)
            result = validator.validate(value)
            if not result.valid:
                all_errors.extend(result.errors)
        
        return ValidationResult(len(all_errors) == 0, all_errors)


class YanCodeValidator:
    """言语言代码验证器"""
    
    def __init__(self):
        pass
    
    def validate_syntax(self, code: str) -> ValidationResult:
        """验证语法"""
        from lexer import Lexer
        from parser import Parser
        
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(code)
            
            parser = Parser()
            parser.parse(tokens)
            
            return ValidationResult(True)
        except Exception as e:
            return ValidationResult(False, [f'语法错误: {str(e)}'])
    
    def validate_security(self, code: str) -> ValidationResult:
        """验证安全性"""
        dangerous_patterns = [
            (r'打开\s*\(', '文件操作可能存在安全风险'),
            (r'读文件\s*\(', '文件读取可能存在安全风险'),
            (r'写文件\s*\(', '文件写入可能存在安全风险'),
            (r'删文件\s*\(', '文件删除可能存在安全风险'),
            (r'建目录\s*\(', '目录创建可能存在安全风险'),
            (r'删目录\s*\(', '目录删除可能存在安全风险'),
        ]
        
        errors = []
        for pattern, message in dangerous_patterns:
            if re.search(pattern, code):
                errors.append(message)
        
        return ValidationResult(len(errors) == 0, errors)
    
    def validate(self, code: str) -> ValidationResult:
        """完整验证"""
        syntax_result = self.validate_syntax()
        if not syntax_result.valid:
            return syntax_result
        
        security_result = self.validate_security(code)
        if not security_result.valid:
            return security_result
        
        return ValidationResult(True)


# 便捷函数
def validate_required(value: Any) -> bool:
    """检查是否为空"""
    return RequiredValidator().validate(value).valid


def validate_type(value: Any, expected_type: type) -> bool:
    """检查类型"""
    return TypeValidator(expected_type).validate(value).valid


def validate_length(value: Any, min_len: int = None, max_len: int = None) -> bool:
    """检查长度"""
    return LengthValidator(min_len, max_len).validate(value).valid


def validate_range(value: Any, min_val: float = None, max_val: float = None) -> bool:
    """检查范围"""
    return RangeValidator(min_val, max_val).validate(value).valid


def validate_email(value: str) -> bool:
    """检查邮箱"""
    return EmailValidator().validate(value).valid


def validate_phone(value: str) -> bool:
    """检查手机号"""
    return PhoneValidator().validate(value).valid


def validate_url(value: str) -> bool:
    """检查URL"""
    return URLValidator().validate(value).valid


def validate_choice(value: Any, choices: List[Any]) -> bool:
    """检查选项"""
    return ChoiceValidator(choices).validate(value).valid


def validate_yan_code(code: str) -> ValidationResult:
    """验证言语言代码"""
    return YanCodeValidator().validate(code)