# https://leetcode.com/problems/maximum-matching-of-players-with-trainers/description/
# difficulty: medium
# tags: two pointers

# Problem
# You are given a 0-indexed integer array players, where players[i] represents the ability of the ith player. You are also given a 0-indexed integer array trainers, where trainers[j] represents the training capacity of the jth trainer.

# The ith player can match with the jth trainer if the player's ability is less than or equal to the trainer's training capacity. Additionally, the ith player can be matched with at most one trainer, and the jth trainer can be matched with at most one player.

# Return the maximum number of matchings between players and trainers that satisfy these conditions.

# Solution, sort both then use two pointers. Another way which I believe is a common two pointers thing is: Since trainers capacity is always going up, we just need to pick a player under the current trainer capacity. To make it simple, we can choose the smallest one.

class Solution:
    def matchPlayersAndTrainers(self, players: List[int], trainers: List[int]) -> int:
        players.sort()
        trainers.sort()

        i = len(players) - 1
        j = len(trainers) - 1

        res = 0

        while j >= 0 and i >= 0:
            if players[i] > trainers[j]:
                i -= 1
            else:
                i -= 1
                j -= 1
                res += 1

        return res
