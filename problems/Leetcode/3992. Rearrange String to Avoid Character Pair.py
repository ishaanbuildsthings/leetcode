class Solution:
    def rearrangeString(self, s: str, x: str, y: str) -> str:
        c = Counter(s)
        res = []
        for cnt in range(c[y]):
            res.append(y)
        for cnt in range(c[x]):
            res.append(x)

        print(f'init res: {res}')

        for v in c:
            print(f'loop on v={v}')
            print(f'count is: {c[v]}')
            if v == x or v == y:
                continue
            for cnt in range(c[v]):
                print(f'count is: {cnt}')
                res.append(v)

        return ''.join(res)