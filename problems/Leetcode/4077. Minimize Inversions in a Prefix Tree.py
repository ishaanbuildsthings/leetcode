from bisect import bisect_left, bisect_right, insort

class TrieNode:
    def __init__(self):
        self.children = {}
        self.val = None # label if a word ends here, else None
class Trie:
    def __init__(self):
        self.rt = TrieNode()
    def insert(self, word, val):
        curr = self.rt
        for c in word:
            if c not in curr.children:
                curr.children[c] = TrieNode()
            curr = curr.children[c]
        curr.val = val
 
# count of elements > X
def countGtX(arr, x):
    return len(arr) - bisect_right(arr, x)
# count of elements < X 
def countLtX(arr, x):
    return bisect_left(arr, x)
 
class Solution:
    def minInversions(self, words: list[str], target: list[int]) -> int:
        mp = [None] * len(target) # maps number in target to its idx
        for i, v in enumerate(target):
            mp[v] = i

        trie = Trie()
        for i, w in enumerate(words):
            trie.insert(w, mp[i])


        # each word basically gets a digital value, mp[wordI]
        # i want to minimize inversions based on these

        # returns min number of inversions, and a sorted list of all the labels
        def solve(node):
            if not node.children:
                return 0, [node.val]
            totInversions = 0
            childs = []
            for letter, childNode in node.children.items():
                childInv, childArr = solve(childNode)
                totInversions += childInv
                childs.append(childArr)

            numChildren = len(node.children)
            aBeforeB = [[0 for _ in range(numChildren)] for _ in range(numChildren)]
            for a in range(numChildren):
                arrA = childs[a]
                for b in range(a + 1, numChildren):
                    arrB = childs[b]
                    aBeforeBInv = 0
                    bBeforeAInv = 0
                    for idx in arrA:
                        greater = countGtX(arrB, idx)
                        smaller = len(arrB) - greater
                        aBeforeBInv += smaller
                        bBeforeAInv += greater
                    aBeforeB[a][b] = aBeforeBInv
                    aBeforeB[b][a] = bBeforeAInv

            fmask = (1 << numChildren) - 1
            # tells us how many inversions we can minimally make
            @cache
            def dp(mask):
                if mask == fmask:
                    return 0
                res = inf
                for b in range(numChildren):
                    if mask & (1 << b):
                        continue
                    inverts = 0
                    for bit in range(numChildren):
                        if mask & (1 << bit):
                            inverts += aBeforeB[bit][b]
                    res = min(res, inverts + dp(mask | (1 << b)))
                return res
            minInversions = dp(0)

            bigArr = []
            for childArr in childs:
                bigArr.extend(childArr)
            bigArr.sort()
            ownInversions = 0
            if node.val is not None:
                ownInversions = countLtX(bigArr, node.val)
                insort(bigArr, node.val)
            return totInversions + minInversions + ownInversions, bigArr
        return solve(trie.rt)[0]