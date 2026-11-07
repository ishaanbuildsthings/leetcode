# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/manacher-palindromes/template.py
# @operations: getAll isPalindrome longestPalCenteredAtI longestPalCenteredAtIPlusOne pointGet
# @data-structure-type: manacher
# @letters: same
# @complexities:
#   getAll: N
#   isPalindrome: 1
#   longestPalCenteredAtI: 1
#   longestPalCenteredAtIPlusOne: 1
#   pointGet: 1
#   build: N
# @memory:
#   layout: none
#   node: odd[1*N] even[1*N]
#   tags: none
#   other: A[1*N]
#   note: odd[i] = how far the palindrome centred on a[i] reaches (its radius, counting a[i]), even[i] = how many pairs the one centred between a[i-1] and a[i] has; Manacher's reuse of the mirrored centre inside the rightmost palindrome makes the build linear

# Manacher's algorithm over a static array: the radius of the longest palindrome around every centre (on a value, and
# between two values), built in O(N), so the longest palindrome around a centre and any palindrome check are O(1)
# with no hashing. Values are numbers or single characters. All indices 0-based, ranges inclusive.


class Manacher:
    # O(N) -- arr: the array (a list or a string, non-empty)
    def __init__(self, arr):
        self.A = A = list(arr)
        self.n = n = len(A)
        # odd[i]: the largest k with a[i-k+1..i+k-1] a palindrome (so at least 1)
        self.odd = odd = [0] * n
        l, r = 0, -1
        for i in range(n):
            k = 1 if i > r else min(odd[l + r - i], r - i + 1)
            while 0 <= i - k and i + k < n and A[i - k] == A[i + k]:
                k += 1
            odd[i] = k
            if i + k - 1 > r:
                l, r = i - k + 1, i + k - 1
        # even[i]: the largest k with a[i-k..i+k-1] a palindrome (the centre is between a[i-1] and a[i]; 0 when none)
        self.even = even = [0] * n
        l, r = 0, -1
        for i in range(n):
            k = 0 if i > r else min(even[l + r - i + 1], r - i + 1)
            while 0 <= i - k - 1 and i + k < n and A[i - k - 1] == A[i + k]:
                k += 1
            even[i] = k
            if i + k - 1 > r:
                l, r = i - k, i + k - 1

    # O(N) -- the whole array
    def getAll(self):
        return list(self.A)

    # O(1) -- a[i]; needs 0 <= i < n, else raises IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.A[i]

    # O(1) -- is a[l..r] a palindrome; needs 0 <= l <= r < n, else raises IndexError
    def isPalindrome(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"isPalindrome: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        m = r - l + 1
        if m & 1:
            return self.odd[(l + r) // 2] >= (m + 1) // 2
        return self.even[(l + r + 1) // 2] >= m // 2

    # O(1) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)); needs 0 <= i < n, else
    # raises IndexError
    def longestPalCenteredAtI(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"longestPalCenteredAtI: needs 0 <= i < n, got i = {i}, n = {self.n}")
        k = self.odd[i] - 1
        return i - k, i + k

    # O(1) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty range,
    # when there is none (so also for i = n - 1); needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtIPlusOne(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"longestPalCenteredAtIPlusOne: needs 0 <= i < n, got i = {i}, n = {self.n}")
        k = self.even[i + 1] if i + 1 < self.n else 0
        return i - k + 1, i + k
