class Solution:
    def pathSum(self, nums: List[int]) -> int:
        res = 0
        idxToNode = {} # maps an idx -> the actual number being stored

        for num in nums:
            s = str(num)
            depth = int(s[0])
            position = int(s[1])
            nodesBefore = 2**(depth - 1) - 1
            idx = nodesBefore + position
            idxToNode[idx] = num
        
        print(idxToNode)

            # 1+2+4
            # level=4, pos=1
            # 2^(level-1)-1 is nodes before
        
        def dfs(nodeIdx, currSum):
            nonlocal res
            # at a leaf
            if not 2 * nodeIdx in idxToNode and not 2 * nodeIdx + 1 in idxToNode:
                res += currSum + idxToNode[nodeIdx] % 10
                return
            v = idxToNode[nodeIdx]
            value = v % 10
            print(f'value: {value}')
            if (2 * nodeIdx) in idxToNode:
                dfs(2 * nodeIdx, currSum + value)
            if (2 * nodeIdx + 1) in idxToNode:
                dfs(2 * nodeIdx + 1, currSum + value)
        
        dfs(1, 0)

        return res
            

