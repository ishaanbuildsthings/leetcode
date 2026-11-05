# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/NextPermutation.inplace.py

# Rearranges sequence into the next larger arrangement in place and returns True, or returns False (sequence
# unchanged) if it is the largest; consecutive calls cost O(1) amortized, unless almost every value is the same
# sequence: a list of values that compare with each other: negatives, floats, chars, tuples ok
def nextPermutation(sequence):
    i = len(sequence) - 2
    while i >= 0 and not sequence[i] < sequence[i + 1]:
        i -= 1
    if i < 0:
        return False
    j = len(sequence) - 1
    while not sequence[i] < sequence[j]:
        j -= 1
    sequence[i], sequence[j] = sequence[j], sequence[i]
    sequence[i + 1:] = reversed(sequence[i + 1:])
    return True
