# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/properBorders.py

# properBorders[i] = length of the longest proper prefix of arrOrString[0..i] that is also a suffix of it (this is KMP)
# works on a str, list or tuple holding any items that can be compared with == (ints, chars, tuples, ...)
# properBorders("aabaaab") -> [0, 1, 0, 1, 2, 2, 3]
# properBorders([-1, 2, -1, 2, 5, -1]) -> [0, 0, 1, 2, 0, 1]
# O(n) time and space
def properBorders(arrOrString):
    n = len(arrOrString)
    properBorders = [0] * n
    for i in range(1, n):
        k = properBorders[i - 1]
        while k > 0 and arrOrString[i] != arrOrString[k]:
            k = properBorders[k - 1]
        if arrOrString[i] == arrOrString[k]:
            k += 1
        properBorders[i] = k
    return properBorders
