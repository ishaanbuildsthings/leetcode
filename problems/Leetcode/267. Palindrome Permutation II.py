class Solution:
    def generatePalindromes(self, s: str) -> List[str]:
        c = Counter(s)
        if sum(c[key] % 2 == 1 for key in c) > 1:
            return []
        odd = None
        for k, v in c.items():
            if v % 2:
                odd = k
            c[k] //= 2
        
        allLetters = sum(c[k] for k in c)

        res = []
        def bt(remain, i, bucket):
            if len(bucket) == allLetters:
                res.append(''.join(bucket))
                return
            for k, v in remain.items():
                if not v:
                    continue
                bucket.append(k)
                remain[k] -= 1
                bt(remain, i + 1, bucket)
                bucket.pop()
                remain[k] += 1
        bt(c, 0, [])

        res2 = []
        for half in res:
            if odd is not None:
                res2.append(half + odd + half[::-1])
            else:
                res2.append(half + half[::-1])
        
        return res2
                
        
        
        
        