class Solution:
    def wiggleSort(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        # 1 1 2 2 3 3

        # 1 3 1 3 2 2 
        d = sorted(nums)
        m = len(nums) // 2
        if len(nums) % 2:
            m += 1
        L = d[:m]
        R = d[m:]
        mn = min(len(L), len(R))
        res = []
        for i in range(mn):
            back1 = L[~i]
            back2 = R[~i]
            res.append(back1)
            res.append(back2)
        if len(L) != len(R):
            res.append(L[0])
        for i in range(len(res)):
            nums[i] = res[i]
        