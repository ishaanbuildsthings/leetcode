class Solution:
    def maxAbsValExpr(self, arr1: List[int], arr2: List[int]) -> int:
        
        def procedure(a1, a2):
            # going to assume the RIGTH number is bigger for both
            # a1[j] >= a1[i] AND a2[j] >= a2[i]

            res = 0

            # we are subtracting both a1[i] and a2[i]
            pfMin = a1[0] + a2[0]
            for r in range(1, len(a1)):
                gained1 = a1[r]
                gained2 = a2[r]
                score = gained1 + gained2 - pfMin + r

                res = max(res, score)

                pfMin = min(pfMin, gained1 + gained2 + r)
            
            return res


        rightRight = procedure(arr1, arr2)
        leftLeft = procedure(arr1[::-1], arr2[::-1])

        neg1 = [-1 * x for x in arr1]
        neg2 = [-1 * x for x in arr2]

        ans1 = max(rightRight, leftLeft)
        ans2 = max(procedure(arr1, neg2), procedure(neg1, arr2))

        return max(ans1, ans2)

