class Solution:
    def numRabbits(self, answers: List[int]) -> int:
        c = Counter(answers)
        res = 0
        for groupSize in c:
            numGroups = c[groupSize]
            res += (groupSize + 1) * math.ceil(numGroups / (groupSize + 1))
        return res