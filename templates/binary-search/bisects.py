import bisect

# Works for ints and floats. NaN is not supported.
# "first" functions return len(arr) if nothing qualifies.
# "last" functions return -1 if nothing qualifies.
# Each function is O(log n) or O(1).


# FOR INCREASING ARRAYS

def firstIndexLT(arr, threshold):
    return 0 if arr and arr[0] < threshold else len(arr)

def lastIndexLT(arr, threshold):
    index = bisect.bisect_left(arr, threshold)
    return index - 1

def firstIndexLTE(arr, threshold):
    return 0 if arr and arr[0] <= threshold else len(arr)

def lastIndexLTE(arr, threshold):
    index = bisect.bisect_right(arr, threshold)
    return index - 1

def firstIndexGT(arr, threshold):
    return bisect.bisect_right(arr, threshold)

def lastIndexGT(arr, threshold):
    return len(arr) - 1 if arr and arr[-1] > threshold else -1

def firstIndexGTE(arr, threshold):
    return bisect.bisect_left(arr, threshold)

def lastIndexGTE(arr, threshold):
    return len(arr) - 1 if arr and arr[-1] >= threshold else -1


# FOR DECREASING ARRAYS
# Negating every value turns a decreasing array into an increasing one,
# so these search for -threshold with key=lambda x: -x (Python 3.10+).

def firstIndexLTDecreasing(arr, threshold):
    return bisect.bisect_right(arr, -threshold, key=lambda x: -x)

def lastIndexLTDecreasing(arr, threshold):
    return len(arr) - 1 if arr and arr[-1] < threshold else -1

def firstIndexLTEDecreasing(arr, threshold):
    return bisect.bisect_left(arr, -threshold, key=lambda x: -x)

def lastIndexLTEDecreasing(arr, threshold):
    return len(arr) - 1 if arr and arr[-1] <= threshold else -1

def firstIndexGTDecreasing(arr, threshold):
    return 0 if arr and arr[0] > threshold else len(arr)

def lastIndexGTDecreasing(arr, threshold):
    index = bisect.bisect_left(arr, -threshold, key=lambda x: -x)
    return index - 1

def firstIndexGTEDecreasing(arr, threshold):
    return 0 if arr and arr[0] >= threshold else len(arr)

def lastIndexGTEDecreasing(arr, threshold):
    index = bisect.bisect_right(arr, -threshold, key=lambda x: -x)
    return index - 1