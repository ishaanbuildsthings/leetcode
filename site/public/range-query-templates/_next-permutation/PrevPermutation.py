# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/next-permutation/PrevPermutation.py

# Returns a new list / string with the previous (next smaller) permutation, with looping behavior around to the
# lexicographical largest permutation if we step past the lexicographical min works with a list of comparable values
# (ints, floats, negatives, chars, tuples) or a string
def prevPermutation(arrOrString):
    a = list(arrOrString)
    i = len(a) - 2
    while i >= 0 and not a[i + 1] < a[i]:
        i -= 1
    if i >= 0:  # i < 0: it was the smallest, so reversing all of it loops around to the maximum
        j = len(a) - 1
        while not a[j] < a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]
    a[i + 1:] = reversed(a[i + 1:])
    return "".join(a) if isinstance(arrOrString, str) else a
