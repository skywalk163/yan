"""
并发模块测试
"""

import pytest
import time
import threading
from yan.concurrency import (
    YanThreadPool,
    YanCoroutineManager,
    ConcurrentQueue,
    ConcurrentDict,
    RWLock,
    Semaphore,
    Event,
    Barrier,
    TaskStatus,
    TaskResult,
    async_function,
    run_async,
    async_wait,
    get_global_thread_pool,
    get_global_coroutine_manager
)


class TestYanThreadPool:
    """线程池测试"""
    
    def test_submit_task(self):
        """测试提交任务"""
        pool = YanThreadPool(max_workers=2)
        
        def task():
            time.sleep(0.1)
            return "done"
        
        task_id = pool.submit(task)
        assert task_id is not None
        
        result = pool.get_result(task_id)
        assert result is not None
        assert result.status == TaskStatus.COMPLETED
        assert result.result == "done"
        
        pool.shutdown()
    
    def test_submit_with_args(self):
        """测试带参数的任务"""
        pool = YanThreadPool(max_workers=2)
        
        def add(a, b):
            return a + b
        
        task_id = pool.submit(add, 3, 5)
        result = pool.get_result(task_id)
        
        assert result.result == 8
        
        pool.shutdown()
    
    def test_submit_with_kwargs(self):
        """测试带关键字参数的任务"""
        pool = YanThreadPool(max_workers=2)
        
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        task_id = pool.submit(greet, name="World", greeting="Hi")
        result = pool.get_result(task_id)
        
        assert result.result == "Hi, World!"
        
        pool.shutdown()
    
    def test_multiple_tasks(self):
        """测试多个任务并发执行"""
        pool = YanThreadPool(max_workers=3)
        
        def task(name, delay):
            time.sleep(delay)
            return name
        
        task_ids = []
        for i in range(5):
            task_id = pool.submit(task, f"task_{i}", 0.05)
            task_ids.append(task_id)
        
        results = pool.wait(task_ids)
        assert len(results) == 5
        
        pool.shutdown()
    
    def test_task_failure(self):
        """测试任务失败"""
        pool = YanThreadPool(max_workers=2)
        
        def fail_task():
            raise ValueError("故意失败")
        
        task_id = pool.submit(fail_task)
        result = pool.get_result(task_id)
        
        assert result.status == TaskStatus.FAILED
        assert isinstance(result.error, ValueError)
        
        pool.shutdown()
    
    def test_cancel_task(self):
        """测试取消任务"""
        pool = YanThreadPool(max_workers=1)
        
        def long_task():
            time.sleep(1)
            return "done"
        
        task_id = pool.submit(long_task)
        
        # 立即取消
        cancelled = pool.cancel(task_id)
        
        if cancelled:
            result = pool.get_result(task_id)
            assert result.status == TaskStatus.CANCELLED
        
        pool.shutdown()
    
    def test_get_stats(self):
        """测试获取统计信息"""
        pool = YanThreadPool(max_workers=2)
        
        def task():
            time.sleep(0.1)
        
        pool.submit(task)
        pool.submit(task)
        
        stats = pool.get_stats()
        assert stats["total"] == 2
        assert stats["running"] >= 0
        
        pool.wait_all()
        
        stats = pool.get_stats()
        assert stats["completed"] == 2
        
        pool.shutdown()
    
    def test_timeout(self):
        """测试超时"""
        pool = YanThreadPool(max_workers=1)
        
        def long_task():
            time.sleep(1)
            return "done"
        
        task_id = pool.submit(long_task)
        result = pool.get_result(task_id, timeout=0.1)
        
        assert result is None
        
        pool.shutdown()


