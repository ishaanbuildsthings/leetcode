class Solution:
    def isPreorder(self, nodes: List[List[int]]) -> bool:
        n = len(nodes)

        nodeLabelToIndex = {}
        for i in range(len(nodes)):
            nodeLabel = nodes[i][0]
            nodeLabelToIndex[nodeLabel] = i
        
        prev = -1 # global position of where we are

        failFound = False

        children = defaultdict(list) # maps INDEX to INDICES, not node labels
        for i in range(n):
            nodeLabel, parentLabel = nodes[i]
            if parentLabel != -1:
                parentIndex = nodeLabelToIndex[parentLabel]
                children[parentIndex].append(i)


        def preorder(i):
            nonlocal prev
            nonlocal failFound
            if i != prev + 1:
                failFound = True
                return
            prev = i

            for childIndex in children[i]:
                preorder(childIndex)
        
        for i in range(n):
            if nodes[i][1] == -1:
                preorder(i)
                break

        if failFound:
            return False
        
        return True

                
