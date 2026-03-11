class Solution:
    def generateTrees(self, n: int) -> List[Optional[TreeNode]]:
        @cache
        def build(l, r):
            if l > r:
                return [None]
            if l == r:
                return [TreeNode(l)]

            result = []
            for rootNum in range(l, r + 1):
                for leftConfig in build(l, rootNum - 1):
                    for rightConfig in build(rootNum + 1, r):
                        result.append(TreeNode(rootNum, leftConfig, rightConfig))
            return result

        return build(1, n)