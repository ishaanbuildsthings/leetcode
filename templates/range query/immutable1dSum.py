# ______________________________________________________________________
# IMMUTABLE RANGE SUM QUERY TEMPLATE
# Variables:
# ITERABLE - replace with the iterable we need to query
# prefix[i] is the sum of [0:i-1], so prior elements. prefix[len(itertable)] is queryable and returns the entire sum.

runningSum = 0
prefixSums = [] # store sums of PRIOR elements
for num in ITERABLE:
    prefixSums.append(runningSum)
    runningSum += num
prefixSums.append(runningSum)

def sumQuery(l, r):
    return prefixSums[r + 1] - prefixSums[l]