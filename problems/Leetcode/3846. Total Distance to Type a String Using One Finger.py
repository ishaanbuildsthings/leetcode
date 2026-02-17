class Solution:
    def totalDistance(self, s: str) -> int:
        board = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
        mp = {}
        for r in range(3):
            w = board[r]
            for c in range(len(w)):
                mp[board[r][c]] = (r, c)
        res = 0

        def dist(l1, l2):
            r1, c1 = mp[l1]
            r2, c2 = mp[l2]
            return abs(r1-r2) + abs(c1-c2)
        
        for i, v in enumerate(s):
            prev = s[i-1] if i else 'a'
            res += dist(v, prev)
        
        return res