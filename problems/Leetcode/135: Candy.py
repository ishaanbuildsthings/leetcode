class Solution:
    def candy(self, ratings: List[int]) -> int:
        n = len(ratings)
        ratingToIdxs = defaultdict(list)
        for i, v in enumerate(ratings):
            ratingToIdxs[v].append(i)
        allRatings = sorted(set(ratings))
        res = [1] * n
        for rating in allRatings:
            for idx in ratingToIdxs[rating]:
                leftCandy = res[idx-1] if (idx > 0 and ratings[idx-1] < ratings[idx]) else 0
                rightCandy = res[idx+1] if (idx < n - 1 and ratings[idx+1] < ratings[idx]) else 0
                req = 1 + max(leftCandy, rightCandy)
                res[idx] = max(res[idx], req)
        return sum(res)