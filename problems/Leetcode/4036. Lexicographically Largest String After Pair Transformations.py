class Solution:
    def largestString(self, nums: list[int]) -> list[str]:
        cost = {}
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        for i, letter in enumerate(ABC):
            cost[letter] = 2**i
        
        def process(num):
            res = []
            for pos in range(40):
                if (num >> pos) & 1:
                    letter = ABC[pos] if pos < 26 else ('z' * (pos - 24))
                    res.append(letter)
            return ''.join(res)[::-1]

        return [process(x) for x in nums]