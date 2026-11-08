# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/zFunction.py

# z[i] = longest common prefix of the entire sequence against the suffix starting at i (z[0] = n)
# zFunction("aabxaab") -> [7, 1, 0, 0, 3, 1, 0]
# zFunction([1, 2, 1, 2]) -> [4, 0, 2, 0]
# O(n) time and space
def zFunction(arrOrString):
    n = len(arrOrString)
    z = [0] * n
    if n == 0:
        return z
    z[0] = n
    l = r = 0  # [l, r) = the match reaching furthest right so far
    for i in range(1, n):
        k = 0
        if i < r:
            k = min(r - i, z[i - l])
        while i + k < n and arrOrString[k] == arrOrString[i + k]:
            k += 1
        z[i] = k
        if i + k > r:
            l, r = i, i + k
    return z
