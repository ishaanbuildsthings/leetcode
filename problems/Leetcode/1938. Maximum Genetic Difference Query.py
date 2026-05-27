class Solution:
    def maxGeneticDifference(self, parents: List[int], queries: List[List[int]]) -> List[int]:

        # build adj list
        n = len(parents)
        adjList = [[] for _ in range(n)]
        root = 0
        for node, par in enumerate(parents):
            if par == -1:
                root = node
            else:
                adjList[node].append(par)
                adjList[par].append(node)

        # hld setup
        parentArr = [-1] * n
        depthArr = [0] * n
        sizeArr = [0] * n
        heavyArr = [-1] * n

        def dfs(node, par):
            parentArr[node] = par
            sizeArr[node] = 1
            maxSub = 0
            for child in adjList[node]:
                if child == par:
                    continue
                depthArr[child] = depthArr[node] + 1
                dfs(child, node)
                sizeArr[node] += sizeArr[child]
                if sizeArr[child] > maxSub:
                    maxSub = sizeArr[child]
                    heavyArr[node] = child

        dfs(root, -1)

        # hld decompose

        headArr = [0] * n
        posArr = [0] * n
        chainId = [0] * n
        chainNodes = []

        def decompose(node, head):
            if head == node:
                chainNodes.append([])

            cid = len(chainNodes) - 1

            chainId[node] = cid
            headArr[node] = head
            posArr[node] = len(chainNodes[cid])
            chainNodes[cid].append(node)

            if heavyArr[node] != -1:
                decompose(heavyArr[node], head)

            for child in adjList[node]:
                if child != parentArr[node] and child != heavyArr[node]:
                    decompose(child, child)

        decompose(root, root)

        # bit trie functions
        maxBits = 18
        leftChild = [0]
        rightChild = [0]

        def newNode():
            leftChild.append(0)
            rightChild.append(0)
            return len(leftChild) - 1

        def insert(prevRoot, val):
            cur = newNode()
            resRoot = cur
            prev = prevRoot
            for bit in range(maxBits, -1, -1):
                b = (val >> bit) & 1
                l = leftChild[prev] if prev else 0
                r = rightChild[prev] if prev else 0
                leftChild[cur] = l
                rightChild[cur] = r
                nxt = newNode()
                if b == 0:
                    leftChild[cur] = nxt
                    prev = l
                else:
                    rightChild[cur] = nxt
                    prev = r
                cur = nxt
            return resRoot

        # find max XOR of a value against a bit trie in O(log(max))
        def maxXor(rootNode, val):
            cur = rootNode
            ans = 0
            for bit in range(maxBits, -1, -1):
                if not cur:
                    break
                b = (val >> bit) & 1
                want = 1 ^ b
                nxt = rightChild[cur] if want else leftChild[cur]
                if nxt:
                    ans |= 1 << bit
                    cur = nxt
                else:
                    cur = leftChild[cur] if b == 0 else rightChild[cur]
            return ans

        chainRoots = []
        for nodes in chainNodes:
            roots = [0]
            for node in nodes:
                roots.append(insert(roots[-1], node))
            chainRoots.append(roots)

        res = [0] * len(queries)
        
        for i, (node, val) in enumerate(queries):
            best = 0
            curNode = node
            while True:
                cid = chainId[curNode]
                rootAtPos = chainRoots[cid][posArr[curNode] + 1]
                best = max(best, maxXor(rootAtPos, val))
                if headArr[curNode] == root:
                    break
                curNode = parentArr[headArr[curNode]]
            res[i] = best
        return res