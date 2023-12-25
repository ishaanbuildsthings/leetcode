# https://leetcode.com/problems/robot-bounded-in-circle/description/
# difficulty: medium

# Problem
# On an infinite plane, a robot initially stands at (0, 0) and faces north. Note that:

# The north direction is the positive direction of the y-axis.
# The south direction is the negative direction of the y-axis.
# The east direction is the positive direction of the x-axis.
# The west direction is the negative direction of the x-axis.
# The robot can receive one of three instructions:

# "G": go straight 1 unit.
# "L": turn 90 degrees to the left (i.e., anti-clockwise direction).
# "R": turn 90 degrees to the right (i.e., clockwise direction).
# The robot performs the instructions given in order, and repeats them forever.

# Return true if and only if there exists a circle in the plane such that the robot never leaves the circle.

# Solution, O(n) time O(1) space, check 4 cycles
DIFFS = {
    'n': [-1, 0],
    's': [1, 0],
    'e': [0, 1],
    'w': [0, -1],
}

def turnLeft(dir):
    leftTurns = {
        'n': 'w',
        'w': 's',
        's': 'e',
        'e': 'n'
    }
    return leftTurns[dir]

def turnRight(dir):
    rightTurns = {
        'n': 'e',
        'e': 's',
        's': 'w',
        'w': 'n'
    }
    return rightTurns[dir]


class Solution:
    def isRobotBounded(self, instructions: str) -> bool:
        x, y = 0, 0
        direction = 'n'

        for _ in range(4):
            for char in instructions:
                if char == 'G':
                    diff = DIFFS[direction]
                    x += diff[0]
                    y += diff[1]
                elif char == 'L':
                    direction = turnLeft(direction)
                elif char == 'R':
                    direction = turnRight(direction)

        return x == 0 and y == 0
