class Solution:
    def countNodes(self, root: Optional[TreeNode]) -> int:
        if not root: return 0
        height = 1
        curr = root
        while curr and curr.left:
            curr = curr.left
            height += 1

        inLevel = 2**height
        before = 0
        for level in range(height - 1):
            before += 2**level
        
        # binary search for the rightmost
        l = 0
        r = inLevel
        res = None
        while l <= r:
            m = (l + r) // 2
            currId = before + m + 1 # there are `currId` nodes
            path = []
            # parent is id//2
            while currId:
                path.append(currId)
                currId //= 2
            path = path[::-1]

            # walk the path and see if it exists
            currNode = root
            for i in range(1, len(path)):
                v = path[i]
                if v == 2 * path[i-1]:
                    currNode = currNode.left
                else:
                    currNode = currNode.right
                if currNode is None:
                    break
                
            if currNode is None:
                r = m - 1
            else:
                res = m
                l = m + 1
        
        return res + before + 1


        
        
