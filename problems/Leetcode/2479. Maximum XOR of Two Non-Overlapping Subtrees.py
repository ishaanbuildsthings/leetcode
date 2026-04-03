class BitTrie:
    def __init__(self, BITS):
        self.root = {}
        self.BITS = BITS
    
    def insert(self, num):
        curr = self.root
        for bitOffset in range(self.BITS - 1, -1, -1):
            bit = (num >> bitOffset) & 1
            if bit in curr:
                curr = curr[bit]
            else:
                newChild = {}
                curr[bit] = newChild
                curr = newChild
    
    def queryMaxXor(self, numToBeXord):
        res = 0
        curr = self.root
        for bitOffset in range(self.BITS - 1, -1, -1):
            numBit = (numToBeXord >> bitOffset) & 1
            desiredBit = numBit ^ 1

            if desiredBit in curr:
                res |= (1 << bitOffset)
                curr = curr[desiredBit]
            else:
                curr = curr[numBit]
        return res

    def queryMinXor(self, numToBeXord):
        res = 0
        curr = self.root
        for bitOffset in range(self.BITS - 1, -1, -1):
            numBit = (numToBeXord >> bitOffset) & 1

            if numBit in curr:
                curr = curr[numBit]
            else:
                res |= (1 << bitOffset)
                curr = curr[numBit ^ 1]
                
        return res

class Solution:
    def maxXor(self, n: int, edges: List[List[int]], values: List[int]) -> int:
        def edgeListToTree(edgeList):
            edgeMap = defaultdict(list)
            for a, b in edgeList:
                edgeMap[a].append(b)
                edgeMap[b].append(a)

            children = defaultdict(list) # maps a node to its children

            def buildTree(node, parent):
                for adj in edgeMap[node]:
                    if adj == parent:
                        continue
                    children[node].append(adj)
                    buildTree(adj, node)
            buildTree(0, -1) # root at 0
            return children

        children = edgeListToTree(edges)

        @cache
        def tot(node):
            if not children[node]:
                return values[node]
            return values[node] + sum(tot(child) for child in children[node])

        res = 0

        def dfs(node):
            nonlocal res

            # base case
            if not children[node]:
                bt = BitTrie(50)
                bt.insert(values[node])
                # send up a list of all valid subtree sums
                return bt, [values[node]]
            
            childrenSums = [dfs(child) for child in children[node]]
            childrenSums.sort(key=lambda x : len(x[1]), reverse=True)
            bt, heavyVals = childrenSums[0]
            for i in range(1, len(childrenSums)):
                for v in childrenSums[i][1]:
                    mx = bt.queryMaxXor(v)
                    res = max(res, mx)
                for v in childrenSums[i][1]:
                    bt.insert(v)
                    heavyVals.append(v)
            bt.insert(tot(node))
            heavyVals.append(tot(node))
            return bt, heavyVals
        
        dfs(0)

        return res