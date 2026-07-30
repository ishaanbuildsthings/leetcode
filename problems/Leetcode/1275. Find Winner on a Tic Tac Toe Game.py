class Solution:
    def tictactoe(self, moves: List[List[int]]) -> str:
        rows = defaultdict(lambda: {'x':0,'o':0})
        cols = defaultdict(lambda: {'x':0,'o':0})
        downright = {'x':0,'o':0}
        upright = {'x':0,'o':0}
        for i, (r, c) in enumerate(moves):
            char = 'x' if not i % 2 else 'o'
            rows[r][char] += 1
            cols[c][char] += 1
            if rows[r][char] == 3 or cols[c][char] == 3:
                return 'A' if char == 'x' else 'B'
            if r == c:
                downright[char] += 1
            if downright[char] == 3:
                return 'A' if char == 'x' else 'B'
            if r == 3 - c - 1:
                upright[char] += 1
            if upright[char] == 3:
                return 'A' if char == 'x' else 'B'
            
        

        return 'Draw' if len(moves) == 9 else 'Pending'
