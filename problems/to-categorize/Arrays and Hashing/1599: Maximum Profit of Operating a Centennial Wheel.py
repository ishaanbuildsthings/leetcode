# https://leetcode.com/problems/maximum-profit-of-operating-a-centennial-wheel/description/
# Difficulty: Medium

# Problem
# You are the operator of a Centennial Wheel that has four gondolas, and each gondola has room for up to four people. You have the ability to rotate the gondolas counterclockwise, which costs you runningCost dollars.

# You are given an array customers of length n where customers[i] is the number of new customers arriving just before the ith rotation (0-indexed). This means you must rotate the wheel i times before the customers[i] customers arrive. You cannot make customers wait if there is room in the gondola. Each customer pays boardingCost dollars when they board on the gondola closest to the ground and will exit once that gondola reaches the ground again.

# You can stop the wheel at any time, including before serving all customers. If you decide to stop serving customers, all subsequent rotations are free in order to get all the customers down safely. Note that if there are currently more than four customers waiting at the wheel, only four will board the gondola, and the rest will wait for the next rotation.

# Return the minimum number of rotations you need to perform to maximize your profit. If there is no scenario where the profit is positive, return -1.

# Solution, O(max(sum(customers) / 4), len(customers)) time, O(1) space
# I just simulated it. Though now I realize I didn't need to actually track the 4 gondolas, it becomes immaterial once they are in the air. We iterate over at most sum(customers) / 4 gondola trips, or len(customers). We track our running profit and max profit.

class Solution:
    def minOperationsMaxProfit(self, customers: List[int], boardingCost: int, runningCost: int) -> int:
        gondola = [0, 0, 0, 0] # always top, right, down, left

        maxProfit = 0
        minRotationRes = 0
        currentProfit = 0
        currentRotations = 0
        totalWaiting = 0
        started = False

        def rotateLeft():
            nonlocal currentRotations
            currentRotations += 1
            first = gondola.pop(0)
            gondola.append(first)


        pointer = 0 # which customers can board
        while pointer < len(customers) or (totalWaiting > 0 and started):
            started = True
            if pointer < len(customers):
                totalWaiting += customers[pointer]
            capacity = 4 - gondola[2]
            amountThatCanBoard = min(capacity, totalWaiting)
            totalWaiting -= amountThatCanBoard
            gondola[2] += amountThatCanBoard
            currentProfit += (amountThatCanBoard * boardingCost)

            rotateLeft()
            pointer += 1
            currentProfit -= runningCost

            if currentProfit > maxProfit:
                minRotationRes = currentRotations
                maxProfit = currentProfit
            gondola[2] = 0
        return minRotationRes if minRotationRes != 0 else -1