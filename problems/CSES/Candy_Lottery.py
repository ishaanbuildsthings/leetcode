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
