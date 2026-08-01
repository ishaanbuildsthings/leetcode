class Solution:
    def maximumWidth(self, planks: list[int]) -> int:
        res = 0
        c = Counter(planks)
        for k, v in c.items():
            remaining = [x for x in planks if x != k]
            remaining.sort()
            l = 0
            r = len(remaining) - 1
            pairs = 0
            while l < r:
                if remaining[l] + remaining[r] == k:
                    pairs += 1
                    l += 1
                    r -= 1
                elif remaining[l] + remaining[r] > k:
                    r -= 1
                else:
                    l += 1
            res = max(res, v + pairs)
        
        pairs = Counter()
        uniq = list(set(planks))
        for i in range(len(uniq)):
            for j in range(i, len(uniq)):
                pairSum = uniq[i] + uniq[j]
                numPairs = min(c[uniq[i]], c[uniq[j]]) if i != j else c[uniq[i]] // 2
                pairs[pairSum] += numPairs

        
        res = max(res, max(pairs.values(), default=0))

        return res