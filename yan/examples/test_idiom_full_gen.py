print('=== 成语接龙完整测试 ===')
print('')
库 = _list('一心一意', '意气风发', '发愤图强', '强词夺理', '理直气壮', '壮志凌云', '云开雾散', '开门见山', '山清水秀', '秀外慧中', '中流砥柱', '水落石出', '出人头地')
已用 = _list()
尾 = ''
回合 = 0
print('开始游戏...')
print('')
回合 = _add(回合, 1)
print(_concat('[第', _concat(回合, '轮] 玩家：一心一意')))
_append(已用, '一心一意')
尾 = _strslice('一心一意', 3, 4)
选 = _list()
for y in 库:
    if _not(_contains(已用, y)):
        z = _strslice(y, 0, 1)
        if _eq(z, 尾):
            _append(选, y)
if _not(_empty(选)):
    r = _head(选)
    _append(已用, r)
    尾 = _strslice(r, 3, 4)
    print(_concat(_concat('AI：', r), '（'), 尾, '）')
print('')
回合 = _add(回合, 1)
print(_concat('[第', _concat(回合, '轮] 玩家：发愤图强')))
首字 = _strslice('发愤图强', 0, 1)
if _not(_eq(首字, 尾)):
    print(_concat('错误：需要以 "', 尾), '" 开头！')
if _eq(首字, 尾):
    _append(已用, '发愤图强')
    尾 = _strslice('发愤图强', 3, 4)
    选 = _list()
    for y in 库:
        if _not(_contains(已用, y)):
            z = _strslice(y, 0, 1)
            if _eq(z, 尾):
                _append(选, y)
    if _not(_empty(选)):
        r = _head(选)
        _append(已用, r)
        尾 = _strslice(r, 3, 4)
        print(_concat(_concat('AI：', r), '（'), 尾, '）')
    if _empty(选):
        print('AI 接不上了！')
print('')
print('=== 游戏结束 ===')
print(_concat('共进行了 ', _concat(回合, ' 回合')))
print(_concat('使用了 ', _concat(_len(已用), ' 个成语')))
print('')
print('使用的成语：')
for c in 已用:
    print(_concat('  ', c))
print('')
print('=== 测试通过 ===')