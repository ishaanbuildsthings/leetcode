# https://leetcode.com/problems/count-houses-in-a-circular-street-ii/description/
# difficulty: hard

# Problem
# You are given an object street of class Street that represents a circular street and a positive integer k which represents a maximum bound for the number of houses in that street (in other words, the number of houses is less than or equal to k). Houses' doors could be open or closed initially (at least one is open).

# Initially, you are standing in front of a door to a house on this street. Your task is to count the number of houses in the street.

# The class Street contains the following functions which may help you:

# void closeDoor(): Close the door of the house you are in front of.
# boolean isDoorOpen(): Returns true if the door of the current house is open and false otherwise.
# void moveRight(): Move to the right house.
# Note that by circular street, we mean if you number the houses from 1 to n, then the right house of housei is housei+1 for i < n, and the right house of housen is house1.

# Return ans which represents the number of houses on this street.

# Solution, O(k) time, O(1) space. Go to the first open house, then keep turning and closing as needed, up to k turns, update result as needed. Fun puzzle. Asked during my 26th birthday.

# Definition for a street.
# class Street:
#     def closeDoor(self):
#         pass
#     def isDoorOpen(self):
#         pass
#     def moveRight(self):
#         pass
class Solution:
    def houseCount(self, street: Optional['Street'], k: int) -> int:
        while not street.isDoorOpen():
            street.moveRight()
        
        res = 0
        steps = 0
        for _ in range(k):
            street.moveRight()
            steps += 1
            if street.isDoorOpen():
                street.closeDoor()
                res = steps
        
        return res

                

