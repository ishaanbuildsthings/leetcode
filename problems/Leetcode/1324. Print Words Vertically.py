class Solution:
    def printVertically(self, s: str) -> List[str]:
        words = s.split(' ')
        mx = max(len(x) for x in words)
        res = []
        for i in range(mx):
            bucket = []
            for wi in range(len(words)):
                w = words[wi]
                if i < len(w):
                    bucket.append(w[i])
                else:
                    bucket.append(' ')
            while bucket and bucket[-1] == ' ':
                bucket.pop()
            res.append(''.join(bucket))
        return res

