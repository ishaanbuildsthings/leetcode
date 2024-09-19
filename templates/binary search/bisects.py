import bisect

# FOR INCREASING ARRAYS

# -1 if no number is < threshold
def firstIndexLT(arr, threshold):
    index = bisect.bisect_left(arr, threshold)
    return index - 1 if index > 0 and arr[index - 1] < threshold else -1

# -1 if no number is < threshold
def lastIndexLT(arr, threshold):
    index = bisect.bisect_left(arr, threshold)
    return index - 1 if index > 0 else -1

# -1 if no number is <= threshold
def firstIndexLTE(arr, threshold):
    index = bisect.bisect_left(arr, threshold)
    return index - 1 if index > 0 and arr[index - 1] == threshold else -1

# -1 if no number <= threshold
def lastIndexLTE(arr, threshold):
    index = bisect.bisect_right(arr, threshold)
    return index - 1 if index > 0 else -1

# len(arr) if no number is > threshold
def firstIndexGT(arr, threshold):
    index = bisect.bisect_right(arr, threshold - 1)
    return index if index < len(arr) and arr[index] > threshold else len(arr)

# len(arr) if no number is > threshold
def lastIndexGT(arr, threshold):
    index = bisect.bisect_right(arr, threshold)
    return index if index < len(arr) else len(arr)

# len(arr) if no number is >= threshold
def firstIndexGTE(arr, threshold):
    index = bisect.bisect_left(arr, threshold)
    return index if index < len(arr) else len(arr)

# len(arr) if no number is >= threshold
def lastIndexGTE(arr, threshold):
    index = bisect.bisect_right(arr, threshold - 1)
    return index if index < len(arr) else len(arr)


# FOR DECREASING ARRAYS

# len(arr) if no number is >= threshold
def lastIndexGTE(arr, threshold):
    l = 0
    r = len(arr) - 1
    while l <= r:
        m = (r + l) // 2
        if arr[m] >= threshold:
            l = m + 1
        else:
            r = m - 1
    return l - 1