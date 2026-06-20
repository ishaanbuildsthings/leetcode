class Solution:
    def removeInvalidParentheses(self, s: str) -> List[str]:
        minRemoved = inf
        res = []
        def bt(bucket, leftSurplus, removed, i):
            nonlocal minRemoved
            nonlocal res
            if removed > minRemoved:
                return
            if i == len(s):
                if leftSurplus == 0:
                    if removed < minRemoved:
                        minRemoved = removed
                        res = [''.join(bucket)]
                    elif removed == minRemoved:
                        res.append(''.join(bucket))
                return
            v = s[i]

            if v.isalpha() or v == '(' or (v == ')' and leftSurplus):
                bucket.append(v)
                nsurplus = (leftSurplus + (1 if v == '(' else -1 if v == ')' else 0))
                ifKeep = bt(bucket, nsurplus, removed, i + 1)
                bucket.pop()
            if not v.isalpha():
                ifDelete = bt(bucket, leftSurplus, removed + 1, i + 1)
        bt([], 0, 0, 0)

        return list(set(res))
