class Solution:
    def highFive(self, items: List[List[int]]) -> List[List[int]]:
        idxToTopFive = defaultdict(list)
        for idx, score in items:
            bucket = idxToTopFive[idx]
            heapq.heappush(bucket, score)
            if len(bucket) == 6:
                heapq.heappop(bucket)
        res = []
        for idx in idxToTopFive:
            tot = sum(idxToTopFive[idx])
            avg = tot // 5
            res.append([idx, avg])
        return sorted(res, key=lambda tup: tup[0])