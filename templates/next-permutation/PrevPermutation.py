# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/PrevPermutation.py

# The next smaller arrangement of sequence (a new list, or a string for a string), or None if it is the smallest
# sequence: a list or a string of values that compare with each other: negatives, floats, chars, tuples ok
def prevPermutation(sequence):
    a = list(sequence)
    i = len(a) - 2
    while i >= 0 and not a[i + 1] < a[i]:
        i -= 1
    if i < 0:
        return None
    j = len(a) - 1
    while not a[j] < a[i]:
        j -= 1
    a[i], a[j] = a[j], a[i]
    a[i + 1:] = reversed(a[i + 1:])
    return "".join(a) if isinstance(sequence, str) else a
