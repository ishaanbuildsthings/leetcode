# can use bucket sorting also
class Solution:
    def hasGroupsSizeX(self, deck: List[int]) -> bool:
        c = Counter(deck)
        g = c[deck[0]]
        for k, v in c.items():
            g = gcd(g, v)
        return g > 1
            