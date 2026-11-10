# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/next-permutation/PrevPermutation.inplace.py

# Moves arr in place to be the previous permutation, with looping behavior around to the lexicographical largest
# permutation if we step past the lexicographical min
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
