# https://leetcode.com/problems/minimum-time-to-repair-cars/description/
# Difficulty: medium
# Tags: binary search

# Problem
# You are given an integer array ranks representing the ranks of some mechanics. ranksi is the rank of the ith mechanic. A mechanic with a rank r can repair n cars in r * n2 minutes.

# You are also given an integer cars representing the total number of cars waiting in the garage to be repaired.

# Return the minimum time taken to repair all the cars.

# Note: All the mechanics can repair the cars simultaneously.

# Solution, O(log(max rank * max cars squared)) time, O(1) space
# At most, we take 10**14 time to repair a car, if we have the max cars and one mechanic with rank 100. So we can binary search timing, and for each timing, see if we can repair enough cars. I also binary searched to find how many cars a single mechanic can repair in a certain time (increasing my TC) but you can just solve the math equation to figure this out, oops!

class Solution:
    def repairCars(self, ranks: List[int], cars: int) -> int:
        ranks.sort() # helps us more quickly assess if we can repair all cars when we do the linear scan

        # tells us how many repairs someone with `rank` can do within `time`
        @cache
        def maxRepairs(rank, time):
            l = 0
            r = 10**6 # max number of cars anyway
            while l <= r:
                m = (r + l) // 2 # m is what we test for # of repairs someone with `rank` can do
                # we could repair in time, try more
                if rank * m**2 <= time:
                    l = m + 1
                else:
                    r = m - 1
            return r


        # tells us if all the cars can be repaired in `time` time
        def canRepairAllCarsInTime(time):
            carsRepaired = 0
            for rank in ranks:
                maxRepairsPersonCanDo = maxRepairs(rank, time)
                carsRepaired += maxRepairsPersonCanDo
                if carsRepaired >= cars:
                    return True
            return False


        l = 0
        r = 10**14 # one person with rank 100 repairing the max cars
        while l < r:
            m = (r + l) // 2 # m is the amount of time we will test
            # try less time
            if canRepairAllCarsInTime(m):
                r = m
            else:
                l = m + 1
        return l