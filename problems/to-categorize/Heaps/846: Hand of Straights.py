# https://leetcode.com/problems/hand-of-straights/
# difficulty: medium
# tags: lazy heap

# Problem
# Alice has some number of cards and she wants to rearrange the cards into groups so that each group is of size groupSize, and consists of groupSize consecutive cards.

# Given an integer array hand where hand[i] is the value written on the ith card and an integer groupSize, return true if she can rearrange the cards, or false otherwise.

# Solution, heapify everything, take out the smallest, iterate through and remove, repeat, O(n log n) time and O(n) space

class Solution:
    def isNStraightHand(self, hand: List[int], groupSize: int) -> bool:
        if len(hand) % groupSize != 0:
            return False

        heap = [*hand]
        heapq.heapify(heap)
        counts = collections.Counter(hand)
        lazy = defaultdict(int)

        while heap:
            while heap and heap[0] in lazy and lazy[heap[0]] > 0:
                lazy[heap[0]] -= 1
                heapq.heappop(heap)
            if not heap:
                break

            smallest = heapq.heappop(heap)
            counts[smallest] -= 1
            for num in range(smallest + 1, smallest + groupSize):
                counts[num] -= 1
                lazy[num] += 1
                if counts[num] < 0:
                    return False

        return True



