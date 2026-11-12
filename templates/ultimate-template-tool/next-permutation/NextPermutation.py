# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/next-permutation/NextPermutation.py

# Returns a new list / string with the next larger permutation, with looping behavior around to the lexicographical
# smallest permutation if we step past the lexicographical max works with a list of comparable values (ints, floats,
# negatives, chars, tuples) or a string
def nextPermutation(arrOrString):
    a = list(arrOrString)
    i = len(a) - 2
    while i >= 0 and not a[i] < a[i + 1]:
        i -= 1
    if i >= 0:  # i < 0: it was the largest, so reversing all of it loops around to the minimum
        j = len(a) - 1
        while not a[i] < a[j]:
            j -= 1
        a[i], a[j] = a[j], a[i]
    a[i + 1:] = reversed(a[i + 1:])
    return "".join(a) if isinstance(arrOrString, str) else a
