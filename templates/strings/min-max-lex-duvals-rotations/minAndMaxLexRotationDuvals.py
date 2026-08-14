# TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

# gives the least/greatest lexicographical rotation of any comparable item (string, list, tuple) in O(n) time


# Returns every start index whose rotation equals the lexicographically smallest one, ascending.
# minRotationIndices("bcabca") -> [2, 5] # starting indices that have the min rotation (if multiple, those are equal rotations)
# minRotationIndices([2, 1, 2, 1]) -> [1, 3]
# O(n) time, O(1) extra space for the scan
def minRotationIndices(stringOrArray):
    n = len(stringOrArray)
    if n == 0:
        return []
    i = ans = 0
    period = n
    while i < n:
        ans = i
        j, k = i + 1, i
        while j < 2 * n:
            a = stringOrArray[k - n] if k >= n else stringOrArray[k]
            b = stringOrArray[j - n] if j >= n else stringOrArray[j]
            if b < a:
                break
            k = i if a < b else k + 1
            j += 1
        period = j - k
        while i <= k:
            i += j - k
    if period <= 0 or n % period:   # guard, unreachable on a completed scan
        period = n
    return list(range(ans % period, n, period))


# Returns every start index whose rotation equals the lexicographically largest one, ascending.
# maxRotationIndices("bcabca") -> [1, 4] # starting indices that have the max rotation (if multiple, those are equal rotations)
# maxRotationIndices([2, 1, 2, 1]) -> [0, 2]
# O(n) time, O(1) extra space for the scan
def maxRotationIndices(stringOrArray):
    n = len(stringOrArray)
    if n == 0:
        return []
    i = ans = 0
    period = n
    while i < n:
        ans = i
        j, k = i + 1, i
        while j < 2 * n:
            a = stringOrArray[k - n] if k >= n else stringOrArray[k]
            b = stringOrArray[j - n] if j >= n else stringOrArray[j]
            if b > a:
                break
            k = i if a > b else k + 1
            j += 1
        period = j - k
        while i <= k:
            i += j - k
    if period <= 0 or n % period:   # guard, unreachable on a completed scan
        period = n
    return list(range(ans % period, n, period))


# Returns the lexicographically smallest rotation.
# minRotation("bcabca") -> "abcabc" # the rotation itself, use minRotationIndices for where it starts
# minRotation([2, 1, 2, 1]) -> [1, 2, 1, 2]
# O(n) time
def minRotation(stringOrArray):
    idx = minRotationIndices(stringOrArray)
    if not idx:
        return stringOrArray
    i = idx[0]
    return stringOrArray[i:] + stringOrArray[:i]


# Returns the lexicographically largest rotation.
# maxRotation("bcabca") -> "cabcab" # the rotation itself, use maxRotationIndices for where it starts
# maxRotation([2, 1, 2, 1]) -> [2, 1, 2, 1]
# O(n) time
def maxRotation(stringOrArray):
    idx = maxRotationIndices(stringOrArray)
    if not idx:
        return stringOrArray
    i = idx[0]
    return stringOrArray[i:] + stringOrArray[:i]