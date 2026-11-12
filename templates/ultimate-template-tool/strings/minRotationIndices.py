# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/minRotationIndices.py

# Every start index whose rotation is the lexicographically smallest one (ascending) more than one only when the
# sequence repeats: those rotations are all equal works on a str, list or tuple holding any items that can be ordered
# with < (ints, chars, tuples, ...)
# minRotationIndices("bcabca") -> [2, 5]
# minRotationIndices([2, -1, 2, -1]) -> [1, 3]
# O(n) time, O(n) space
def minRotationIndices(arrOrString):
    n = len(arrOrString)
    if n == 0:
        return []
    doubled = arrOrString + arrOrString
    # Duval: walk the doubled sequence in Lyndon-word blocks; best = start of the smallest rotation found so far
    i = best = 0
    period = n
    while i < n:
        best = i
        j, k = i + 1, i
        while j < 2 * n:
            a = doubled[k]
            b = doubled[j]
            if b < a:
                break
            k = i if a < b else k + 1
            j += 1
        period = j - k
        while i <= k:
            i += j - k
    return list(range(best % period, n, period))
