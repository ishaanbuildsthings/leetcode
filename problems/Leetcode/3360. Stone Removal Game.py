class Solution:
    def canAliceWin(self, n: int) -> bool:
        turn = 'A'
        subtract = 10
        remain = n
        while True:
            if subtract > remain:
                return False if turn == 'A' else True
            remain -= subtract
            turn = 'B' if turn == 'A' else 'A'
            subtract -= 1
        
        