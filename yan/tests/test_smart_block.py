"""
测试智能块推断机制
"""
import pytest
import sys
import os

# 添加父目录到路径以便导入 yan 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import BlockStack


class TestBlockStack:
    """测试 BlockStack 类"""

    def test_block_stack_push_pop(self):
        """测试 push/pop 操作"""
        stack = BlockStack()

        # 空栈
        assert stack.is_empty() is True
        assert stack.depth() == 0

        # 压入一个块
        stack.push('if', 4)
        assert stack.is_empty() is False
        assert stack.depth() == 1

        # 获取当前块
        current = stack.current()
        assert current is not None
        assert current['type'] == 'if'
        assert current['indent'] == 4

        # 压入另一个块
        stack.push('while', 8)
        assert stack.depth() == 2

        current = stack.current()
        assert current['type'] == 'while'
        assert current['indent'] == 8

        # 弹出块
        popped = stack.pop()
        assert popped['type'] == 'while'
        assert popped['indent'] == 8
        assert stack.depth() == 1

        current = stack.current()
        assert current['type'] == 'if'

        # 弹出最后一个块
        popped = stack.pop()
        assert popped['type'] == 'if'
        assert stack.is_empty() is True
        assert stack.depth() == 0

    def test_block_stack_empty(self):
        """测试空栈行为"""
        stack = BlockStack()

        # 空栈检查
        assert stack.is_empty() is True
        assert stack.depth() == 0

        # 空栈调用 current() 应返回 None
        assert stack.current() is None

        # 空栈调用 pop() 应返回 None
        assert stack.pop() is None

    def test_block_stack_depth(self):
        """测试栈深度"""
        stack = BlockStack()

        assert stack.depth() == 0

        stack.push('if', 4)
        assert stack.depth() == 1

        stack.push('while', 8)
        assert stack.depth() == 2

        stack.push('for', 12)
        assert stack.depth() == 3

        stack.pop()
        assert stack.depth() == 2

        stack.pop()
        assert stack.depth() == 1

        stack.pop()
        assert stack.depth() == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
