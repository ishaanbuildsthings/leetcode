class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        numToFrq, frqToNums, res = Counter(nums), defaultdict(list), []
        for num in numToFrq:
            frqToNums[numToFrq[num]].append(num)
        for frequency in range(len(nums), 0, -1):
            res.extend(frqToNums[frequency])
            if len(res) == k:
                return res