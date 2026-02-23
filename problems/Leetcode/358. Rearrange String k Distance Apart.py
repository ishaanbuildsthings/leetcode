class Solution:
    def rearrangeString(self, s: str, kk: int) -> str:
        c = Counter(s)
        n = len(s)
        resArr = [None] * n
        latest = defaultdict(lambda: -inf)
        for i in range(n):
            elements = sorted([(v, k) for k, v in c.items() if v != 0], reverse=True)
            for v, k in elements:
                dist = i - latest[k]
                if dist < kk:
                    continue
                resArr[i] = k
                c[k] -= 1
                latest[k] = i
                break
        
        if any(x is None for x in resArr):
            return ''
        return ''.join(resArr)