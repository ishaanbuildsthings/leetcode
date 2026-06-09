# https://leetcode.com/problems/time-needed-to-buy-tickets/description/?envType=daily-question&envId=2024-04-09

# Solution, O(n) time O(1) space
class Solution:
    def timeRequiredToBuy(self, tickets: List[int], k: int) -> int:
        return sum(
            min(tickets[k], tickets[i]) if i <= k
            else min(tickets[i], tickets[k] - 1)
            for i in range(len(tickets))
        )