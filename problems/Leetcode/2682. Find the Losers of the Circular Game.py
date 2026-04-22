class Solution:
    def circularGameLosers(self, n: int, k: int) -> List[int]:
        c = Counter()
        c[0] += 1
        i = 0
        for op in range(1, 2 * n + 20):
            dist = op * k
            newI = (i + dist) % n
            print(f'{newI=}')
            c[newI] += 1
            if c[newI] == 2:
                break
            i = newI
        res = []
        for person in range(n):
            if c[person] == 0:
                res.append(person + 1)
        return res