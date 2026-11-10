# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/next-permutation/NextPermutation.inplace.py

# Moves arr in place to be the next permutation, with looping behavior around to the lexicographical smallest
# permutation if we step past the lexicographical max
# Works with a list of any comparable item (int, float, negatives, char, tuple, etc)
def nextPermutation(arr):
    i = len(arr) - 2
    while i >= 0 and not arr[i] < arr[i + 1]:
        i -= 1
    if i >= 0:  # i < 0: it was the largest, so reversing all of it loops around
        j = len(arr) - 1
        while not arr[i] < arr[j]:
            j -= 1
        arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1:] = reversed(arr[i + 1:])
