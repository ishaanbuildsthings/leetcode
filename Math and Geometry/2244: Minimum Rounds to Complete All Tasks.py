# https://leetcode.com/problems/minimum-rounds-to-complete-all-tasks/description/
# Difficulty: Medium
# Tags: Math

# Problem
# You are given a 0-indexed integer array tasks, where tasks[i] represents the difficulty level of a task. In each round, you can complete either 2 or 3 tasks of the same difficulty level.

# Return the minimum rounds required to complete all the tasks, or -1 if it is not possible to complete all the tasks.

# Solution, O(n) time and O(n) space
# Count each task, then use math to solve it. We take at most 2 2s.

class Solution:
    def minimumRounds(self, tasks: List[int]) -> int:
        counts = Counter(tasks)
        result = 0
        for key in counts:
            if counts[key] == 1:
                return -1
            if counts[key] % 3 == 0:
                result += counts[key] / 3
            if counts[key] % 3 == 1:
                result += 2 + (counts[key] - 4) / 3
            if counts[key] % 3 == 2:
                result += 1 + (counts[key] - 2) / 3

        return int(result)