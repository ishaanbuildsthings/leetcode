class Solution:
    def gcdOfOddEvenSums(self, n: int) -> int:
        odds = []
        evens = []
        for number in range(1, 5*n):
            if number % 2:
                odds.append(number)
            else:
                evens.append(number)

        return gcd(sum(odds[:n]), sum(evens[:n]))