class Solution:
    def isPossible(self, nums: List[int]) -> bool:
        wantNext = defaultdict(lambda : SortedList()) # maps an ending number to a sorted list of lengths of that ending number
        for v in nums:
            sl = wantNext[v]
            if not sl:
                wantNext[v + 1].add(1)
            else:
                small = sl[0]
                sl.pop(0)
                wantNext[v + 1].add(small + 1)
        for key in wantNext:
            for val in wantNext[key]:
                if val < 3:
                    return False
        return True
