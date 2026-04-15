class Solution:
    def splitPainting(self, segments: List[List[int]]) -> List[List[int]]:
        events = defaultdict(int)
        for l, r, v in segments:
            events[l] += v
            events[r] -= v
        events = sorted([(i, diff) for i, diff in events.items()])
        res = []
        curr = 0
        prev = None
        for i, diff in events:
            seg = [prev, i, curr]
            if prev is not None and curr != 0:
                res.append(seg)
            curr += diff
            prev = i
        
        return res