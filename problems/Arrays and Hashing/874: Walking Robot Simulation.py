# https://leetcode.com/problems/walking-robot-simulation/
# Difficulty: medium
# tags: simulation

# Problem
# A robot on an infinite XY-plane starts at point (0, 0) facing north. The robot can receive a sequence of these three possible types of commands:

# -2: Turn left 90 degrees.
# -1: Turn right 90 degrees.
# 1 <= k <= 9: Move forward k units, one unit at a time.
# Some of the grid squares are obstacles. The ith obstacle is at grid point obstacles[i] = (xi, yi). If the robot runs into an obstacle, then it will instead stay in its current location and move on to the next command.

# Return the maximum Euclidean distance that the robot ever gets from the origin squared (i.e. if the distance is 5, return 25).

# Note:

# North means +Y direction.
# East means +X direction.
# South means -Y direction.
# West means -X direction.
# There can be obstacle in [0,0].

# solution, O(commands time * length of command) + O(obstacles time), O(obstacles space), just simulate walking. I used key strings for ease but there are better.

# 0 = north, 1 = east, 2 = south, 3 = west

diffs = {
    0 : [-1, 0],
    1 : [0, 1],
    2 : [1, 0],
    3 : [0, -1],
}

class Solution:
    def robotSim(self, commands: List[int], obstacles: List[List[int]]) -> int:
        obsSet = set([f'{-1 * tup[1]},{tup[0]}' for tup in obstacles]) # defined my plane different
        pos = [0, 0]
        direction = 0
        res = 0

        for command in commands:
            if command == -1:
                direction += 1
                direction %= 4
            elif command == -2:
                direction -= 1
                if direction == -1:
                    direction = 3
            else:
                rowDiff = diffs[direction][0]
                colDiff = diffs[direction][1]
                for steps in range(command):
                    newPos = [pos[0] + rowDiff, pos[1] + colDiff]
                    newPosStr = f'{newPos[0]},{newPos[1]}'
                    print(newPosStr)
                    if newPosStr in obsSet:
                        break
                    pos = newPos
                    euclid = abs(pos[0])**2 + abs(pos[1])**2
                    res = max(res, euclid)

        return res



