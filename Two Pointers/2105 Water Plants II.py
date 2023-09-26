# https://leetcode.com/problems/watering-plants-ii/
# difficulty: medium
# tags: two pointers

# problem
# Alice and Bob want to water n plants in their garden. The plants are arranged in a row and are labeled from 0 to n - 1 from left to right where the ith plant is located at x = i.

# Each plant needs a specific amount of water. Alice and Bob have a watering can each, initially full. They water the plants in the following way:

# Alice waters the plants in order from left to right, starting from the 0th plant. Bob waters the plants in order from right to left, starting from the (n - 1)th plant. They begin watering the plants simultaneously.
# It takes the same amount of time to water each plant regardless of how much water it needs.
# Alice/Bob must water the plant if they have enough in their can to fully water it. Otherwise, they first refill their can (instantaneously) then water the plant.
# In case both Alice and Bob reach the same plant, the one with more water currently in his/her watering can should water this plant. If they have the same amount of water, then Alice should water this plant.
# Given a 0-indexed integer array plants of n integers, where plants[i] is the amount of water the ith plant needs, and two integers capacityA and capacityB representing the capacities of Alice's and Bob's watering cans respectively, return the number of times they have to refill to water all the plants.

# Solution, O(n) time O(1) space
# Just iterate and count, simulation. Code can be more concise.

class Solution:
    def minimumRefill(self, plants: List[int], capacityA: int, capacityB: int) -> int:
        l = 0
        r = len(plants) - 1

        aliceWater = capacityA
        bobWater = capacityB
        refills = 0

        while l <= r:
            if l == r:
                if aliceWater >= bobWater:
                    if aliceWater >= plants[l]:
                        aliceWater -= plants[l]
                    else:
                        aliceWater = capacityA
                        aliceWater -= plants[l]
                        refills += 1
                else:
                    if bobWater >= plants[r]:
                        bobWater -= plants[r]
                    else:
                        bobWater = capacityB
                        bobWater -= plants[r]
                        refills += 1
                return refills

            if aliceWater >= plants[l]:
                aliceWater -= plants[l]
            else:
                aliceWater = capacityA
                aliceWater -= plants[l]
                refills += 1

            if bobWater >= plants[r]:
                bobWater -= plants[r]
            else:
                bobWater = capacityB
                bobWater -= plants[r]
                refills += 1

            l += 1
            r -= 1

        return refills
