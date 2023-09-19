# https://leetcode.com/problems/minimum-number-of-days-to-eat-n-oranges/
# Difficulty: Hard
# Tags: bfs, dynamic programming 1d

# Problem
# There are n oranges in the kitchen and you decided to eat some of these oranges every day as follows:

# Eat one orange.
# If the number of remaining oranges n is divisible by 2 then you can eat n / 2 oranges.
# If the number of remaining oranges n is divisible by 3 then you can eat 2 * (n / 3) oranges.
# You can only choose one of the actions per day.

# Given the integer n, return the minimum number of days to eat n oranges.

# Solution, O(log n) time and O(log n) space, since worst case we end up making log size reductions before arriving at our solution
# I just bfs'd it. There was a dp solution but it was too smart for me :) Though now I see my bfs assumptions could be used to derive that solution of never eating 3 single oranges in a row (otherwise bfs may not run in time)

import queue as queueDataStructure

class Solution:
    def minDays(self, n: int) -> int:
        queue = queueDataStructure.Queue()
        queue.put(n)
        result = 0
        seen = set()

        while True:
            length = queue.qsize()
            for i in range(length):
                orangeCount = queue.get()

                if orangeCount in seen:
                    continue
                seen.add(orangeCount)

                if orangeCount == 0:
                    return result

                queue.put(orangeCount - 1)
                if orangeCount % 2 == 0:
                    queue.put(orangeCount / 2)
                if orangeCount % 3 == 0:
                    queue.put(orangeCount / 3)
            result += 1