class Solution:
    def nthUglyNumber(self, n: int, a: int, b: int, c: int) -> int:
        l = n // 3 * min(a, b, c)
        r = n * min(a, b, c)

        def numbersLTEValThatAreDivisible(val):
            aDivis = val // a
            bDivis = val // b
            cDivis = val // c
            abDivis = val // (lcm(a, b))
            acDivis = val // (lcm(a, c))
            bcDivis = val // (lcm(b, c))
            abcDivis = val // (lcm(a, b, c))
            return aDivis + bDivis + cDivis - abDivis - acDivis - bcDivis + abcDivis
        
        res = None
        while l <= r:
            m = (r + l) // 2
            numbers = numbersLTEValThatAreDivisible(m)
            if numbers < n:
                l = m + 1
            elif numbers == n:
                res = m
                r = m - 1
            else:
                r = m - 1
        return res