# TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

# Prefix function (pi, KMP): pi[i] = length of the longest proper prefix that is also a suffix ending at i
# works on any indexable sequence of comparable items (string, list, tuple)


# prefixFunction("aabaaab") -> [0, 1, 0, 1, 2, 2, 3]
# prefixFunction([1, 2, 1, 2]) -> [0, 0, 1, 2]
# O(n) time, O(n) space
def prefixFunction(arrOrString):
    n = len(arrOrString)
    pi = [0] * n
    for i in range(1, n):
        k = pi[i - 1]
        while k > 0 and arrOrString[i] != arrOrString[k]:
            k = pi[k - 1]
        if arrOrString[i] == arrOrString[k]:
            k += 1
        pi[i] = k
    return pi


# Length of the shortest p such that the sequence is a repeat of its first p items (n if it isn't a repeat).
# shortestPeriod("abcabcabc") -> 3
# shortestPeriod("abcab") -> 5
# O(n) time
def shortestPeriod(arrOrString):
    n = len(arrOrString)
    if n == 0:
        return 0
    p = n - prefixFunction(arrOrString)[-1]
    return p if n % p == 0 else n