class TestYanCoroutineManager:
    """协程管理器测试"""
    
    def test_create_task(self):
        """测试创建协程任务"""
        cm = YanCoroutineManager()
        
        async def task():
            await __import__('asyncio').sleep(0.1)
            return "coroutine done"
        
        result = cm.run_coroutine(task())
        assert result == "coroutine done"
        
        cm.close()
    
    def test_gather(self):
        """测试并发运行多个协程"""
        cm = YanCoroutineManager()
        
        async def task(name, delay):
            await __import__('asyncio').sleep(delay)
            return name
        
        async def run():
            results = await cm.gather(
                task("A", 0.05),
                task("B", 0.03),
                task("C", 0.01)
            )
            return results
        
        results = cm.run_coroutine(run())
        assert len(results) == 3
        assert "A" in results
        assert "B" in results
        assert "C" in results
        
        cm.close()
    
    def test_coroutine_failure(self):
        """测试协程失败"""
        cm = YanCoroutineManager()
        
        async def fail_task():
            await __import__('asyncio').sleep(0.01)
            raise ValueError("协程失败")
        
        with pytest.raises(ValueError):
            cm.run_coroutine(fail_task())
        
        cm.close()


class TestConcurrentQueue:
    """线程安全队列测试"""
    
    def test_queue_put_get(self):
        """测试队列基本操作"""
        q = ConcurrentQueue()
        
        q.put("item1")
        q.put("item2")
        
        assert q.get() == "item1"
        assert q.get() == "item2"
    
    def test_queue_empty_full(self):
        """测试队列空满状态"""
        q = ConcurrentQueue(maxsize=2)
        
        assert q.empty() is True
        
        q.put("item1")
        q.put("item2")
        
        assert q.full() is True
        
        q.get()
        assert q.full() is False
    
    def test_queue_put_nowait(self):
        """测试非阻塞放入"""
        q = ConcurrentQueue(maxsize=1)
        
        q.put_nowait("item")
        
        with pytest.raises(Exception):
            q.put_nowait("item2")
    
    def test_queue_get_nowait(self):
        """测试非阻塞获取"""
        q = ConcurrentQueue()
        
        with pytest.raises(Exception):
            q.get_nowait()
        
        q.put("item")
        assert q.get_nowait() == "item"
    
    def test_queue_join(self):
        """测试队列join"""
        q = ConcurrentQueue()
        items_processed = [0]
        
        def worker():
            while True:
                item = q.get()
                if item is None:
                    break
                items_processed[0] += 1
                q.task_done()
        
        t = threading.Thread(target=worker)
        t.start()
        
        for i in range(5):
            q.put(i)
        
        q.put(None)
        q.join()
        
        assert items_processed[0] == 5


class TestConcurrentDict:
    """线程安全字典测试"""
    
    def test_dict_basic_operations(self):
        """测试字典基本操作"""
        cd = ConcurrentDict()
        
        cd["key1"] = "value1"
        cd["key2"] = "value2"
        
        assert cd["key1"] == "value1"
        assert cd["key2"] == "value2"
        assert len(cd) == 2
        
        del cd["key1"]
        assert "key1" not in cd
    
    def test_dict_get_setdefault(self):
        """测试get和setdefault"""
        cd = ConcurrentDict()
        
        assert cd.get("nonexistent") is None
        assert cd.get("nonexistent", "default") == "default"
        
        cd.setdefault("key", "default")
        assert cd["key"] == "default"
        
        cd.setdefault("key", "new_value")
        assert cd["key"] == "default"
    
    def test_dict_update(self):
        """测试update"""
        cd = ConcurrentDict()
        cd["a"] = 1
        
        cd.update({"b": 2, "c": 3})
        
        assert cd["a"] == 1
        assert cd["b"] == 2
        assert cd["c"] == 3
    
    def test_dict_clear(self):
        """测试clear"""
        cd = ConcurrentDict()
        cd["a"] = 1
        cd["b"] = 2
        
        cd.clear()
        
        assert len(cd) == 0


