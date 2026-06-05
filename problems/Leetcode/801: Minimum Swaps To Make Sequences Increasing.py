class Solution:
    def minSwap(self, nums1: List[int], nums2: List[int]) -> int:
        nums1 = [-inf] + nums1
        nums2 = [-inf] + nums2
        swapped = 0
        notSwapped = 0
        for i in range(1, len(nums1)):
            newNotSwapped = inf
            newSwapped = inf
            if nums1[i] > nums1[i - 1] and nums2[i] > nums2[i - 1]:
                newNotSwapped = notSwapped
                newSwapped = 1 + swapped
            if nums1[i] > nums2[i - 1] and nums2[i] > nums1[i - 1]:
                newNotSwapped = min(newNotSwapped, swapped)
                newSwapped = min(newSwapped, 1 + notSwapped)
            
            swapped = newSwapped
            notSwapped = newNotSwapped
        
        return min(swapped, notSwapped)
            