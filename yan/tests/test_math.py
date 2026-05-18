#!/usr/bin/env python3
"""
言语言标准库测试 - Math 模块
"""

from yan_test import *
from yan_assertions import *


@suite("Math 模块测试")
class MathTests:

    def setup(self):
        """测试前准备"""
        pass

    def teardown(self):
        """测试后清理"""
        pass

    @test("圆周率常量测试")
    def test_pi(self):
        """测试圆周率常量"""
        from stdlib.math import π, 圆周率
        # 断言 π 值正确
        等(π, 3.141592653589793)

    @test("自然常数测试")
    def test_e(self):
        """测试自然常数"""
        from stdlib.math import e, 自然常数
        # 断言 e 值正确
        等(e, 2.718281828459045)

    @test("绝对值测试")
    def test_abs(self):
        """测试绝对值函数"""
        from stdlib.math import 绝对
        等(绝对(-5), 5)
        等(绝对(5), 5)
        等(绝对(0), 0)
        等(绝对(-3.14), 3.14)

    @test("向下取整测试")
    def test_floor(self):
        """测试向下取整"""
        from stdlib.math import 下取整
        等(下取整(3.9), 3)
        等(下取整(-3.9), -4)
        等(下取整(5), 5)

    @test("向上取整测试")
    def test_ceil(self):
        """测试向上取整"""
        from stdlib.math import 上取整
        等(上取整(3.1), 4)
        等(上取整(-3.1), -3)
        等(上取整(5), 5)

    @test("四舍五入测试")
    def test_round(self):
        """测试四舍五入"""
        from stdlib.math import 四舍五入
        等(四舍五入(3.5), 4)
        等(四舍五入(3.4), 3)
        等(四舍五入(-3.5), -4)

    @test("开平方测试")
    def test_sqrt(self):
        """测试开平方根"""
        from stdlib.math import 开方
        等(开方(4), 2.0)
        等(开方(9), 3.0)
        等(开方(16), 4.0)
        等(开方(0), 0.0)

    @test("幂运算测试")
    def test_power(self):
        """测试幂运算"""
        from stdlib.math import 幂
        等(幂(2, 3), 8)
        等(幂(2, 0), 1)
        等(幂(2, -1), 0.5)

    @test("阶乘测试")
    def test_factorial(self):
        """测试阶乘函数"""
        from stdlib.math import 阶乘
        等(阶乘(0), 1)
        等(阶乘(1), 1)
        等(阶乘(5), 120)
        等(阶乘(10), 3628800)

    @test("素数判断测试")
    def test_is_prime(self):
        """测试素数判断"""
        from stdlib.math import 是素数
        为假(是素数(0))
        为假(是素数(1))
        为真(是素数(2))
        为真(是素数(3))
        为假(是素数(4))
        为真(是素数(5))
        为假(是素数(9))
        为真(是素数(17))
        为真(是素数(23))

    @test("斐波那契数列测试")
    def test_fibonacci(self):
        """测试斐波那契数列"""
        from stdlib.math import 斐波那契
        等(斐波那契(0), 0)
        等(斐波那契(1), 1)
        等(斐波那契(10), 55)
        等(斐波那契(15), 610)

    @test("最大公约数测试")
    def test_gcd(self):
        """测试最大公约数"""
        from stdlib.math import 最大公约数
        等(最大公约数(12, 8), 4)
        等(最大公约数(18, 24), 6)
        等(最大公约数(7, 13), 1)

    @test("最小公倍数测试")
    def test_lcm(self):
        """测试最小公倍数"""
        from stdlib.math import 最小公倍数
        等(最小公倍数(4, 6), 12)
        等(最小公倍数(5, 10), 10)
        等(最小公倍数(7, 13), 91)

    @test("求和测试")
    def test_sum(self):
        """测试求和函数"""
        from stdlib.math import 求和
        等(求和(列(1, 2, 3, 4, 5)), 15)
        等(求和(列()), 0)
        等(求和(列(10)), 10)

    @test("平均值测试")
    def test_average(self):
        """测试平均值函数"""
        from stdlib.math import 平均值
        等(平均值(列(1, 2, 3, 4, 5)), 3.0)
        等(平均值(列(2, 4)), 3.0)

    @test("最大值测试")
    def test_max(self):
        """测试最大值函数"""
        from stdlib.math import 最大值
        等(最大值(1, 2, 3), 3)
        等(最大值(5, 5, 3), 5)
        等(最大值(-1, -5, -3), -1)

    @test("最小值测试")
    def test_min(self):
        """测试最小值函数"""
        from stdlib.math import 最小值
        等(最小值(1, 2, 3), 1)
        等(最小值(5, 5, 3), 3)
        等(最小值(-1, -5, -3), -5)


if __name__ == "__main__":
    report = run()
    print_summary(report)
