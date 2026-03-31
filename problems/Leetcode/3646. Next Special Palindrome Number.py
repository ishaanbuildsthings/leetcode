class Solution:
    def specialPalindrome(self, n: int) -> int:
        length = len(str(n))
        res = inf
        for mask in range(0, 1 << 11, 2): # skip masks with a 0 set
            digits = []
            for d in range(1, 10):
                if mask & (1 << d):
                    digits.append(d)
            lengthHere = sum(x for x in digits)
            if lengthHere < length:
                continue
            if lengthHere > length + 1:
                continue
            odds = sum(d % 2 for d in digits)
            if odds > 1:
                continue
            half = []
            for d in digits:
                half.extend([d] * (d//2))
            oddDigits = [x for x in digits if x % 2]
            for perm in set(itertools.permutations(half)): # set here not required but a huge speedup, prevents downstream work from being duplicated
                full = perm + tuple(oddDigits) + perm[::-1]
                num = int(''.join(str(x) for x in full))
                if num > n and num < res:
                    res = num
        return res


            
            