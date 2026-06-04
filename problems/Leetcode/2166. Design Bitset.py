WORD = 64
class Bitset:

    def __init__(self, size: int):
        self.n = math.ceil(size / WORD) # how many words we have
        self.words = [0] * self.n
        self.sz = size
        self.flipped = False
        self.ones = 0 # how many bits are set in the thing regardless of flip status or not
        
    def fix(self, idx: int) -> None:
        wordI = idx // 64
        bit = idx % 64
        word = self.words[wordI]
        if not self.flipped:
            if not word & (1 << bit):
                self.ones += 1
            word |= (1 << bit)
            self.words[wordI] = word
            return
        if word & (1 << bit):
            self.ones -= 1
            word ^= (1 << bit)
        self.words[wordI] = word

    def unfix(self, idx: int) -> None:
        wordI = idx // 64
        bit = idx % 64
        word = self.words[wordI]
        if not self.flipped:
            if word & (1 << bit):
                word ^= (1 << bit)
                self.ones -= 1
            self.words[wordI] = word
            return
        if not word & (1 << bit):
            word ^= (1 << bit)
            self.ones += 1
        self.words[wordI] = word

    def flip(self) -> None:
        self.flipped = not self.flipped

    def all(self) -> bool:
        if not self.flipped:
            return self.ones == self.sz
        zeroes = self.sz - self.ones
        return zeroes == self.sz
        

    def one(self) -> bool:
        if not self.flipped:
            return self.ones > 0
        zeroes = self.sz - self.ones
        return zeroes > 0

    def count(self) -> int:
        if not self.flipped:
            return self.ones
        zeroes = self.sz - self.ones
        return zeroes

    def toString(self) -> str:
        out = []
        for idx in range(self.sz):
            phys = (self.words[idx // 64] >> (idx % 64)) & 1
            out.append('1' if phys ^ self.flipped else '0')
        return ''.join(out)
        


# Your Bitset object will be instantiated and called as such:
# obj = Bitset(size)
# obj.fix(idx)
# obj.unfix(idx)
# obj.flip()
# param_4 = obj.all()
# param_5 = obj.one()
# param_6 = obj.count()
# param_7 = obj.toString()