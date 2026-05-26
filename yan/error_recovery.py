"""
言语言错误恢复模块（增强版）
提供智能错误恢复和容错执行功能
"""

from typing import List, Dict, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from error import YanError, SourceLocation


@dataclass
class RecoveryAction:
    """恢复操作记录"""
    action_type: str  # 'skip', 'replace', 'insert', 'continue', 'stop'
    location: SourceLocation
    description: str
    applied: bool = False
    original_error: Optional[YanError] = None


@dataclass
class RecoveryResult:
    """恢复结果"""
    success: bool
    errors: List[YanError]
    warnings: List[str]
    actions: List[RecoveryAction]
    final_node: Optional[Any] = None


class RecoveryStrategy:
    """恢复策略基类"""
    
    def __init__(self, priority: int = 100):
        self.priority = priority
    
    def can_recover(self, error: YanError) -> bool:
        """检查是否可以恢复此错误"""
        return False
    
    def recover(self, error: YanError, context: Dict[str, Any]) -> RecoveryAction:
        """执行恢复操作"""
        raise NotImplementedError


class SkipStatementStrategy(RecoveryStrategy):
    """跳过当前语句策略"""
    
    def __init__(self):
        super().__init__(priority=50)
    
    def can_recover(self, error: YanError) -> bool:
        """可以恢复语法错误和解析错误"""
        return error.error_type in ["语法错误", "词法错误"]
    
    def recover(self, error: YanError, context: Dict[str, Any]) -> RecoveryAction:
        return RecoveryAction(
            action_type='skip',
            location=error.location,
            description=f"跳过包含错误的语句",
            original_error=error
        )


class InsertMissingTokenStrategy(RecoveryStrategy):
    """插入缺失令牌策略"""
    
    def __init__(self):
        super().__init__(priority=30)
    
    def can_recover(self, error: YanError) -> bool:
        """检查是否是缺失令牌错误"""
        message = error.message.lower()
        return any(keyword in message for keyword in ["期望", "缺少", "未找到"])
    
    def recover(self, error: YanError, context: Dict[str, Any]) -> RecoveryAction:
        # 分析错误消息，尝试推断缺失的令牌
        message = error.message
        missing_token = "未知"
        
        if "期望 '则'" in message:
            missing_token = "则"
        elif "期望 '于'" in message:
            missing_token = "于"
        elif "期望 '的'" in message:
            missing_token = "的"
        elif "期望标识符" in message:
            missing_token = "变量名"
        
        return RecoveryAction(
            action_type='insert',
            location=error.location,
            description=f"尝试插入缺失的令牌 '{missing_token}'",
            original_error=error
        )


class ReplaceInvalidTokenStrategy(RecoveryStrategy):
    """替换无效令牌策略"""
    
    def __init__(self):
        super().__init__(priority=40)
    
    def can_recover(self, error: YanError) -> bool:
        """检查是否是无效令牌错误"""
        message = error.message.lower()
        return any(keyword in message for keyword in ["无效", "非法", "错误的"])
    
    def recover(self, error: YanError, context: Dict[str, Any]) -> RecoveryAction:
        return RecoveryAction(
            action_type='replace',
            location=error.location,
            description=f"替换无效令牌",
            original_error=error
        )


class ContinueAfterErrorStrategy(RecoveryStrategy):
    """继续执行策略"""
    
    def __init__(self):
        super().__init__(priority=60)
    
    def can_recover(self, error: YanError) -> bool:
        """运行时错误可以继续执行"""
        return error.error_type == "运行时错误"
    
    def recover(self, error: YanError, context: Dict[str, Any]) -> RecoveryAction:
        return RecoveryAction(
            action_type='continue',
            location=error.location,
            description=f"记录错误并继续执行",
            original_error=error
        )


