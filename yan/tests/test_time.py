#!/usr/bin/env python3
"""
言语言标准库测试 - Time 模块
"""

from yan_test import *
from yan_assertions import *


@suite("Time 模块测试")
class TimeTests:

    @test("获取当前时间戳测试")
    def test_current_timestamp(self):
        """测试获取当前时间戳"""
        from stdlib.time import 当前时间戳
        ts = 当前时间戳()
        # 时间戳应该大于0
        大于(ts, 0)
        # 时间戳应该在合理范围内（2020年至今）
        大于(ts, 1577836800)

    @test("获取当前日期测试")
    def test_current_date(self):
        """测试获取当前日期"""
        from stdlib.time import 当前日期
        date = 当前日期()
        # 日期应该是字符串格式
        类型(date, str)
        # 应该包含年份
        包含(date, "202")

    @test("获取当前时间字符串测试")
    def test_current_time_string(self):
        """测试获取当前时间字符串"""
        from stdlib.time import 当前时间字符串
        time_str = 当前时间字符串()
        # 时间字符串应该包含日期和时间
        类型(time_str, str)

    @test("获取年测试")
    def test_get_year(self):
        """测试获取年"""
        from stdlib.time import 取年
        year = 取年("2024-01-15")
        等(year, 2024)

    @test("获取月测试")
    def test_get_month(self):
        """测试获取月"""
        from stdlib.time import 取月
        month = 取月("2024-01-15")
        等(month, 1)

    @test("获取日测试")
    def test_get_day(self):
        """测试获取日"""
        from stdlib.time import 取日
        day = 取日("2024-01-15")
        等(day, 15)

    @test("获取星期几测试")
    def test_weekday(self):
        """测试获取星期几"""
        from stdlib.time import 星期几
        # 2024-01-01 是星期一
        wd = 星期几("2024-01-01")
        等(wd, 0)

    @test("闰年判断测试")
    def test_leap_year(self):
        """测试闰年判断"""
        from stdlib.time import 是闰年
        为真(是闰年(2024))
        为假(是闰年(2023))
        为真(是闰年(2000))
        为假(是闰年(1900))

    @test("获取月天数测试")
    def test_month_days(self):
        """测试获取月天数"""
        from stdlib.time import 月天数
        等(月天数(2024, 1), 31)
        等(月天数(2024, 2), 29)  # 2024是闰年
        等(月天数(2023, 2), 28)
        等(月天数(2024, 4), 30)

    @test("睡眠测试")
    def test_sleep(self):
        """测试睡眠函数"""
        from stdlib.time import 睡眠
        import time
        start = time.time()
        睡眠(0.1)
        elapsed = time.time() - start
        # 睡眠0.1秒，应该至少经过0.09秒
        大于等于(elapsed, 0.09)

    @test("中文月份名称测试")
    def test_chinese_month_name(self):
        """测试中文月份名称"""
        from stdlib.time import 中文月名
        等(中文月名(1), "一月")
        等(中文月名(12), "十二月")

    @test("中文星期名称测试")
    def test_chinese_weekday_name(self):
        """测试中文星期名称"""
        from stdlib.time import 中文星期名
        等(中文星期名(0), "星期一")
        等(中文星期名(6), "星期日")

    @test("角度转弧度测试")
    def test_degrees_to_radians(self):
        """测试角度转弧度"""
        from stdlib.time import 角度弧度
        import math
        等(角度弧度(180), math.pi)
        等(角度弧度(90), math.pi / 2)
        等(角度弧度(0), 0)

    @test("弧度转角度测试")
    def test_radians_to_degrees(self):
        """测试弧度转角度"""
        from stdlib.time import 弧度角度
        import math
        等(弧度角度(math.pi), 180)
        等(弧度角度(math.pi / 2), 90)
        等(弧度角度(0), 0)


if __name__ == "__main__":
    report = run()
    print_summary(report)
