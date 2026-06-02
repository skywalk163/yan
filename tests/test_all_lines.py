import sys
sys.path.insert(0, 'yan')
from yan.main import run

lines = [
    '印10加5。',
    '印10减5。',
    '印10乘5。',
    '印10除5。',
    '10加5，乘2，印。',
    '印列1 2 3。',
    '印范围5。',
    '列1 2 3，皆乘2，印。',
    '列1 2 3 4 5，只大2，印。',
    '列1 2 3，归加0，印。',
    '印x。',
    '印面积。',
    '印nums。',
    '印阶乘5。',
    '印平方5。',
    '印距离3 7。',
    '印若5大3则"大"否则"小"。',
    '印若$(10 > 5)则真否则假。',
]

for line in lines:
    try:
        result = run(line, use_global_verbs=True, syntax_version=1)
        print(f'{line} -> {result}')
    except Exception as e:
        print(f'{line} -> Error: {e}')
