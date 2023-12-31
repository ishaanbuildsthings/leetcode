# https://leetcode.com/problems/find-consecutive-integers-from-a-data-stream/description/
# difficulty: medium

# Problem
# For a stream of integers, implement a data structure that checks if the last k integers parsed in the stream are equal to value.

# Implement the DataStream class:

# DataStream(int value, int k) Initializes the object with an empty integer stream and the two integers value and k.
# boolean consec(int num) Adds num to the stream of integers. Returns true if the last k integers are equal to value, and false otherwise. If there are less than k integers, the condition does not hold true, so returns false.

# Solution, O(1) init and consec, standard logic

class DataStream:

    def __init__(self, value: int, k: int):
        self.streak = 0
        self.last = None
        self.k = k
        self.value = value

    def consec(self, num: int) -> bool:
        if num == self.last:
            self.streak += 1
        else:
            self.streak = 1
        self.last = num
        return self.streak >= self.k and self.value == num


# Your DataStream object will be instantiated and called as such:
# obj = DataStream(value, k)
# param_1 = obj.consec(num)