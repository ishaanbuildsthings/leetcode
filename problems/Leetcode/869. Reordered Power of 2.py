class Solution:
    def reorderedPowerOf2(self, n: int) -> bool:
        s = str(n)
        options = [] # generate all powers of 2 of length len(s)
        curr = 1
        while True:
            currS = str(curr)
            if len(currS) == len(s):
                options.append(currS)
            elif len(currS) > len(s):
                break
            curr *= 2

        return any(Counter(opt) == Counter(s) for opt in options)