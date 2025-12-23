import functools

numBooks, maxTotalPrice = map(int, input().split())
prices = list(map(int, input().split()))
pages = list(map(int, input().split()))
copies = list(map(int, input().split()))

# Decompose all 100 book types into log(copies) bundles, worst case is n * log(copies) bundles
# Run 0/1 knapsack on those enumerating the dp[cost] -> max pages, for each item, which is n * cost
# Final time complexity: O(n * log(copies) * maxBudget)

bundles = [] # at most size 10 * n = ~1000, holds (priceOfBundle, pagesInBundle)
for i in range(numBooks):
    price, page, copy = prices[i], pages[i], copies[i]
    power = 0
    while copy:
        bundleSize = min(2**power, copy)
        bundles.append((bundleSize * price, bundleSize * page))
        copy -= bundleSize
        power += 1

dp = [0] * (maxTotalPrice + 1) # dp[cost] tells us max pages we can form spending exactly cost

for priceOfBundle, pagesInBundle in bundles:
    for newCost in range(maxTotalPrice, -1, -1):
        if newCost - priceOfBundle < 0:
            continue
        newPages = pagesInBundle + dp[newCost - priceOfBundle]
        dp[newCost] = max(dp[newCost], newPages)

print(max(dp))
    

