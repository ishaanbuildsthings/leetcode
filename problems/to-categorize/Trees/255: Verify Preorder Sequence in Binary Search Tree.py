# tags: bst, stack, preorder

# Solution, O(n) space and time

class Solution:
    def verifyPreorder(self, preorder: List[int]) -> bool:
        firstIndexOnRightWithGreaterVal = {}
        stack = [0] # stores indices
        for i in range(1, len(preorder)):
            newVal = preorder[i]
            while stack and newVal > preorder[stack[-1]]:
                firstIndexOnRightWithGreaterVal[stack[-1]] = i
                stack.pop()
            stack.append(i)


        def recurse(l, r, leftBound, rightBound):
            # base case
            if l > r:
                return leftBound < rightBound

            rootVal = preorder[l]

            # if no element on the right is bigger
            if not l in firstIndexOnRightWithGreaterVal:
                return recurse(l + 1, r, leftBound, rootVal)

            firstBiggerIndex = firstIndexOnRightWithGreaterVal[l]
            isLeftSubtreeValid = recurse(l + 1, firstBiggerIndex - 1, leftBound, rootVal)
            isRightSubtreeValid = recurse(firstBiggerIndex, r, rootVal, rightBound)
            return isLeftSubtreeValid and isRightSubtreeValid


        return recurse(0, len(preorder) - 1, float('-inf'), float('inf'))


