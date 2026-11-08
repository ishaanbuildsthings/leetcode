# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/shortestPeriod.py

# length of the shortest prefix that repeats a whole number of times to form the sequence (n if none, 0 if empty)
# shortestPeriod("abcabcabc") -> 3
# shortestPeriod("abcab") -> 5
# O(n) time and space
def shortestPeriod(arrOrString):
    n = len(arrOrString)
    if n == 0:
        return 0
    pi = [0] * n
    for i in range(1, n):
        k = pi[i - 1]
        while k > 0 and arrOrString[i] != arrOrString[k]:
            k = pi[k - 1]
        if arrOrString[i] == arrOrString[k]:
            k += 1
        pi[i] = k
    p = n - pi[-1]
    return p if n % p == 0 else n
