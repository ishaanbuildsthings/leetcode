# https://leetcode.com/problems/corporate-flight-bookings/description/
# Difficulty: medium
# tags: sweep line

# Problem
# There are n flights that are labeled from 1 to n.

# You are given an array of flight bookings bookings, where bookings[i] = [firsti, lasti, seatsi] represents a booking for flights firsti through lasti (inclusive) with seatsi seats reserved for each flight in the range.

# Return an array answer of length n, where answer[i] is the total number of seats reserved for flight i.

# Solution, O(n) time and O(1) space since we use the sweep line for the result

class Solution:
    def corpFlightBookings(self, bookings: List[List[int]], n: int) -> List[int]:
        sweep = [0 for _ in range(n)]
        sweep.append(0)
        for l, r, seats in bookings:
            l -= 1
            r -= 1
            sweep[l] += seats
            sweep[r + 1] -= seats
        sweep.pop()
        running = 0
        for i in range(len(sweep)):
            running += sweep[i]
            sweep[i] = running
        return sweep
