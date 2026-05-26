print('=== 成语接龙游戏 ===')
print('')
print('规则：输入四字成语，AI会接着你的最后一个字继续')
print("输入 '退出' 结束游戏")
print('')
成语文件 = __import__('pathlib').Path('examples/idioms.txt')
成语内容 = 成语文件.read_text(encoding='utf-8')
成语行列表 = 成语内容.splitlines()
成语库 = _list()
for 行 in 成语行列表:
    清理 = 行.strip()
    if _not(_eq(清理, '')):
        if _not(_eq(清理.startswith('--'), True)):
            _append(成语库, 清理)
    已用 = _list()
    尾 = ''
    玩 = True
    print('请输入第一个成语：')
    while 玩:
        你 = input()
        if _eq(你, 'quit'):
            print('游戏结束！')
            玩 = False
            continue
        if _eq(你, 'exit'):
            print('游戏结束！')
            玩 = False
            continue
        if _eq(你, 'help'):
            print('')
            print('=== 帮助 ===')
            print('  输入四字成语接龙')
            print("  输入 'quit' 或 'exit' 退出")
            print("  输入 'help' 显示帮助")
            print("  输入 '库' 查看所有可用成语")
            print('')
            continue
        if _eq(你, '库'):
            print('')
            print('=== 可用成语库 ===')
            for c in 成语库:
                print(_concat('  ', c))
            print('')
            continue
        if _eq(你, '帮'):
            if _empty(尾):
                print('还没有开始接龙，请先输入一个成语！')
                continue
            可选 = _list()
            for y in 成语库:
                if _not(_contains(已用, y)):
                    z = _strslice(y, 0, 1)
                    if _eq(z, 尾):
                        _append(可选, y)
            if _empty(可选):
                print('没有可用的提示了！')
            if _not(_empty(可选)):
                print('')
                print('=== 提示 ===')
                print(_concat('可以接 "', 尾), '" 开头的成语有：')
                for h in 可选:
                    print(_concat('  ', h))
                print('')
            continue
        if _eq(你, '退出'):
            print('游戏结束！')
            玩 = False
            continue
        if _ne(_strlen(你), 4):
            print('请输入四字成语！')
            continue
        if _not(_contains(成语库, 你)):
            print(_concat('"', 你), '" 不在库中！')
            continue
        if _contains(已用, 你):
            print(_concat('"', 你), '" 已用过！')
            continue
        if _not(_empty(尾)):
            x = _strslice(你, 0, 1)
            if _not(_eq(x, 尾)):
                print(_concat('需要以 "', 尾), '" 开头！')
                continue
        _append(已用, 你)
        尾 = _strslice(你, 3, 4)
        print(_concat(_concat('你：', 你), '（'), 尾, '）')
        print('AI思考中...')
        __import__('time').sleep(0.5)
        选 = _list()
        for y in 库:
            if _not(_contains(已用, y)):
                z = _strslice(y, 0, 1)
                if _eq(z, 尾):
                    _append(选, y)
        if _empty(选):
            print('AI接不上了！你赢了！')
            玩 = False
            continue
        选长 = _len(选)
        i = __import__('random').randint(0, 选长 - 1)
        r = _nth(选, i)
        _append(已用, r)
        尾 = _strslice(r, 3, 4)
        print(_concat(_concat('AI：', r), '（'), 尾, '）')
    print('')
    print('=== 游戏结束 ===')
    print(_concat('共使用了 ', _concat(_len(已用), ' 个成语')))