# https://leetcode.com/problems/seat-reservation-manager/description/
# difficulty: medium
# tags: heaps

# problem
# Design a system that manages the reservation state of n seats that are numbered from 1 to n.

# Implement the SeatManager class:

# SeatManager(int n) Initializes a SeatManager object that will manage n seats numbered from 1 to n. All seats are initially available.
# int reserve() Fetches the smallest-numbered unreserved seat, reserves it, and returns its number.
# void unreserve(int seatNumber) Unreserves the seat with the given seatNumber.

# Solution, O(n) init, O(log n) reserve and unreserve, standard minheap

class SeatManager:

    def __init__(self, n: int):
        self.availableSeats = [i for i in range(1, n + 1)]

    def reserve(self) -> int:
        takenSeat = heapq.heappop(self.availableSeats)
        return takenSeat

    def unreserve(self, seatNumber: int) -> None:
        heapq.heappush(self.availableSeats, seatNumber)


# Your SeatManager object will be instantiated and called as such:
# obj = SeatManager(n)
# param_1 = obj.reserve()
# obj.unreserve(seatNumber)