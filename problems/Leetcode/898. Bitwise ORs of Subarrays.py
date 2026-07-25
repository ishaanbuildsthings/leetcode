class Solution:
    def subarrayBitwiseORs(self, arr: List[int]) -> int:
        # proof that the answer is at most log2(max(arr)) * n
        # consider an element in the arr, it has some set bits, call the index l
        # now consider up to n possible right indices, r
        # if we consider all l's, and for each l, every r, that is all n^2 subarrays
        # for a given starting l, we have some set bits
        # for each r as we iterate to the right, there are only up to 30 bits we can add on, due to how OR works
        # so for each l we can only produce 30 unique ORs
        ors = {arr[0]}
        totalOrs = {arr[0]}
        for i in range(1, len(arr)):
            newOrs = {arr[i]}
            totalOrs.add(arr[i])
            for prevOr in ors:
                newOrs.add(arr[i] | prevOr)
                totalOrs.add(arr[i] | prevOr)
            ors = newOrs
        return len(totalOrs)