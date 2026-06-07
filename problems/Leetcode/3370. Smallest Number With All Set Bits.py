class Solution:
    def smallestNumber(self, n: int) -> int:
        for number in range(n, 10**6 + 1):
            # print(f'number: {number}')
            print(bin(number)[2:])
            if all(c == '1' for c in bin(number)[2:]):
                # print(f'yes')
                return number
        