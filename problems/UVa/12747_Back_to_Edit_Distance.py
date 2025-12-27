T = int(input())
for t in range(T):
    n = int(input())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))

    # Imagine we transform A -> B with some operations
    # There were some elements (possibly none) in A that we never deleted
    # They appear as a subsequence in B too
    # Everything else got deleted and therefore re-inserted
    # So the optimal answer requires finding the LCS and then the remaining elements each use 2 operations
    # How to find LCS?
    # [1, 3, 5, 4, 2]
    # [1, 5, 4, 3, 2]
    # remap the first array to be the indices they occur in the second array
    # [0, 3, 1, 2, 4]
    # now an increasing subsequence in the indices implies we saw those from left to right in array B
    # we also saw them from left to right in array A because we read it from left to right
    # this is a common subsequence then as it appears left to right in both A and B
    # to find the longest common one, then we just find the LIS on the indices array

    bToIdx = {v : i for i, v in enumerate(B)}
    A = [bToIdx[v] for v in A]

    # to find the LIS in n log n, we maintain the smallest number we can keep at the end with a subsequence of length i+1
    tails = []
    for v in A:
        # find the rightmost tail we are greater than
        # necessarily we will be less than the tail one to the right of it
        # we update that tail
        # or if we are greater than every tail present, we append a new subsequence

        # [1, 3, 5, 8]
        # inserting a 6

        l = 0
        r = len(tails) - 1
        resI = None
        while l <= r:
            m = (r+l)//2
            tail = tails[m]
            if v > tail:
                resI = m
                l = m + 1
            else:
                r = m - 1
        # cleaner way would be find first index > v, that reduces to 2 cases
        # we are greater than nothing
        if resI is None:
            if tails:
                tails[0] = v
            else:
                tails = [v]
        # we are greater than everything
        elif resI == len(tails) - 1:
            tails.append(v)
        else:
            tails[resI + 1] = v
        
    lcs = len(tails)
    edited = n - lcs
    print(f'Case {t+1}: {edited * 2}')