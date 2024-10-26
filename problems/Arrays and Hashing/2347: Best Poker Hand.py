# https://leetcode.com/problems/best-poker-hand/description/
# difficulty: easy

# Problem
# You are given an integer array ranks and a character array suits. You have 5 cards where the ith card has a rank of ranks[i] and a suit of suits[i].

# The following are the types of poker hands you can make from best to worst:

# "Flush": Five cards of the same suit.
# "Three of a Kind": Three cards of the same rank.
# "Pair": Two cards of the same rank.
# "High Card": Any single card.
# Return a string representing the best type of poker hand you can make with the given cards.

# Note that the return values are case-sensitive.

# Solution, O(1) time and space
HAND_SIZE = 5
class Solution:
    def bestHand(self, ranks: List[int], suits: List[str]) -> str:
        if all(suits[i] == suits[0] for i in range(HAND_SIZE)):
            return 'Flush'
        counts = Counter(ranks)
        best = max(counts.values())
        return (
            'Three of a Kind' if best >= 3 else
            'Pair' if best == 2 else
            'High Card'
        )

