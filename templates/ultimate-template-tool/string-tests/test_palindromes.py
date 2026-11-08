# Stress test for longestPalAroundEachCenter (../strings) against brute force: python3 test_palindromes.py
import os, random
HERE = os.path.dirname(os.path.abspath(__file__))
env = {}
exec(open(os.path.join(HERE, "..", "strings", "longestPalAroundEachCenter.py")).read(), env)
f = env["longestPalAroundEachCenter"]
isPal = lambda s, a, b: list(s[a:b + 1]) == list(s[a:b + 1])[::-1]
for _ in range(20000):
    n = random.randint(0, 14)
    sigma = random.choice([1, 2, 3, 26])
    s = [random.randrange(sigma) - 1 for _ in range(n)]
    s = random.choice([s, tuple(s), "".join(chr(98 + x) for x in s)])
    atI, atIPlusOne = f(s)
    for i in range(n):
        k = 0
        while i - k >= 0 and i + k < n and isPal(s, i - k, i + k):
            k += 1
        assert atI[i] == (i - k + 1, i + k - 1), (s, i)
        k = 0
        while i - k >= 0 and i + 1 + k < n and isPal(s, i - k, i + 1 + k):
            k += 1
        assert atIPlusOne[i] == ((i - k + 1, i + k) if k else (i + 1, i)), (s, i)
print("longestPalAroundEachCenter ok: 20000 random cases")
