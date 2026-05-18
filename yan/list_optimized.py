#!/usr/bin/env python3
"""
言语言惰性列表优化

支持流式处理和延迟计算
"""

from typing import Callable, Iterator, Optional, Any, List, TypeVar, Generic
from functools import wraps
import itertools

T = TypeVar('T')
U = TypeVar('U')


class LazyList(Generic[T]):
    """惰性列表，支持流式处理
    
    特点：
    - 延迟计算：操作不会立即执行，直到实际需要结果
    - 流式处理：可以处理无限序列
    - 内存高效：不需要创建中间列表
    """
    
    def __init__(
        self,
        source: Any,
        operations: Optional[List[tuple]] = None
    ):
        """初始化惰性列表
        
        Args:
            source: 数据源（可迭代对象或生成器）
            operations: 已有的操作列表 [(op_name, func), ...]
        """
        self._source = source
        self._operations = operations or []
        self._cached: Optional[List[T]] = None
    
    def map(self, func: Callable[[T], U]) -> 'LazyList[U]':
        """映射操作
        
        Args:
            func: 转换函数
        
        Returns:
            新的惰性列表
        """
        return LazyList(self._source, self._operations + [('map', func)])
    
    def filter(self, pred: Callable[[T], bool]) -> 'LazyList[T]':
        """过滤操作
        
        Args:
            pred: 谓词函数
        
        Returns:
            新的惰性列表
        """
        return LazyList(self._source, self._operations + [('filter', pred)])
    
    def take(self, n: int) -> 'LazyList[T]':
        """取前n个元素
        
        Args:
            n: 元素数量
        
        Returns:
            新的惰性列表
        """
        return LazyList(self._source, self._operations + [('take', n)])
    
    def drop(self, n: int) -> 'LazyList[T]':
        """跳过前n个元素
        
        Args:
            n: 跳过的元素数量
        
        Returns:
            新的惰性列表
        """
        return LazyList(self._source, self._operations + [('drop', n)])
    
    def take_while(self, pred: Callable[[T], bool]) -> 'LazyList[T]':
        """取满足条件的连续元素
        
        Args:
            pred: 谓词函数
        
        Returns:
            新的惰性列表
        """
        return LazyList(self._source, self._operations + [('take_while', pred)])
    
    def drop_while(self, pred: Callable[[T], bool]) -> 'LazyList[T]':
        """跳过满足条件的连续元素
        
        Args:
            pred: 谓词函数
        
        Returns:
            新的惰性列表
        """
        return LazyList(self._source, self._operations + [('drop_while', pred)])
    
    def flat_map(self, func: Callable[[T], List[U]]) -> 'LazyList[U]':
        """扁平化映射
        
        Args:
            func: 返回列表的函数
        
        Returns:
            新的惰性列表
        """
        return LazyList(self._source, self._operations + [('flat_map', func)])
    
    def zip(self, other: 'LazyList[U]') -> 'LazyList[tuple[T, U]]':
        """拉链操作
        
        Args:
            other: 另一个惰性列表
        
        Returns:
            新的惰性列表
        """
        return LazyList((self._source, other._source), self._operations + [('zip', other)])
    
    def enumerate(self) -> 'LazyList[tuple[int, T]]':
        """枚举操作
        
        Returns:
            新的惰性列表
        """
        return LazyList(self._source, self._operations + [('enumerate', None)])
    
    def _apply_operations(self, data) -> Iterator:
        """应用所有操作
        
        Args:
            data: 输入数据
        
        Yields:
            处理后的元素
        """
        iterator = iter(data) if not hasattr(data, '__iter__') else data
        
        for op_name, op_func in self._operations:
            if op_name == 'map':
                iterator = map(op_func, iterator)
            elif op_name == 'filter':
                iterator = filter(op_func, iterator)
            elif op_name == 'take':
                iterator = itertools.islice(iterator, op_func)
            elif op_name == 'drop':
                iterator = itertools.islice(iterator, op_func, None)
            elif op_name == 'take_while':
                iterator = itertools.takewhile(op_func, iterator)
            elif op_name == 'drop_while':
                iterator = itertools.dropwhile(op_func, iterator)
            elif op_name == 'flat_map':
                iterator = itertools.chain.from_iterable(
                    map(lambda x: op_func(x) or [], iterator)
                )
            elif op_name == 'enumerate':
                iterator = enumerate(iterator)
            elif op_name == 'zip':
                other_source = op_func
                other_iter = iter(other_source._apply_operations(other_source._source))
                iterator = zip(iterator, other_iter)
        
        return iterator
    
    def to_list(self) -> List[T]:
        """转换为普通列表（触发计算）"""
        if self._cached is not None:
            return self._cached
        
        result = list(self._apply_operations(self._source))
        self._cached = result
        return result
    
    def __iter__(self) -> Iterator[T]:
        """迭代器接口"""
        return self._apply_operations(self._source)
    
    def __len__(self) -> int:
        """获取长度（会触发完整计算）"""
        return len(self.to_list())
    
    def __getitem__(self, index: int) -> T:
        """索引访问（会触发计算）"""
        return self.to_list()[index]
    
    def first(self, default: Optional[T] = None) -> Optional[T]:
        """获取第一个元素"""
        for item in self:
            return item
        return default
    
    def is_empty(self) -> bool:
        """检查是否为空"""
        return self.first() is None
    
    def stream(self) -> Iterator[T]:
        """返回流式迭代器"""
        return self._apply_operations(self._source)
    
    def pipe(self, func: Callable[['LazyList[T]'], 'LazyList[U]']) -> 'LazyList[U]':
        """管道操作
        
        Args:
            func: 接收惰性列表并返回惰性列表的函数
        
        Returns:
            新的惰性列表
        """
        return func(self)


