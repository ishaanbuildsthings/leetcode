# https://leetcode.com/problems/convert-the-temperature/
# Difficulty: Easy
# Tags: math

# Problem
# You are given a non-negative floating point number rounded to two decimal places celsius, that denotes the temperature in Celsius.

# You should convert Celsius into Kelvin and Fahrenheit and return it as an array ans = [kelvin, fahrenheit].

# Return the array ans. Answers within 10-5 of the actual answer will be accepted.

# Note that:

# Kelvin = Celsius + 273.15
# Fahrenheit = Celsius * 1.80 + 32.00

# Solution, O(1) time and space

class Solution:
    def convertTemperature(self, celsius: float) -> List[float]:
        k = celsius + 273.15
        f = celsius * 1.8 + 32
        return [k, f]