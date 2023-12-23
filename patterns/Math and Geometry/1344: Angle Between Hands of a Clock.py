# https://leetcode.com/problems/angle-between-hands-of-a-clock/
# difficulty: medium
# tags: math

# Problem
# Given two numbers, hour and minutes, return the smaller angle (in degrees) formed between the hour and the minute hand.

# Answers within 10-5 of the actual value will be accepted as correct.

# Solution, O(1) time and space, I'm sure there is something better

class Solution:
    def angleClock(self, hour: int, minutes: int) -> float:
        minuteOffset = 360 * (minutes / 60)
        hourOffset = ((360 * (hour / 12)) + (30 * (minuteOffset / 360))) % 360
        diff = abs(hourOffset - minuteOffset)
        return min(diff, 360 - diff)