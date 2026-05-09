    # ============ 动词原子 ============
    
    def visitPrintAtom(self, ctx: YanParser.PrintAtomContext):
        return Word('印')
    
    def visitAddAtom(self, ctx: YanParser.AddAtomContext):
        return Word('加')
    
    def visitSubAtom(self, ctx: YanParser.SubAtomContext):
        return Word('减')
    
    def visitMulAtom(self, ctx: YanParser.MulAtomContext):
        return Word('乘')
    
    def visitDivAtom(self, ctx: YanParser.DivAtomContext):
        return Word('除')
    
    def visitModAtom(self, ctx: YanParser.ModAtomContext):
        return Word('模')
    
    def visitPowAtom(self, ctx: YanParser.PowAtomContext):
        return Word('幂')
    
    def visitAbsAtom(self, ctx: YanParser.AbsAtomContext):
        return Word('绝对')
    
    def visitNegAtom(self, ctx: YanParser.NegAtomContext):
        return Word('负')
    
    def visitGtAtom(self, ctx: YanParser.GtAtomContext):
        return Word('大')
    
    def visitLtAtom(self, ctx: YanParser.LtAtomContext):
        return Word('小')
    
    def visitEqAtom(self, ctx: YanParser.EqAtomContext):
        return Word('等')
    
    def visitNeAtom(self, ctx: YanParser.NeAtomContext):
        return Word('不等')
    
    def visitAndAtom(self, ctx: YanParser.AndAtomContext):
        return Word('且')
    
    def visitOrAtom(self, ctx: YanParser.OrAtomContext):
        return Word('或')
    
    def visitNotAtom(self, ctx: YanParser.NotAtomContext):
        return Word('非')
    
    def visitHeadAtom(self, ctx: YanParser.HeadAtomContext):
        return Word('首')
    
    def visitTailAtom(self, ctx: YanParser.TailAtomContext):
        return Word('余')
    
    def visitAppendAtom(self, ctx: YanParser.AppendAtomContext):
        return Word('入')
    
    def visitLenAtom(self, ctx: YanParser.LenAtomContext):
        return Word('长')
    
    def visitConcatAtom(self, ctx: YanParser.ConcatAtomContext):
        return Word('连')
    
    def visitContainsAtom(self, ctx: YanParser.ContainsAtomContext):
        return Word('含')
    
    def visitMapAtom(self, ctx: YanParser.MapAtomContext):
        return Word('皆')
    
    def visitFilterAtom(self, ctx: YanParser.FilterAtomContext):
        return Word('只')
    
    def visitReduceAtom(self, ctx: YanParser.ReduceAtomContext):
        return Word('归')
