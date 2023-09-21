ITERABLE = 'abc'
# _______________________________________
# PREPROCESSED PALINDROME FOR ALL SUBSTRINGS/SUBARRAYS
# Variables:
# ITERABLE - replace with a string or array
# isPal[l][r] tells us if [l:r] is a palindrome
# Preprocess - O(n^2), isPal[l][r] query - O(1)
isPal = [[False for _ in ITERABLE] for _ in ITERABLE]
# 1 letter pals
for i in range(len(ITERABLE)):
    isPal[i][i] = True
# 2 letter pals
for l in range(len(ITERABLE) - 1):
    if ITERABLE[l] == ITERABLE[l+1]:
        isPal[l][l+1] = True
# length 3 or more pals
for size in range(3, len(ITERABLE) + 1):
    for l in range(len(ITERABLE) - size + 1):
        r = l + size - 1
        if ITERABLE[l] == ITERABLE[r] and isPal[l+1][r-1]:
            isPal[l][r] = True