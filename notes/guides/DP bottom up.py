"""
Bottom up DP requires thinking about:
1/ The order of our for loops
2/ The order we iterate, inside a for loop
3/ If we update the value in our loop, dp[x] = ..., or a different value from our loop, dp[x + 1] = ...
4/ If we need to re-duplicate a cache or if we can avoid it

Let us look at some cases:

UNBOUNDED KNAPSACK
https://leetcode.com/problems/coin-change/
Given 12 coin denomiations, coins[i] <= 1e9, and an amount <= 1e4, minimum # of coins to form that amount? Repeats allowed.

Recurrence relationship is: given a coin and a previous doable amount, a new doable amount can be formed. To update dp[x] we will use dp[x - ?].
"""

# dp[amount] is min # of coins to form that amount
dp = [inf] * (amount + 1)
dp[0] = 0
for coin in coins:
    for amt in range(coin, amount + 1):
        dp[amt] = min(dp[amt], dp[amt - coin] + 1)
return dp[-1] if dp[-1] != inf else -1

"""
#1
Our DP does NOT depend on the index of the coin we are at, so we can order the for loops in either direction
#2
To update dp[x] we need smaller dp[x - ?]. Since we can use a coin multiple times, we should loop UP in our amount. If we loop down it gets messed up
since it is unbounded knapsack. We want to make sure we can re-use the same coin multiple times. We could loop down only if we represent dp[x] as the 
minimum # of coins to go from X to our target amount, which is effectively the same problem.
#4
Duplicating the cache is not relevant. We do that in 0/1 knapsack when we don't want to accidentally pick the same element multiple times in one iteration of the outer loop.
"""

# Different loop order, no difference
cache = [inf] * (amount + 1)
cache[0] = 0
for amt in range(1, amount + 1):
    for coin in coins:
        if amt - coin < 0:
            continue
        cache[amt] = min(cache[amt], cache[amt - coin] + 1)
return cache[-1] if cache[-1] != inf else -1

"""
0-1 Knapsack
https://leetcode.com/problems/maximum-sum-of-three-numbers-divisible-by-three/description/

Given numbers, pick 3 that have the biggest sum divisible by 3. N <= 1e5.
"""

# Using dp and new dp array, we can write the inner two for loops in any order. We cannot move the outermost N loop though. Our DP needs a clear concept of "caches before this item" and "caches after this item".
dp = [[-inf] * 4 for _ in range(4)]
dp[0][0] = 0
for i in range(len(nums)):
    ndp = [x[:] for x in dp]
    for r in range(2, -1, -1): # Order of these two loops doesn't matter.
        for taken in range(2, -1, -1): # Also order inside these two for loops doesn't matter
        newR = (r + nums[i]) % 3
        ndp[newR][taken+1] = max(dp[newR][taken + 1], dp[r][taken] + nums[i])                
    dp = ndp
return max(0, dp[0][3])

# If we don't want ndp, we have to write the cache in an order where we don't write to a spot then read from it.
dp = [[-inf] * 4 for _ in range(4)]
dp[0][0] = 0
for i in range(len(nums)):
    for taken in range(2, -1, -1): # Order of these two loops DOES matter, we write to bigger takens so ALL smaller takens must be solved first. The taken loop must also descend.
        for r in range(4): # This for loop could run in either direction since we are reading from all smaller taken cells anyway
            newR = (r + nums[i]) % 3
            dp[newR][taken+1] = max(dp[newR][taken + 1], dp[r][taken] + nums[i]) # We could also do a pull style here instead since we have a monotone “increasing dimension” that we can iterate in the safe direction
return max(0, dp[0][3])

# We can also do a pull style with ndp but it felt less natural to me.
dp = [[-inf] * 4 for _ in range(4)] # dp[remainder][taken]
dp[0][0] = 0
for num in nums:
    ndp = [x[:] for x in dp]
    for r in range(3):
        oldR = (r - num) % 3
        for taken in range(1, 4):
            ndp[r][taken] = max(dp[r][taken], dp[oldR][taken - 1] + num) # pulling here
    dp = ndp
return max(dp[0][3], 0)

"""
If a transition can go from state A → B, you must ensure your iteration order never processes B before A within the same item/step in a way that would allow chaining.
In general: sometimes nesting order matters, especially in multi-dimensional in-place DP where more than one coordinate changes, or updates happen within the same layer.

If we loop on for s in range(...) we might update dp[s] OR update dp[s + ?]. This is not a difference of 01 vs unbound. 01 vs unbound is if we loop up or down.
01:
dp[s] |= dp[s-x] # reads smaller
dp[s+x] |= dp[s] # writes bigger

unbound:
dp[s] = min(dp[s], dp[s-x] + 1)
dp[s+x] = min(dp[s+x], dp[s] + 1)

So: it is not “0/1 updates different state, unbounded updates same state”.
It is “0/1 forbids within-step reuse; unbounded allows it”.
"""

# Can we form the sum[W] from nums?

def subsetSum01_pull(nums, W):
    dp = [False] * (W + 1)
    dp[0] = True
    for x in nums:
        for s in range(W, x - 1, -1):   # DOWN
            dp[s] = dp[s] or dp[s - x]
    return dp[W]

def subsetSum01_push(nums, W):
    dp = [False] * (W + 1)
    dp[0] = True
    for x in nums:
        for s in range(W - x, -1, -1):  # DOWN
            if dp[s]:
                dp[s + x] = True
    return dp[W]

def subsetSumUnbounded_pull(nums, W):
    dp = [False] * (W + 1)
    dp[0] = True
    for x in nums:
        for s in range(x, W + 1):       # UP
            dp[s] = dp[s] or dp[s - x]
    return dp[W]

def subsetSumUnbounded_push(nums, W):
    dp = [False] * (W + 1)
    dp[0] = True
    for x in nums:
        for s in range(0, W - x + 1):   # UP
            if dp[s]:
                dp[s + x] = True
    return dp[W]

# Bitset DP is naturally expressed as a PUSH.
# https://leetcode.com/problems/partition-equal-subset-sum/
tot = sum(nums)
if tot % 2: return False
half = tot // 2
bs = 1 # 0 is doable
for num in nums:
    nbs = bs << num
    bs |= nbs # all new values are updated using all old values at the same time
return bool(bs >> half & 1)

