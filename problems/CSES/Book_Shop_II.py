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

dp = [0] * (maxTotalPrice + 1) # dp[cost] tells us max pages we can form spending exactly cost, technically 0 is wrong we should use -inf but it is fine

for priceOfBundle, pagesInBundle in bundles:
    for newCost in range(maxTotalPrice, -1, -1):
        if newCost - priceOfBundle < 0:
            continue
        newPages = pagesInBundle + dp[newCost - priceOfBundle]
        dp[newCost] = max(dp[newCost], newPages)

print(max(dp))
    




# This is an O(n * maxBudget) solution, it's from chatGPT I haven't written this myself / don't fully get it
# from collections import deque

# numBooks, maxTotalPrice = map(int, input().split())
# prices = list(map(int, input().split()))
# pages = list(map(int, input().split()))
# copies = list(map(int, input().split()))

# # dp[cost] = max pages achievable with exactly this cost
# dp = [float('-inf')] * (maxTotalPrice + 1)
# dp[0] = 0

# for bookPrice, bookPages, maxCopies in zip(prices, pages, copies):
#     previousDP = dp
#     newDP = previousDP[:]  # taking 0 copies is always allowed

#     # Process each residue class modulo bookPrice
#     for remainder in range(bookPrice):
#         window = deque()  # (indexInChain, transformedValue)
#         indexInChain = 0

#         # Iterate costs: remainder, remainder + bookPrice, ...
#         for cost in range(remainder, maxTotalPrice + 1, bookPrice):
#             basePages = previousDP[cost]
#             transformedValue = basePages - indexInChain * bookPages

#             # Maintain deque in decreasing order of transformedValue
#             while window and window[-1][1] <= transformedValue:
#                 window.pop()
#             window.append((indexInChain, transformedValue))

#             # Remove entries outside the allowed copy window
#             minIndexAllowed = indexInChain - maxCopies
#             while window and window[0][0] < minIndexAllowed:
#                 window.popleft()

#             # Best transition for this cost
#             bestTransformed = window[0][1]
#             candidatePages = indexInChain * bookPages + bestTransformed

#             if candidatePages > newDP[cost]:
#                 newDP[cost] = candidatePages

#             indexInChain += 1

#     dp = newDP

# # Total cost must be <= maxTotalPrice
# print(max(dp))
