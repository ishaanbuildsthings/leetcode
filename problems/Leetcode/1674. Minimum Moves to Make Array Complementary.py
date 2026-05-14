class Solution:
    def minMoves(self, nums: List[int], limit: int) -> int:
        

        # pair costs 2, 4, 6, ... 2 * limit

        # for each of those, we see how many exactly match

        # we see how many can attain in 1 operation

        # the rest attain in 2 operations

        ranges = []
        c = Counter()
        for i in range(len(nums) // 2):
            s = nums[i]
            e = nums[~i]
            c[s + e] += 1
            lo = min(s + 1, e + 1)
            hi = max(s + limit, e + limit)
            ranges.append((lo, hi))
        
        sweep = [0] * (2 * limit + 2)
        for a, b in ranges:
            sweep[a] += 1
            sweep[b + 1] -= 1
        
        res = inf
        curr = 0
        for i in range(len(sweep)):
            curr += sweep[i]
            score = curr - c[i]
            otherRanges = len(nums) // 2 - curr
            score += 2 * otherRanges
            res = min(res, score)
        
        return res

        

        