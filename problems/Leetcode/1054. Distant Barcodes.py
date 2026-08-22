from sortedcontainers import SortedList
class Solution:
    def rearrangeBarcodes(self, barcodes: List[int]) -> List[int]:
        sl = SortedList()
        c = Counter(barcodes)
        for key, frq in c.items():
            sl.add((frq, key))
        res = [None] * len(barcodes)
        i = 0
        while sl:
            frq, key = sl.pop(-1)
            res[i] = key
            i += 1
            if sl:
                frq2, key2 = sl.pop(-1)
                res[i] = key2
                i += 1
                if frq2 - 1:
                    sl.add((frq2-1,key2))
            if frq - 1:
                sl.add((frq-1,key))
        return res

        # _ _ _ _ _ _ _ _
        # 1 _ 1 _ 1 _ 1 _
        # 1 2 1 2 1 _ 1 _




        # 1 2 1 2 1 2 1 2
        