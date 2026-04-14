class Solution:
    def findPeakGrid(self, mat: List[List[int]]) -> List[int]:
        for i in range(len(mat)):
            mat[i] = [-1] + mat[i] + [-1]
        mat.append([-1] * len(mat[0]))
        mat.insert(0, [-1] * len(mat[0]))
        
        # find column search range
        l = 1
        r = len(mat[0]) - 1
        while l <= r:
            m = (r+l)//2
            # find max in this column
            mxR = None
            mx = -inf
            for ri in range(1, len(mat)):
                if mat[ri][m] > mx:
                    mx = mat[ri][m]
                    mxR = ri
            
            if l == r:
                return (mxR - 1, l - 1)
            
            v = mat[mxR][m]
            left = mat[mxR][m-1]
            right = mat[mxR][m+1]
            if left < v < right:
                l = m + 1
                continue
            if left > v > right:
                r = m - 1
                continue
            if v > max(left, right):
                return (mxR - 1, m - 1)
            
            # divot case doesn't matter
            l = m + 1