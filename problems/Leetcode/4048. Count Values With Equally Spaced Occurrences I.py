class Solution:
    def countSpecialIntegers(self, nums: list[int]) -> int:
        c = Counter(nums)
        res = 0
        vToI = defaultdict(list)
        for i, v in enumerate(nums):
            vToI[v].append(i)
        for k, frq in c.items():
            if frq != 3:
                continue
            bucket = vToI[k]
            g1 = bucket[1]-bucket[0]
            g2 = bucket[-1]-bucket[1]
            if g1 == g2:
                res += 1
        return res