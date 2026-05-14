# https://leetcode.com/problems/largest-values-from-labels/description/
# difficulty: medium

# Solution, O(n log n) time and O(n) space

class Solution:
    def largestValsFromLabels(self, values: List[int], labels: List[int], numWanted: int, useLimit: int) -> int:
        zipped = [
            (values[i], labels[i]) for i in range(len(values))
        ]
        zipped.sort(key = lambda x: -x[0])
        usedLabels = defaultdict(int)

        score = 0
        used = 0

        for val, label in zipped:
            if used == numWanted:
                break

            if usedLabels[label] < useLimit:
                usedLabels[label] += 1
                score += val
                used += 1

        return score
