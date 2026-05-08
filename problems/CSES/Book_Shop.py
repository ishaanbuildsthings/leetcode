numBooks, maxSpend = map(int, input().split())
prices = list(map(int, input().split()))
pages = list(map(int, input().split()))
 
 
# # dp[index][spent] is the max number of pages we can get by spending exactly spent in the 0...index books
# dp = [[-1] * (maxSpend + 1) for _ in range(numBooks)]
# fmax = lambda x, y: x if x > y else y
 
# # iterate over books
# for i in range(len(prices)):
#   price = prices[i]
#   page = pages[i]
#   for spendAmount in range(maxSpend + 1):
#     resHere = 0
#     if i > 0:
#       ifDontBuyThisBook = dp[i - 1][spendAmount]
#       resHere = ifDontBuyThisBook
#     if price <= spendAmount and i > 0:
#       ifBuy = dp[i - 1][spendAmount - price] + page
#       resHere = fmax(resHere, ifBuy)
#     # or for first row
#     if price <= spendAmount:
#       resHere = fmax(resHere, page)
#     dp[i][spendAmount] = resHere
 
# print(max(dp[-1]))
 
 
dp = [0] * (maxSpend + 1)
for i in range(len(prices)):
  price = prices[i]
  page = pages[i]
  for spendAmount in range(maxSpend, -1, -1):
    if price > spendAmount:
      continue
    ifBuy = dp[spendAmount - price] + page
    dp[spendAmount] = max(dp[spendAmount], ifBuy)
print(max(dp))