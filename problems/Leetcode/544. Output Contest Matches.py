class Solution:
    def findContestMatch(self, n: int) -> str:
        arr = [f'({i+1},{n-i})' for i in range(n // 2)]
        while len(arr) > 1:
            nt = []
            for i in range(0, len(arr) // 2):
                first = arr[i]
                second = arr[-1 - i]
                pair = f'({first},{second})'
                nt.append(pair)
            arr = nt
        
        return arr[0]