# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/maxRotation.py

# The lexicographically largest rotation, same type as the input (string, list, tuple)
# works on a str, list or tuple holding any items that can be ordered with < (ints, chars, tuples, ...)
# maxRotation("bcabca") -> "cabcab"
# maxRotation([3, -1, 2]) -> [3, -1, 2]
# O(n) time, O(n) space
def maxRotation(arrOrString):
    n = len(arrOrString)
    if n == 0:
        return arrOrString
    doubled = arrOrString + arrOrString
    # Duval: walk the doubled sequence in Lyndon-word blocks; best = start of the largest rotation found so far
    i = best = 0
    period = n
    while i < n:
        best = i
        j, k = i + 1, i
        while j < 2 * n:
            a = doubled[k]
            b = doubled[j]
            if b > a:
                break
            k = i if a > b else k + 1
            j += 1
        period = j - k
        while i <= k:
            i += j - k
    start = best % period
    return doubled[start : start + n]
