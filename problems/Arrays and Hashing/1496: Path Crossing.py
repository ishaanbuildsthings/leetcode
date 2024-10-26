# https://leetcode.com/problems/path-crossing/description/?envType=daily-question&envId=2023-12-23
# difficulty: Easy

# Problem
# Given a string path, where path[i] = 'N', 'S', 'E' or 'W', each representing moving one unit north, south, east, or west, respectively. You start at the origin (0, 0) on a 2D plane and walk on the path specified by path.

# Return true if the path crosses itself at any point, that is, if at any time you are on a location you have previously visited. Return false otherwise.

# Solution
# O(path) time and space, move and check

OFFSETS = {
    'N' : [-1, 0],
    'S' : [1, 0],
    'W' : [0, -1],
    'E' : [0, 1],
}

class Solution:
    def isPathCrossing(self, path: str) -> bool:
        seen = { (0, 0) }
        currX = 0
        currY = 0
        for char in path:
            offset = OFFSETS[char]
            currX += offset[1]
            currY += offset[0]
            if (currX, currY) in seen:
                return True
            seen.add((currX, currY))
        return False
