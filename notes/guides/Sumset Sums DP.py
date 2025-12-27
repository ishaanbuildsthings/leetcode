"""
Subset sums can be feasibility (can we form this sum), mins (fewest components to merge to make this sum), and maxes.

There are varying constraints on the task, number of elements, total sum of elements, max sum of each element, how many copies there are of an element, value of the element, and more.\

Feasibility can be solved with bitsets since it normally stores a boolean.
"""

# Some miscellaneous ideas for problem solving:

"""
1e5 unique sized elements (sum(A) <= 1e9) means our bitset is going to be too big. I don't think we can check if a subset sum Q (Q<=1e9) is doable.

If the Q query is <= 1e5, we can cap our bitset at 1e5 and it becomes (# of components * capped bitset size) / W

If sum(A) <= 1e5 we have at most root(sum) unique sizes. Since 1 + 2 + 3 + ... + rootN = N complexity. For each unique size we shift our bitset up to at most sum(A).
So I think it reduces to root N * S / W.
I think binary bundle splitting will not help us here since each component size is different.

Bundle splitting helps when we have fewer elements but lots of copies of them. For instance Book Shop II cses. I think if sum(A) <= 1e5 it doesn't help since we have 
at most root N copies anyway and we would do root(N) * S iterations (or divided by W if only checking feasibility). If we had rootN copies all size rootN we could save time
but that is not worst case complexity. I tried on Codeforces - Lucky Country to not use binary splitting and it did not AC, but I think it doesn't actually improve time complexity.

If we need a max value under a cost we need a dp[cost] array which tells us the max value for spending exactly that cost. This means we lose the bitset. Also min # of merges or max # of merges
can be done in the DP.

There is something about a monotonic deque which can help drop a log factor in some problems like Book Shop II but I don't understand it.

If we have huge costs but small values we can make the values the DP param and store the minimum cost in the dp table.

A bitset can tell if a bit is set in O(1) with a proper implementation I think, instead of python big integers. For instance in Atcoder Median Sum I needed to find the middle set bit in a big mask.
# Implementing a custom Python class or using C++ builtins would help do that faster than:
for offset in range(1e6):
    if (1 << offset) & bitset # could be an O(1) check, but don't fully understand a proper bitset implementation
Which is 1e12 / W.

If we have small weights and a huge target value and huge quantities of weights, we cannot have the target value be a parameter of the DP. So we need to figure out a residue set we can form and use that.
See Codeforces - E. Knapsack

We can generate all subset sums even for huge items in a few ways, problem: https://cses.fi/problemset/task/1623/
Don't use a bitset since the weights are too big. Just store valid weights in an array [1, 5, 80, ...] and double the array size as we add on more elements.
We can also use a different DP which also tells us which subset forms each sum:
subsetSum = [0] * (1 << n)
for mask in range(1, 1 << n):
    lsb = mask & -mask
    i = (lsb.bit_length() - 1)
    subsetSum[mask] = subsetSum[mask ^ lsb] + a[i]
Also, we can use meet in the middle for a larger constraint. Pick some subset sum from the left half and binary search for the best right sum in the right half.

There is some other technique similar to the binary bundle splitting. Imagine we have various weights [a, a, b, b, b, c, c, d, ...] where S <= 1e5.
Any time a weight appears > 2 times, so [a, a, a] for example, just replace it with [a, 2a]. Basically at the end we should get weights where each weight appears at most twice.
We have at most root N unique weight sizes already, and since there are at most 2 of each weight type now, we have root N weights.
I think it would perform similar to the bundle splitting decomposition.
https://codeforces.com/blog/entry/97396?#comment-863912


If we have N items each with weight w_i, find a set S such that the total sum is C.
Just to find if it is feasible we can do bitset dp which is N*C/W.
If we want to reconstruct the set, we still can with a bitset! When we do bs |= bs << shift, we actually want to do:
newBs = bs | bs << shift
newSetBits = newBs ^ bs
Now we get the newly set bits, for each one we assign the parent pointer. It is amortized.
We can also write it as:
shifted = bs << w
newSetBits = shifted & ~bs
bs |= shifted
I don't believe we can keep the bitset technique for min # of weights to form a sum C. For example [1, 1, 1, 1, 4] and we want to get sum 4.
After our first 4 weights we would form a sum 4 and it would never be new again, but we did not take the minimum # of elements.
https://codeforces.com/blog/entry/98663
I believe this guide also shows how my bundle splitting actually doesn't add a log when sum <= 1e5, and how the [a, a, a] -> [a, 2a] technique also would not add a log.
There are other advanced things in that blog I haven't understood yet. Like "Subset Sum Speedup 2".
"""