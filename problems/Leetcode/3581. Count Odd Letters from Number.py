class Solution:
    def countOddLetters(self, n: int) -> int:
        a = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        mapping = {
            digit : Counter(a[digit]) for digit in range(10)
        }
        tot = Counter()
        for d in str(n):
            tot += mapping[int(d)]
        res = 0
        for key in tot:
            res += tot[key] % 2 == 1
        return res