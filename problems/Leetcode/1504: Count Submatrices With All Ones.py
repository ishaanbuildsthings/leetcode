class Solution:
    def numSubmat(self, mat: List[List[int]]) -> int:
        # O(n^2), hard stack + dp
        # we build up-chains and then use the histogram processing per row
        h = len(mat)
        w = len(mat[0])
        up = [[0 for _ in range(w)] for _ in range(h)]
        for r in range(h):
            for c in range(w):
                if r:
                    up[r][c] = 1 + up[r-1][c] if mat[r][c] else 0
                else:
                    up[r][c] = mat[r][c]
        
        def forHist(histRow):
            # for each up-chain we want to consider how many rectangles can include this up-chain, AND how many use a smaller part of this up-chain

            # vertically, we never double-count because two different rows share different bottom-sides for the rectangles
            # horizontally, we do not want to double count up-chains, like
            # 1 1
            # 1 1
            # this grid has two up-chains of size 2 so we need to make sure not to double count them
            # so for an up-chain, we go left until a strictly smaller up-chain, but right until an equal sized up-chain
            leftSmallerOrEqual = [None] * w # (I think I labeled this right)
            stack = [] # mono-increasing # (I think I labeled this right)
            for c in range(w):
                while stack and histRow[c] < histRow[stack[-1]]:
                    poppedI = stack.pop()
                if stack:
                    leftSmallerOrEqual[c] = stack[-1]
                stack.append(c)
            
            rightSmaller = [None] * w # (I think I labeled this right)
            stack = [] # strict increasing (I think I labeled that right)
            for c in range(w - 1, -1, -1):
                while stack and histRow[c] <= histRow[stack[-1]]:
                    poppedI = stack.pop()
                if stack:
                    rightSmaller[c] = stack[-1]
                stack.append(c)
            
            res = 0
            for c in range(w):
                leftCut = leftSmallerOrEqual[c] if leftSmallerOrEqual[c] is not None else -1
                rightCut = rightSmaller[c] if rightSmaller[c] is not None else w
                leftOpts = c - leftCut
                rightOpts = rightCut - c
                res += leftOpts * rightOpts * histRow[c]
            
            return res
        
        return sum(forHist(histRow) for histRow in up)

        # O(n^3), build up-chains then for each cell as a top left corner, scan right computing the bottleneck height
        # height = len(mat)
        # width = len(mat[0])

        # aboveMat = [row[:] for row in mat]
        # for r in range(1, height):
        #     for c in range(width):
        #         if aboveMat[r][c]:
        #             aboveMat[r][c] += aboveMat[r - 1][c]

        # res = 0
        # # fix the bottom left cell
        # for r in range(height):
        #     for c in range(width):
        #         if not mat[r][c]:
        #             continue
        #         # for each bottom left, iterate right while we can
        #         bottleneck = float('inf')
        #         for j in range(c, width):
        #             bottleneck = min(bottleneck, aboveMat[r][j])
        #             res += bottleneck
        
        # return res
                