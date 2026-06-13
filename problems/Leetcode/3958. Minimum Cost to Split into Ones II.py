class Solution:
    def minCost(self, n: int) -> int:
        # solution 1, merge from 1s up to N
        # sl = SortedList([(1, n)]) # holds (num, count)
        # res = 0
        # while sl[0][0] != n:
        #     num1, count1 = sl.pop(0)
        #     if count1 == 1:
        #         num2, count2 = sl.pop(0)
        #         res += num1 * num2
        #         sl.add((num1 + num2, 1))
        #         if count2 > 1:
        #             sl.add((num2, count2 - 1))
        #         continue
        #     pairs = count1 // 2
        #     sl.add((num1 + num1, pairs))
        #     if count1 % 2:
        #         sl.add((num1, 1))
        #     res += num1 * num1 * pairs
        
        # return res


        # solution 2, split down from N to 1
        @cache
        def splitCost(x):
            if x == 1:
                return 0
            half = x // 2
            half2 = x - half
            cost = half * half2
            return cost + splitCost(half) + splitCost(half2)
        
        return splitCost(n)