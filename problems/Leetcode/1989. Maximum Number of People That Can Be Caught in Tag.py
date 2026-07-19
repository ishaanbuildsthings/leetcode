class Solution:
    def catchMaximumAmountofPeople(self, team: List[int], dist: int) -> int:
        taggedFromRight = set()
        n = len(team)
        closestOnRight = inf
        for i in range(n - 1, -1, -1):
            if team[i]:
                closestOnRight = i
            if not team[i]:
                distance = closestOnRight - i
                if distance <= dist:
                    taggedFromRight.add(i)
        
        taggedFromLeft = set()
        closestOnLeft = -inf
        for i in range(n):
            if team[i]:
                closestOnLeft = i
            if not team[i]:
                distance = i - closestOnLeft
                if distance <= dist:
                    taggedFromLeft.add(i)
        
        return min(team.count(1), len(taggedFromLeft | taggedFromRight))