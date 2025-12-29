"""
https://codeforces.com/contest/2174/problem/B is a good example of prefix DP.

Our solution will be to compress the N kids into K:

1/ Our answer will involve paying increasing amounts to children:

[1      3             9]

If we can pay earlier, we always should
[1   3                9]

So we only care about the first occurence of each max storage type. Compress n to size k.

A normal top down solution is dp(i, currBudgetLeft, prevMax), loop over new spending options inside.

This part is kind of a bottom up guide:
We can do this with bottom up push DP. Push DP requires looping over old states, making a choice, and updating a new node.

Remember DP at the point in time when we consider the current item, is the best answer before we use this item.
So we consider spending different amounts at this current item and updating things.

Also, we defined dp[budgetLeft][currMax] to be the best score we can get, including the future segment we are going to walk with the spend we make.
Not sure if we can avoid that, I think we could, and define it to be the best score we get not accounting for that future walk.
But the future walk way seems more clean. We don't worry about the edge case at the last item (we walk to end of the N items) and I think the implementation for other parts gets more clean.


Push DP bottom up O(k^4):

for item in range(kItems):
    for oldBudgetState in range(k + 1):
        for oldCurrMax in range(k + 1): # we could probably clamp this or the budget
            for spendHere in range(oldCurrMax + 1, maxWeCanSpendAtItme + 1):
                ndp[oldBudgetLeft - spendHere][spendHere] = max(ndp[...], dp[oldBudgetState][oldCurrMax] + gainIfSpendXHere)



Pull DP O(k^4)

In pull DP  we are going to loop over new states and see where we could have come from.
We are looping over previous states that could reach this node
We are NOT considering decisions from the previous item, we are considering the current item
For an old state to reach this node, we could either been at this node already and done nothing, or spent the newCurrMax at this item

for item in range(kItems):
    for newBudgetLeft in range(k + 1):
        for newCurrMax in range(maxStorage + 1):
            # to reach this state, we could have just done nothing
            ndp[newBudgetLeft][newCurrMax] = max(ndp[...], dp[newBudgetLeft][newCurrMax] + gain from this position to the next item)
            # or raised up to reach this max, implying we spent newCurrMax at this node
            # this could have happened at multiple old current max nodes
            for oldCurrentMax in range(newCurrMax):
                ndp[newBudgetLeft][newCurrMax] = max(ndp[...]. dp[newBudgetLeft + newCurrMax][oldCurrentMax] + gain from this position to the next item)

Pull DP O(k^3)
Now to optimize this to O(k^3) we observe the inner for loop only cares about the best possible oldCurrentMax. So we construct a prefix and just query that in O(1).

Push DP O(k^3) should be doable but not sure how yet
"""