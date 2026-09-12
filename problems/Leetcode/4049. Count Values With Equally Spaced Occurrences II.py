class Solution:
    def countSpecialIntegers(self, nums: list[int]) -> int:
        c = Counter(nums)
        res = 0
        vToI = defaultdict(list)
        for i, v in enumerate(nums):
            vToI[v].append(i)
        for k, frq in c.items():
            if frq < 3:
                continue
            bucket = vToI[k]
            gaps = set()
            for i in range(len(bucket) - 1):
                gap = bucket[i+1]-bucket[i]
                gaps.add(gap)
            if len(gaps) > 1:
                continue
            res += 1
        return res