    def visitIdAtom(self, ctx: YanParser.IdAtomContext):
        name = ctx.ID().getText()

        # 检查是否以动词开头（前缀动词）
        verbs = ['印', '加', '减', '乘', '除', '模', '幂', '绝对', '负',
                 '大', '小', '等', '不等', '且', '或', '非',
                 '首', '余', '入', '长', '连', '含',
                 '皆', '只', '归']

        for verb in verbs:
            if name.startswith(verb) and len(name) > len(verb):
                verb_node = Word(verb)
                arg_node = Word(name[len(verb):])
                return Call(verb_node, [arg_node])

        # 检查是否包含中缀动词
        for verb in verbs:
            if verb in name and not name.startswith(verb):
                # 找到动词的位置
                pos = name.find(verb)
                left = name[:pos]
                right = name[pos + len(verb):]
                
                # 创建中缀调用
                verb_node = Word(verb)
                left_node = Word(left)
                
                if right:
                    # 有右操作数
                    right_node = Word(right)
                    return Call(verb_node, [left_node, right_node])
                else:
                    # 没有右操作数（柯里化）
                    return Call(verb_node, [left_node])

        return Word(name)
