class Solution:
    def mostFrequentIDs(self, nums: List[int], freq: List[int]) -> List[int]:
        sl = SortedList() # freq, idx
        idToFrq = defaultdict(int)
        res = []
        for num, frq in zip(nums, freq):
            oldFrq = idToFrq[num]
            sl.discard((oldFrq, num))
            nfrq = oldFrq + frq
            sl.add((nfrq, num))
            idToFrq[num] = nfrq
            res.append(sl[-1][0])
        return res