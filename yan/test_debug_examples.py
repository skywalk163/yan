"""测试运行 playground 中的例子，捕获运行时错误"""
import sys
import io
sys.path.insert(0, 'g:\\dumategithub\\newlisp\\yan')

from main import run
import traceback

def test_example(name, code):
    """运行单个例子，捕获输出和错误"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"{'='*60}")
    
    # 捕获 stdout
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    
    try:
        result = run(code, debug=False)
        output = captured.getvalue()
        if output:
            print(f"输出:\n{output[:500]}")
        if result is not None:
            print(f"结果: {result}")
        print("✅ 执行成功")
    except Exception as e:
        sys.stdout = old_stdout
        print(f"❌ 运行时错误: {e}")
        traceback.print_exc()
        return False
    finally:
        sys.stdout = old_stdout
    
    return True


# 从 index.html 中提取的例子代码
examples = {}

# 斐波那契数列（缩进语法）
examples['fibonacci_indent'] = """-- 斐波那契数列（缩进语法）
定 斐波那契 = 函 n
  若 小 n 2
    返回 1
  返回 加 斐波那契 减 n 1 斐波那契 减 n 2

-- 打印前10个斐波那契数
遍历 i 于 范围 1 11
  定 结果 = 斐波那契 i
  印 连 "斐波那契(" i ") = " 结果。"""

# 成语接龙
examples['idiom'] = """-- 成语接龙示例
-- 展示言语言的字符串处理和逻辑判断能力
印 "=== 成语接龙游戏 ==="。
印 "规则：输入四字成语，下一个成语的第一个字要接上一个成语的最后一个字"。
印 ""。

-- 成语库
定 成语库 = 列
  "一心一意" "意气风发" "发愤图强" "强词夺理"
  "理直气壮" "壮志凌云" "云开见日" "日新月异"
  "异曲同工" "工欲善其事" "事半功倍" "倍道而行"
  "行云流水" "水落石出" "出生入死" "死里逃生"
  "生龙活虎" "虎虎生威" "威风凛凛" "凛若冰霜"
  "霜露之病" "病入膏肓" "肓肉生肌" "肌无完肤"
  "肤受之诉" "诉诸武力" "力不从心" "心花怒放"
  "放虎归山" "山穷水尽" "尽善尽美" "美不胜收"
。

-- 获取成语的最后一个字
定 取尾字 = 函 成语：
  定 长度值 = 长度 成语。
  定 尾字 = 取 成语 (减 长度值 1)。
  返回 尾字。
。

-- 获取成语的首字
定 取首字 = 函 成语：
  返回 取 成语 0。
。

-- 查找可以接龙的成语
定 找接龙 = 函 当前成语：
  定 尾字 = 取尾字 当前成语。
  定 可选列表 = 列。
  遍历 y 于 成语库：
    定 首字 = 取首字 y。
    若 等 首字 尾字：
      添 可选列表 y。
    。
  。
  返回 可选列表。
。

-- 游戏演示
印 "开始游戏！".
印 ""。
印 "第一个成语：一心一意"。
印 ""。

定 可选 = 找接龙 "一心一意"。
印 "可以接龙的成语有："。
印 可选。
印 ""。

定 下一个 = 取 可选 0。
印 连 "选择：" 下一个。"""

# 二分查找（缩进语法）
examples['binary_search'] = """-- 二分查找（缩进语法）
定义 二分查找 = 函 arr 目标
  定义 左 = 0
  定义 右 = 减 长度 arr 1
  当时 小于等于 左 右
    定义 中 = 除 (加 左 右) 2
    定义 中值 = 取 arr 中
    如果 等 中值 目标
      返回 中
    如果 小于 中值 目标
      定义 左 = 加 中 1
    否则
      定义 右 = 减 中 1
  返回 负一

-- 测试
定义 有序数组 = 列 1 3 5 7 9 11 13 15 17 19 21 25 30 35 40
印 "有序数组:"
印 有序数组
印 "查找 11:"
印 二分查找 有序数组 11
印 "查找 16:"
印 二分查找 有序数组 16
印 "查找 1:"
印 二分查找 有序数组 1
印 "查找 40:"
印 二分查找 有序数组 40"""

if __name__ == '__main__':
    for name, code in examples.items():
        test_example(name, code)
        print()