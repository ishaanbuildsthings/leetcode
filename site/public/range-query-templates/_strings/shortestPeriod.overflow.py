# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/shortestPeriod.overflow.py

# length of the shortest prefix that repeats to form the sequence, where the last copy may be cut off (n if none, 0 if
# empty) i.e. the smallest p with arrOrString[i] == arrOrString[i + p] for every i; p doesn't have to divide n works on
# a str, list or tuple holding any items that can be compared with == (ints, chars, tuples, ...)
# shortestPeriod("abcabcabc") -> 3
# shortestPeriod("abcab") -> 3   # "abc" + "ab"
# shortestPeriod("abcd") -> 4
# shortestPeriod([5, -1, 5]) -> 2
# O(n) time and space
def shortestPeriod(arrOrString):
    n = len(arrOrString)
    if n == 0:
        return 0
    properBorders = [0] * n
    for i in range(1, n):
        k = properBorders[i - 1]
        while k > 0 and arrOrString[i] != arrOrString[k]:
            k = properBorders[k - 1]
        if arrOrString[i] == arrOrString[k]:
            k += 1
        properBorders[i] = k
    return n - properBorders[-1]
