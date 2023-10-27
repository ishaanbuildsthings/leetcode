# https://leetcode.com/problems/destroying-asteroids/description/
# difficulty: medium
# tags: greedy

# Problem
# You are given an integer mass, which represents the original mass of a planet. You are further given an integer array asteroids, where asteroids[i] is the mass of the ith asteroid.

# You can arrange for the planet to collide with the asteroids in any arbitrary order. If the mass of the planet is greater than or equal to the mass of the asteroid, the asteroid is destroyed and the planet gains the mass of the asteroid. Otherwise, the planet is destroyed.

# Return true if all asteroids can be destroyed. Otherwise, return false.

# Solution, O(n log n) time, O(sort) space
# Just sort then apply greedy

class Solution:
    def asteroidsDestroyed(self, mass: int, asteroids: List[int]) -> bool:
        asteroids.sort()
        currentSize = mass
        for asteroid in asteroids:
            if mass >= asteroid:
                mass += asteroid
            else:
                return False
        return True