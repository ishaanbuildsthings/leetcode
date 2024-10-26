# https://leetcode.com/problems/categorize-box-according-to-criteria/description/
# difficulty: easy
# tags: math

# Solution, O(1) time and space

class Solution:
    def categorizeBox(self, length: int, width: int, height: int, mass: int) -> str:
        maxDimension = max(length, width, height)
        volume = length * width * height

        isBulky = maxDimension >= 10**4 or volume >= 10**9
        isHeavy = mass >= 100

        return ("Both" if isBulky and isHeavy
                else "Heavy" if isHeavy
                else "Bulky" if isBulky
                else "Neither")