# https://leetcode.com/problems/count-ways-to-build-rooms-in-an-ant-colony/description/
# difficulty: hard
# tags: math, tree, stars and bars

# Problem
# You are an ant tasked with adding n new rooms numbered 0 to n-1 to your colony. You are given the expansion plan as a 0-indexed integer array of length n, prevRoom, where prevRoom[i] indicates that you must build room prevRoom[i] before building room i, and these two rooms must be connected directly. Room 0 is already built, so prevRoom[0] = -1. The expansion plan is given such that once all the rooms are built, every room will be reachable from room 0.

# You can only build one room at a time, and you can travel freely between rooms you have already built only if they are connected. You can choose to build any room as long as its previous room is already built.

# Return the number of different orders you can build all the rooms in. Since the answer may be large, return it modulo 109 + 7.

# Solution, O(n) time and space + preprocess for factorials, mod inverse can be preprocessed too but that may be a log factor
# First, construct the tree. Then, we have a certain amount of ways for a subchild, we can interleave a second child with something similar to stars and bars, and multiply by the number of orders that new child can go in.

MOD = 10**9 + 7

def facs():
    fac = [1]
    for i in range(1, 10**5 + 1):
        fac.append((fac[-1] * i) % MOD)
    return fac

FACTORIALS = facs()

@cache
def modInverse(num):
    return pow(num, MOD - 2, MOD)

class Solution:
    def waysToBuildRooms(self, prevRoom: List[int]) -> int:
        children = defaultdict(list) # maps a node to nodes that can be built after this one is

        for i in range(len(prevRoom)):
            if prevRoom[i] == -1:
                continue
            children[prevRoom[i]].append(i)

        sizes = {} # maps a node to the size of its subtree
        def size(node):
            # base case
            if len(children[node]) == 0:
                sizes[node] = 1
                return 1

            tot = 1
            for child in children[node]:
                tot += size(child)

            sizes[node] = tot
            return tot


        size(0)


        def numInterleavedSubseq(a, b):
            topFac = FACTORIALS[a + b]
            return (topFac * modInverse(FACTORIALS[a]) * modInverse(FACTORIALS[b])) % MOD

        print(numInterleavedSubseq(0, 3))

        # calculate the number of ways rooted at this node
        def dfs(node):
            # base case
            if len(children[node]) == 0:
                return 1

            ways = 1
            currLength = 0
            for child in children[node]:
                interleave = numInterleavedSubseq(currLength, sizes[child])
                ways *= dfs(child)
                ways *= interleave
                ways %= MOD

                currLength += sizes[child]

            return ways

        return dfs(0)





        # [3, 6, 3]

        # means i have to build 3 before building 0
        # i have to build 3 before building 2


