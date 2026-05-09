#!/usr/bin/env python3
# 测试 ID 拆分逻辑

verbs = ['印', '加', '减', '乘', '除', '模', '幂', '绝对', '负',
         '大', '小', '等', '不等', '且', '或', '非',
         '首', '余', '入', '长', '连', '含',
         '皆', '只', '归']

test_ids = ['盘子数等', '印张三', '汉诺塔盘子数减1']

for id_text in test_ids:
    print(f"\n测试: {id_text}")
    # 检查是否包含动词
    for verb in verbs:
        if verb in id_text:
            # 找到动词的位置
            pos = id_text.find(verb)
            if pos > 0:  # 动词不在开头
                left = id_text[:pos]
                right = id_text[pos + len(verb):]
                print(f"  拆分: {left} + {verb} + {right}")
            break
    else:
        print(f"  未找到动词")