class ErrorRecoveryManager:
    """增强版错误恢复管理器"""
    
    def __init__(self, max_errors: int = 10, enable_recovery: bool = True):
        self.max_errors = max_errors
        self.enable_recovery = enable_recovery
        self.error_count = 0
        self.recovery_actions: List[RecoveryAction] = []
        self.errors: List[YanError] = []
        self.warnings: List[str] = []
        
        # 注册恢复策略
        self.strategies: List[RecoveryStrategy] = [
            InsertMissingTokenStrategy(),
            ReplaceInvalidTokenStrategy(),
            SkipStatementStrategy(),
            ContinueAfterErrorStrategy(),
        ]
        # 按优先级排序
        self.strategies.sort(key=lambda s: s.priority)
    
    def add_strategy(self, strategy: RecoveryStrategy):
        """添加自定义恢复策略"""
        self.strategies.append(strategy)
        self.strategies.sort(key=lambda s: s.priority)
    
    def should_recover(self) -> bool:
        """检查是否应该继续尝试恢复"""
        if not self.enable_recovery:
            return False
        return self.error_count < self.max_errors
    
    def recover(self, error: YanError, context: Dict[str, Any] = None) -> Optional[RecoveryAction]:
        """尝试恢复错误"""
        if not self.should_recover():
            return None
        
        self.error_count += 1
        self.errors.append(error)
        
        # 尝试找到合适的恢复策略
        for strategy in self.strategies:
            if strategy.can_recover(error):
                action = strategy.recover(error, context or {})
                action.applied = True
                self.recovery_actions.append(action)
                return action
        
        # 如果没有找到策略，记录错误
        self.warnings.append(f"无法恢复错误: {error.message}")
        return None
    
    def record_error(self, error: YanError):
        """记录错误但不尝试恢复"""
        self.error_count += 1
        self.errors.append(error)
    
    def get_recovery_summary(self) -> Dict[str, Any]:
        """获取恢复摘要"""
        return {
            'total_errors': self.error_count,
            'recovered_errors': len([a for a in self.recovery_actions if a.applied]),
            'unrecovered_errors': len(self.errors) - len([a for a in self.recovery_actions if a.applied]),
            'warnings': self.warnings,
            'actions': [
                {
                    'type': a.action_type,
                    'location': str(a.location),
                    'description': a.description
                } for a in self.recovery_actions
            ]
        }
    
    def format_summary(self) -> str:
        """格式化恢复摘要"""
        summary = self.get_recovery_summary()
        lines = []
        
        if summary['total_errors'] == 0:
            lines.append("✓ 无错误")
        else:
            lines.append(f"错误统计:")
            lines.append(f"  - 总计: {summary['total_errors']}")
            lines.append(f"  - 已恢复: {summary['recovered_errors']}")
            lines.append(f"  - 未恢复: {summary['unrecovered_errors']}")
            
            if summary['warnings']:
                lines.append("\n警告:")
                for warning in summary['warnings']:
                    lines.append(f"  - {warning}")
            
            if summary['actions']:
                lines.append("\n恢复操作:")
                for action in summary['actions']:
                    lines.append(f"  - [{action['type']}] {action['location']}: {action['description']}")
        
        return "\n".join(lines)
    
    def reset(self):
        """重置状态"""
        self.error_count = 0
        self.recovery_actions.clear()
        self.errors.clear()
        self.warnings.clear()


class ErrorContextCollector:
    """错误上下文收集器"""
    
    def __init__(self):
        self.symbol_table: Dict[str, Any] = {}
        self.call_stack: List[Dict[str, Any]] = []
        self.source_code: str = ""
        self.line_numbers: Dict[int, str] = {}
        self.imported_modules: Set[str] = set()
    
    def add_symbol(self, name: str, value: Any, location: SourceLocation):
        """添加符号到符号表"""
        self.symbol_table[name] = {
            'value': value,
            'location': location,
            'type': type(value).__name__
        }
    
    def push_call(self, func_name: str, location: SourceLocation):
        """压入调用栈"""
        self.call_stack.append({
            'function': func_name,
            'location': location,
            'timestamp': None
        })
    
    def pop_call(self):
        """弹出调用栈"""
        if self.call_stack:
            return self.call_stack.pop()
        return None
    
    def set_source_code(self, code: str):
        """设置源代码"""
        self.source_code = code
        # 建立行号映射
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            self.line_numbers[i] = line
    
    def add_imported_module(self, module_name: str):
        """记录导入的模块"""
        self.imported_modules.add(module_name)
    
    def get_context_for_error(self, error: YanError) -> Dict[str, Any]:
        """获取错误的上下文信息"""
        context = {
            'error': error,
            'line_content': self.line_numbers.get(error.location.line, ""),
            'nearby_symbols': self._get_nearby_symbols(error.location),
            'call_stack': self.call_stack.copy(),
            'imported_modules': list(self.imported_modules)
        }
        return context
    
    def _get_nearby_symbols(self, location: SourceLocation) -> List[Dict[str, Any]]:
        """获取错误位置附近的符号"""
        nearby = []
        for name, info in self.symbol_table.items():
            # 检查符号定义位置是否在错误附近
            sym_loc = info['location']
            if abs(sym_loc.line - location.line) <= 5:
                nearby.append({
                    'name': name,
                    'type': info['type'],
                    'location': str(sym_loc)
                })
        return nearby


# 全局错误恢复管理器
_global_recovery_manager = ErrorRecoveryManager()

# 全局错误上下文收集器
_global_context_collector = ErrorContextCollector()


def get_recovery_manager() -> ErrorRecoveryManager:
    """获取全局错误恢复管理器"""
    return _global_recovery_manager


def get_context_collector() -> ErrorContextCollector:
    """获取全局错误上下文收集器"""
    return _global_context_collector


def enable_error_recovery(enable: bool = True):
    """启用或禁用错误恢复"""
    _global_recovery_manager.enable_recovery = enable


def set_max_errors(max_errors: int):
    """设置最大错误数"""
    _global_recovery_manager.max_errors = max_errors