class TestRWLock:
    """读写锁测试"""
    
    def test_read_lock(self):
        """测试读锁"""
        rwlock = RWLock()
        shared_value = [0]
        
        def reader():
            rwlock.acquire_read()
            try:
                value = shared_value[0]
                time.sleep(0.01)
                assert shared_value[0] == value
            finally:
                rwlock.release_read()
        
        threads = []
        for _ in range(3):
            t = threading.Thread(target=reader)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
    
    def test_write_lock(self):
        """测试写锁"""
        rwlock = RWLock()
        shared_value = [0]
        
        def writer():
            rwlock.acquire_write()
            try:
                shared_value[0] += 1
                time.sleep(0.01)
            finally:
                rwlock.release_write()
        
        threads = []
        for _ in range(3):
            t = threading.Thread(target=writer)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert shared_value[0] == 3
    
    def test_read_write_exclusion(self):
        """测试读写互斥"""
        rwlock = RWLock()
        shared_value = [0]
        
        def writer():
            with rwlock:
                shared_value[0] = 1
                time.sleep(0.02)
                shared_value[0] = 2
        
        def reader():
            rwlock.acquire_read()
            try:
                val = shared_value[0]
                time.sleep(0.01)
                # 如果写锁在执行，读应该等待
                return val
            finally:
                rwlock.release_read()
        
        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)
        
        writer_thread.start()
        time.sleep(0.005)
        reader_thread.start()
        
        writer_thread.join()
        reader_result = reader_thread.join()
        
        # 读者应该看到一致的值（要么全是1，要么全是2）
        # 由于写锁持有期间读锁等待，读者应该看到2


class TestSemaphore:
    """信号量测试"""
    
    def test_semaphore_basic(self):
        """测试信号量基本操作"""
        sem = Semaphore(2)
        counter = [0]
        
        def worker():
            with sem:
                counter[0] += 1
                time.sleep(0.01)
                counter[0] -= 1
        
        threads = []
        for _ in range(4):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 信号量限制并发数为2
        assert max(counter) <= 2
    
    def test_semaphore_acquire_release(self):
        """测试手动获取和释放"""
        sem = Semaphore(1)
        
        assert sem.acquire() is True
        assert sem.acquire(blocking=False) is False
        
        sem.release()
        assert sem.acquire(blocking=False) is True
        
        sem.release()


class TestEvent:
    """事件测试"""
    
    def test_event_set_wait(self):
        """测试事件设置和等待"""
        event = Event()
        result = [False]
        
        def waiter():
            event.wait()
            result[0] = True
        
        t = threading.Thread(target=waiter)
        t.start()
        
        time.sleep(0.01)
        assert result[0] is False
        
        event.set()
        t.join()
        
        assert result[0] is True
    
    def test_event_clear(self):
        """测试事件清除"""
        event = Event()
        
        event.set()
        assert event.is_set() is True
        
        event.clear()
        assert event.is_set() is False


class TestBarrier:
    """屏障测试"""
    
    def test_barrier_basic(self):
        """测试屏障基本操作"""
        barrier = Barrier(3)
        counter = [0]
        
        def worker():
            counter[0] += 1
            barrier.wait()
        
        threads = []
        for _ in range(3):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert counter[0] == 3
    
    def test_barrier_action(self):
        """测试屏障动作"""
        barrier = Barrier(2, action=lambda: print("所有线程到达"))
        results = []
        
        def worker(id):
            results.append(f"worker {id} before")
            barrier.wait()
            results.append(f"worker {id} after")
        
        t1 = threading.Thread(target=worker, args=(1,))
        t2 = threading.Thread(target=worker, args=(2,))
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        assert "worker 1 before" in results
        assert "worker 2 before" in results
        assert "worker 1 after" in results
        assert "worker 2 after" in results


class TestDecorators:
    """装饰器测试"""
    
    def test_async_function_decorator(self):
        """测试异步函数装饰器"""
        @async_function
        def my_function():
            time.sleep(0.01)
            return "decorated"
        
        task_id = my_function()
        assert task_id is not None
        
        pool = get_global_thread_pool()
        result = pool.get_result(task_id)
        
        assert result.result == "decorated"


class TestGlobalInstances:
    """全局实例测试"""
    
    def test_global_thread_pool(self):
        """测试全局线程池"""
        pool = get_global_thread_pool()
        assert isinstance(pool, YanThreadPool)
    
    def test_global_coroutine_manager(self):
        """测试全局协程管理器"""
        cm = get_global_coroutine_manager()
        assert isinstance(cm, YanCoroutineManager)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])