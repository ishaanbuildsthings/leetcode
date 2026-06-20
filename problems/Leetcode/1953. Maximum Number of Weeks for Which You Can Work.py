class Solution:
    def numberOfWeeks(self, milestones: List[int]) -> int:
        # can be avoided
        milestones.sort()
        mx = milestones[-1]
        tot = sum(milestones[:-1])
        if mx <= tot + 1:
            return sum(milestones)
        return tot + tot + 1