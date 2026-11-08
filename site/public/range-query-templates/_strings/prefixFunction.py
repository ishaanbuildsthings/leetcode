# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/prefixFunction.py

# pi[i] = length of the longest proper prefix that is also a suffix of arrOrString[0..i]
# prefixFunction("aabaaab") -> [0, 1, 0, 1, 2, 2, 3]
# prefixFunction([1, 2, 1, 2]) -> [0, 0, 1, 2]
# O(n) time and space
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
