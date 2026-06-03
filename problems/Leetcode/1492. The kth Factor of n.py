class Solution:
    def kthFactor(self, n: int, k: int) -> int:

        # can do in O(1) space, count # of factors in a loop first, then we can iterate again and track

        small = []
        big = []
        for num in range(1, 1 + math.floor(math.sqrt(n))):
            if n % num == 0:
                small.append(num)
                if num * num != n:
                    big.append(n // num)

        big = big[::-1]

        if k > len(small) + len(big):
            return -1

        if k <= len(small):
            return small[k - 1]
        
        return big[k - len(small) - 1]