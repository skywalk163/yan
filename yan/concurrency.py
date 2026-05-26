"""
言语言并发支持模块
提供多线程和协程功能
"""

import threading
import queue
import asyncio
import time
import concurrent.futures
from typing import Any, Callable, List, Optional, Dict, Coroutine
from dataclasses import dataclass, field
from enum import Enum


class ConcurrencyMode(Enum):
    """并发模式"""
    THREAD = "thread"       # 多线程
    PROCESS = "process"     # 多进程
    COROUTINE = "coroutine" # 协程
    ASYNC = "async"         # 异步


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[Exception] = None
    start_time: float = 0.0
    end_time: float = 0.0
    
    @property
    def duration(self) -> float:
        """任务执行时间"""
        return self.end_time - self.start_time
    
    def to_dict(self):
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "error": str(self.error) if self.error else None,
            "duration": self.duration
        }


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    func: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    future: Optional[concurrent.futures.Future] = None
    result: Optional[TaskResult] = None


class YanThreadPool:
    """线程池管理器"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or (threading.active_count() * 5)
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="yan-thread-"
        )
        self._tasks: Dict[str, TaskInfo] = {}
        self._task_id_counter = 1
        self._lock = threading.Lock()
    
    def submit(self, func: Callable, *args, **kwargs) -> str:
        """提交任务到线程池"""
        with self._lock:
            task_id = f"task_{self._task_id_counter}"
            self._task_id_counter += 1
        
        def wrapper():
            start_time = time.perf_counter()
            info = self._tasks[task_id]
            info.status = TaskStatus.RUNNING
            
            try:
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                info.status = TaskStatus.COMPLETED
                info.result = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.COMPLETED,
                    result=result,
                    start_time=start_time,
                    end_time=end_time
                )
                return result
            except Exception as e:
                end_time = time.perf_counter()
                info.status = TaskStatus.FAILED
                info.result = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=e,
                    start_time=start_time,
                    end_time=end_time
                )
                raise
        
        info = TaskInfo(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs
        )
        self._tasks[task_id] = info
        
        future = self._executor.submit(wrapper)
        info.future = future
        
        return task_id
    
    def submit_batch(self, tasks: List[tuple]) -> List[str]:
        """批量提交任务"""
        task_ids = []
        for func, args, kwargs in tasks:
            task_id = self.submit(func, *args, **kwargs)
            task_ids.append(task_id)
        return task_ids
    
    def get_result(self, task_id: str, timeout: float = None) -> Optional[TaskResult]:
        """获取任务结果"""
        if task_id not in self._tasks:
            return None
        
        info = self._tasks[task_id]
        
        if info.result:
            return info.result
        
        if info.future:
            try:
                info.future.result(timeout=timeout)
                return info.result
            except concurrent.futures.TimeoutError:
                return None
            except Exception:
                return info.result
        
        return None
    
    def wait(self, task_ids: List[str], timeout: float = None) -> List[TaskResult]:
        """等待多个任务完成"""
        futures = []
        task_map = {}
        
        for task_id in task_ids:
            if task_id in self._tasks and self._tasks[task_id].future:
                futures.append(self._tasks[task_id].future)
                task_map[id(self._tasks[task_id].future)] = task_id
        
        results = []
        for future in concurrent.futures.as_completed(futures, timeout=timeout):
            task_id = task_map.get(id(future))
            if task_id:
                result = self.get_result(task_id)
                if result:
                    results.append(result)
        
        return results
    
    def wait_all(self, timeout: float = None) -> List[TaskResult]:
        """等待所有任务完成"""
        return self.wait(list(self._tasks.keys()), timeout=timeout)
    
    def cancel(self, task_id: str) -> bool:
        """取消任务"""
        if task_id not in self._tasks:
            return False
        
        info = self._tasks[task_id]
        
        if info.status == TaskStatus.PENDING and info.future:
            success = info.future.cancel()
            if success:
                info.status = TaskStatus.CANCELLED
                info.result = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.CANCELLED,
                    start_time=0,
                    end_time=time.perf_counter()
                )
            return success
        
        return False
    
    def shutdown(self, wait: bool = True):
        """关闭线程池"""
        self._executor.shutdown(wait=wait)
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        if task_id in self._tasks:
            return self._tasks[task_id].status
        return None
    
    def list_tasks(self) -> List[TaskInfo]:
        """列出所有任务"""
        return list(self._tasks.values())
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        stats = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "total": len(self._tasks)
        }
        
        for info in self._tasks.values():
            status = info.status.value
            if status in stats:
                stats[status] += 1
        
        return stats


class YanCoroutineManager:
    """协程管理器"""
    
    def __init__(self):
        self._loop = None
        self._tasks: Dict[str, asyncio.Task] = {}
        self._task_id_counter = 1
        self._results: Dict[str, TaskResult] = {}
    
    @property
    def loop(self):
        """获取事件循环"""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop
    
    async def create_task(self, coro: Coroutine, task_id: str = None) -> str:
        """创建协程任务"""
        if task_id is None:
            task_id = f"coro_{self._task_id_counter}"
            self._task_id_counter += 1
        
        async def wrapper():
            start_time = time.perf_counter()
            
            try:
                result = await coro
                end_time = time.perf_counter()
                self._results[task_id] = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.COMPLETED,
                    result=result,
                    start_time=start_time,
                    end_time=end_time
                )
                return result
            except Exception as e:
                end_time = time.perf_counter()
                self._results[task_id] = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=e,
                    start_time=start_time,
                    end_time=end_time
                )
                raise
        
        task = self.loop.create_task(wrapper())
        self._tasks[task_id] = task
        
        return task_id
    
    def run_coroutine(self, coro: Coroutine) -> Any:
        """运行协程并返回结果"""
        return self.loop.run_until_complete(coro)
    
    async def gather(self, *coros: Coroutine) -> List[Any]:
        """并发运行多个协程"""
        return await asyncio.gather(*coros)
    
    async def wait(self, task_ids: List[str], timeout: float = None) -> List[TaskResult]:
        """等待多个任务完成"""
        tasks = []
        for task_id in task_ids:
            if task_id in self._tasks:
                tasks.append(self._tasks[task_id])
        
        if tasks:
            done, pending = await asyncio.wait(tasks, timeout=timeout)
            
            for task in pending:
                task.cancel()
            
            await asyncio.gather(*pending, return_exceptions=True)
        
        results = []
        for task_id in task_ids:
            if task_id in self._results:
                results.append(self._results[task_id])
        
        return results
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self._results.get(task_id)
    
    def cancel(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            if not task.done():
                task.cancel()
                self._results[task_id] = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.CANCELLED,
                    start_time=0,
                    end_time=time.perf_counter()
                )
                return True
        return False
    
    def close(self):
        """关闭协程管理器"""
        for task in self._tasks.values():
            if not task.done():
                task.cancel()
        
        if self._loop:
            self._loop.close()
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        stats = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "total": len(self._tasks)
        }
        
        for task_id, task in self._tasks.items():
            if task.done():
                if task_id in self._results:
                    status = self._results[task_id].status.value
                else:
                    try:
                        task.result()
                        status = "completed"
                    except asyncio.CancelledError:
                        status = "cancelled"
                    except Exception:
                        status = "failed"
                
                if status in stats:
                    stats[status] += 1
            else:
                stats["running"] += 1
        
        return stats


class ConcurrentQueue:
    """线程安全队列"""
    
    def __init__(self, maxsize: int = 0):
        self._queue = queue.Queue(maxsize=maxsize)
    
    def put(self, item: Any, block: bool = True, timeout: float = None):
        """放入元素"""
        self._queue.put(item, block=block, timeout=timeout)
    
    def get(self, block: bool = True, timeout: float = None) -> Any:
        """获取元素"""
        return self._queue.get(block=block, timeout=timeout)
    
    def put_nowait(self, item: Any):
        """非阻塞放入"""
        self._queue.put_nowait(item)
    
    def get_nowait(self) -> Any:
        """非阻塞获取"""
        return self._queue.get_nowait()
    
    def empty(self) -> bool:
        """检查是否为空"""
        return self._queue.empty()
    
    def full(self) -> bool:
        """检查是否已满"""
        return self._queue.full()
    
    def qsize(self) -> int:
        """获取队列大小"""
        return self._queue.qsize()
    
    def task_done(self):
        """标记任务完成"""
        self._queue.task_done()
    
    def join(self):
        """等待所有任务完成"""
        self._queue.join()


class ConcurrentDict:
    """线程安全字典"""
    
    def __init__(self):
        self._dict = {}
        self._lock = threading.Lock()
    
    def __getitem__(self, key: Any) -> Any:
        """获取值"""
        with self._lock:
            return self._dict[key]
    
    def __setitem__(self, key: Any, value: Any):
        """设置值"""
        with self._lock:
            self._dict[key] = value
    
    def __delitem__(self, key: Any):
        """删除值"""
        with self._lock:
            del self._dict[key]
    
    def __contains__(self, key: Any) -> bool:
        """检查是否包含键"""
        with self._lock:
            return key in self._dict
    
    def __len__(self) -> int:
        """获取长度"""
        with self._lock:
            return len(self._dict)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """安全获取"""
        with self._lock:
            return self._dict.get(key, default)
    
    def setdefault(self, key: Any, default: Any = None) -> Any:
        """设置默认值"""
        with self._lock:
            return self._dict.setdefault(key, default)
    
    def update(self, other: Dict):
        """更新字典"""
        with self._lock:
            self._dict.update(other)
    
    def keys(self) -> List[Any]:
        """获取键列表"""
        with self._lock:
            return list(self._dict.keys())
    
    def values(self) -> List[Any]:
        """获取值列表"""
        with self._lock:
            return list(self._dict.values())
    
    def items(self) -> List[tuple]:
        """获取键值对列表"""
        with self._lock:
            return list(self._dict.items())
    
    def clear(self):
        """清空字典"""
        with self._lock:
            self._dict.clear()


class RWLock:
    """读写锁"""
    
    def __init__(self):
        self._read_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._read_count = 0
    
    def acquire_read(self):
        """获取读锁"""
        with self._read_lock:
            self._read_count += 1
            if self._read_count == 1:
                self._write_lock.acquire()
    
    def release_read(self):
        """释放读锁"""
        with self._read_lock:
            self._read_count -= 1
            if self._read_count == 0:
                self._write_lock.release()
    
    def acquire_write(self):
        """获取写锁"""
        self._write_lock.acquire()
    
    def release_write(self):
        """释放写锁"""
        self._write_lock.release()
    
    def __enter__(self):
        """上下文管理器（写锁）"""
        self.acquire_write()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.release_write()


class Semaphore:
    """信号量"""
    
    def __init__(self, value: int = 1):
        self._semaphore = threading.Semaphore(value)
    
    def acquire(self, blocking: bool = True, timeout: float = None) -> bool:
        """获取信号量"""
        return self._semaphore.acquire(blocking=blocking, timeout=timeout)
    
    def release(self, n: int = 1):
        """释放信号量"""
        for _ in range(n):
            self._semaphore.release()
    
    def __enter__(self):
        """上下文管理器"""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.release()


class Event:
    """事件"""
    
    def __init__(self):
        self._event = threading.Event()
    
    def set(self):
        """设置事件"""
        self._event.set()
    
    def clear(self):
        """清除事件"""
        self._event.clear()
    
    def is_set(self) -> bool:
        """检查事件是否设置"""
        return self._event.is_set()
    
    def wait(self, timeout: float = None):
        """等待事件"""
        return self._event.wait(timeout=timeout)


class Barrier:
    """屏障"""
    
    def __init__(self, parties: int, action: Optional[Callable] = None):
        self._barrier = threading.Barrier(parties, action=action)
    
    def wait(self, timeout: float = None) -> int:
        """等待所有线程到达屏障"""
        return self._barrier.wait(timeout=timeout)
    
    def abort(self):
        """中断屏障"""
        self._barrier.abort()
    
    @property
    def parties(self) -> int:
        """获取参与方数量"""
        return self._barrier.parties
    
    @property
    def n_waiting(self) -> int:
        """获取等待中的线程数"""
        return self._barrier.n_waiting


# 全局线程池实例
_global_thread_pool = None


def get_global_thread_pool() -> YanThreadPool:
    """获取全局线程池"""
    global _global_thread_pool
    if _global_thread_pool is None:
        _global_thread_pool = YanThreadPool()
    return _global_thread_pool


def thread_pool_executor(max_workers: int = None) -> YanThreadPool:
    """创建线程池"""
    return YanThreadPool(max_workers=max_workers)


def run_async(func: Callable, *args, **kwargs) -> str:
    """异步执行函数"""
    pool = get_global_thread_pool()
    return pool.submit(func, *args, **kwargs)


def async_wait(task_ids: List[str], timeout: float = None) -> List[TaskResult]:
    """等待异步任务完成"""
    pool = get_global_thread_pool()
    return pool.wait(task_ids, timeout=timeout)


# 全局协程管理器实例
_global_coroutine_manager = None


def get_global_coroutine_manager() -> YanCoroutineManager:
    """获取全局协程管理器"""
    global _global_coroutine_manager
    if _global_coroutine_manager is None:
        _global_coroutine_manager = YanCoroutineManager()
    return _global_coroutine_manager


# 装饰器
def async_function(func: Callable) -> Callable:
    """异步函数装饰器"""
    def wrapper(*args, **kwargs):
        pool = get_global_thread_pool()
        return pool.submit(func, *args, **kwargs)
    return wrapper


def coroutine_function(func: Callable) -> Callable:
    """协程函数装饰器"""
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


# 示例使用
if __name__ == "__main__":
    # 线程池示例
    pool = YanThreadPool(max_workers=2)
    
    def task_func(name, delay):
        print(f"任务 {name} 开始")
        time.sleep(delay)
        print(f"任务 {name} 完成")
        return f"结果: {name}"
    
    # 提交任务
    task1 = pool.submit(task_func, "A", 1)
    task2 = pool.submit(task_func, "B", 0.5)
    task3 = pool.submit(task_func, "C", 0.8)
    
    print(f"任务ID: {task1}, {task2}, {task3}")
    print(f"统计信息: {pool.get_stats()}")
    
    # 等待完成
    results = pool.wait_all()
    
    print("\n任务结果:")
    for result in results:
        print(f"{result.task_id}: {result.status.value} - {result.result} (耗时: {result.duration:.2f}s)")
    
    pool.shutdown()
    
    # 协程示例
    cm = YanCoroutineManager()
    
    async def async_task(name, delay):
        print(f"协程 {name} 开始")
        await asyncio.sleep(delay)
        print(f"协程 {name} 完成")
        return f"协程结果: {name}"
    
    # 运行协程
    result = cm.run_coroutine(async_task("协程A", 0.5))
    print(f"\n协程结果: {result}")
    
    cm.close()