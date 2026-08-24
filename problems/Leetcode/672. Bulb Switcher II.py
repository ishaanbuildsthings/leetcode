class Solution:
    def flipLights(self, n: int, presses: int) -> int:
        if presses == 0:
            return 1
        if presses == 1:
            return 2 if n == 1 else 3 if n == 2 else 4
        if presses in [2, 3] and n == 1:
            return 2
        if presses == n == 2:
            return 4
        if presses == 2:
            return 7
        if n == 1:
            return 2
        if n == 2:
            return 4
        return 8