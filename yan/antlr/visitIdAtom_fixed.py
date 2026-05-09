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

        # 不要在 ID 中拆分中缀动词
        # 让中缀表达式规则处理这种情况

        return Word(name)
