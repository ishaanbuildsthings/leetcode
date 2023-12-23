# https://leetcode.com/problems/count-houses-in-a-circular-street/description/
# difficulty: easy

# problem
# You are given an object street of class Street that represents a circular street and a positive integer k which represents a maximum bound for the number of houses in that street (in other words, the number of houses is less than or equal to k). Houses' doors could be open or closed initially.

# Initially, you are standing in front of a door to a house on this street. Your task is to count the number of houses in the street.

# The class Street contains the following functions which may help you:

# void openDoor(): Open the door of the house you are in front of.
# void closeDoor(): Close the door of the house you are in front of.
# boolean isDoorOpen(): Returns true if the door of the current house is open and false otherwise.
# void moveRight(): Move to the right house.
# void moveLeft(): Move to the left house.
# Return ans which represents the number of houses on this street.

# Solution, O(k) time and O(1) space
# Close every door, then open every door and count

# Definition for a street.
# class Street:
#     def openDoor(self):
#         pass
#     def closeDoor(self):
#         pass
#     def isDoorOpen(self):
#         pass
#     def moveRight(self):
#         pass
#     def moveLeft(self):
#         pass
class Solution:
    def houseCount(self, street: Optional['Street'], k: int) -> int:
        # close every door
        for i in range(k):
            street.closeDoor()
            street.moveRight()

        res = 0
        # open doors
        for i in range(k):
            if not street.isDoorOpen():
                street.openDoor()
                res += 1
            street.moveRight()
        return res