class LazyListBuilder:
    """惰性列表构建器"""
    
    def __init__(self):
        self._items: List[T] = []
    
    def add(self, item: T) -> 'LazyListBuilder':
        """添加元素"""
        self._items.append(item)
        return self
    
    def add_all(self, items: List[T]) -> 'LazyListBuilder':
        """批量添加元素"""
        self._items.extend(items)
        return self
    
    def build(self) -> LazyList[T]:
        """构建惰性列表"""
        return LazyList(self._items)
    
    @staticmethod
    def from_iterable(source) -> LazyList:
        """从可迭代对象创建"""
        return LazyList(source)
    
    @staticmethod
    def range(start: int, stop: Optional[int] = None, step: int = 1) -> LazyList[int]:
        """创建惰性范围"""
        if stop is None:
            return LazyList(range(start))
        return LazyList(range(start, stop, step))
    
    @staticmethod
    def repeat(value: T, times: Optional[int] = None) -> LazyList[T]:
        """创建重复值惰性列表"""
        if times is None:
            return LazyList(itertools.repeat(value))
        return LazyList(itertools.repeat(value, times))
    
    @staticmethod
    def generate(func: Callable[[], T], times: Optional[int] = None) -> LazyList[T]:
        """创建生成器惰性列表"""
        if times is None:
            return LazyList(iter(func))
        return LazyList(itertools.islice(iter(func), times))


def lazy(func: Callable) -> Callable:
    """将函数转换为惰性版本
    
    Args:
        func: 返回列表的函数
    
    Returns:
        返回惰性列表的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return LazyList(func(*args, **kwargs))
    return wrapper


def pipeline(source: List[T]) -> LazyList[T]:
    """创建管道
    
    Args:
        source: 数据源
    
    Returns:
        惰性列表
    """
    return LazyList(source)


# 言语言内置函数的惰性版本
def 皆_lazy(func: Callable, source: List) -> LazyList:
    """惰性映射"""
    return LazyList(source).map(func)


def 只_lazy(pred: Callable, source: List) -> LazyList:
    """惰性过滤"""
    return LazyList(source).filter(pred)


def 归_lazy(func: Callable, initial: Any, source: List) -> Any:
    """归约操作（需要完整计算）"""
    return LazyList(source).to_list()  # 先触发计算再归约
