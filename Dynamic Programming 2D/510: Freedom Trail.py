# https://leetcode.com/problems/freedom-trail/description/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# In the video game Fallout 4, the quest "Road to Freedom" requires players to reach a metal dial called the "Freedom Trail Ring" and use the dial to spell a specific keyword to open the door.

# Given a string ring that represents the code engraved on the outer ring and another string key that represents the keyword that needs to be spelled, return the minimum number of steps to spell all the characters in the keyword.

# Initially, the first character of the ring is aligned at the "12:00" direction. You should spell all the characters in key one by one by rotating ring clockwise or anticlockwise to make each character of the string key aligned at the "12:00" direction and then by pressing the center button.

# At the stage of rotating the ring to spell the key character key[i]:

# You can rotate the ring clockwise or anticlockwise by one place, which counts as one step. The final purpose of the rotation is to align one of ring's characters at the "12:00" direction, where this character must equal key[i].
# If the character key[i] has been aligned at the "12:00" direction, press the center button to spell, which also counts as one step. After the pressing, you could begin to spell the next character in the key (next stage). Otherwise, you have finished all the spelling.

# Solution, standard dp. We have word*ring states and up to run options for each.

class Solution:
    def findRotateSteps(self, ring: str, key: str) -> int:
        @cache
        def dp(i, pos):
            # base case
            if i == len(key):
                return 0

            resForThis = float('inf')

            for nextPos in range(len(ring)):
                if ring[nextPos] != key[i]:
                    continue
                small = min(nextPos, pos)
                big = max(nextPos, pos)
                dist1 = big - small
                dist2 = small + len(ring) - big
                dist = min(dist1, dist2)
                resForThis = min(resForThis, dist + dp(i + 1, nextPos))

            return resForThis

        return dp(0, 0) + len(key)

        # TODO: dp state doesnt use for loop :o