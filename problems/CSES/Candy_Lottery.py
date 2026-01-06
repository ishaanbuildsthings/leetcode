# Solution 1
# Compute the exact change max=X for all X and take their weighted sums
# First, compute chance of a max being 1
# From this, we compute chance of maximum being at most 2
# We can compute the chance max is exactly 2 by subtracting. Repeat this
from decimal import Decimal, getcontext, ROUND_HALF_EVEN

n, k = map(int, input().split())

getcontext().prec = 80

res = Decimal(0)
oddsAll = [Decimal(0)] * (k + 1) # oddsAll[upperBound] is the chance all numbers are <= upperBound (different from upperBound being guaranteed the maximum)

# compute the chance that no number is > mx (different from mx being the max)
for mx in range(1, k + 1):
    singleChance = Decimal(mx) / Decimal(k)
    allChance = singleChance ** Decimal(n)
    oddsExact = allChance - oddsAll[mx - 1]
    oddsAll[mx] = allChance
    weightedContribution = oddsExact * Decimal(mx)
    res += weightedContribution

print(res.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN))



# Solution 2
# Define indicators, I1 = chance max is >= 1, I2 = chance max is >= 2, etc
# Now when max is X, we score I1 + I2 + ... + IX
# So we need to compute the expected sum of the indicators
# Each indicator has a chance of occuring and we can use linearity of expectation to get their probabilities
# It just uses inverse probability to compute these
# from decimal import Decimal, getcontext, ROUND_HALF_EVEN

# n, k = map(int, input().split())

# getcontext().prec = 80

# res = Decimal(0)

# # compute the chance the maximum is >= mx (indicator approach)
# for mx in range(1, k + 1):
#     singleChance = Decimal(mx - 1) / Decimal(k)
#     allChance = singleChance ** Decimal(n)
#     oddsGte = Decimal(1) - allChance
#     res += oddsGte

# print(res.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN))
