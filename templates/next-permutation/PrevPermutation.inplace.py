# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/PrevPermutation.inplace.py

# Moves arr in place to be the previous permutation, if it was already the lexicographical smallest it loops around.
# Works with a list of any comparable item (int, float, negatives, char, tuple, etc)
def prevPermutation(arr):
    i = len(arr) - 2
    while i >= 0 and not arr[i + 1] < arr[i]:
        i -= 1
    if i >= 0:  # i < 0: it was the smallest, so reversing all of it loops around
        j = len(arr) - 1
        while not arr[j] < arr[i]:
            j -= 1
        arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1:] = reversed(arr[i + 1:])
    return i >= 0  # False when it looped around
