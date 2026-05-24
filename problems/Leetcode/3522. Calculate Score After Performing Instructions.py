class Solution:
    def calculateScore(self, instructions: List[str], values: List[int]) -> int:
        seen = set()
        res = 0
        i = 0
        while True:
            if i < 0 or i >= len(instructions):
                # print(f'breaking, i={i}')
                break
            if i in seen:
                # print(f'seen, breaking, i={i}')
                break
            if instructions[i] == 'add':
                res += values[i]
                # print(f'res now: {res}')
                
                # print(f'jump)
                seen.add(i)
                i += 1
                continue
            else:
                # print(f'jumping to: {i+values[i]}')
                nextI = i + values[i]
                seen.add(i)
                i = nextI
        
        
        return res