class Solution:
    def maximumSetSize(self, nums1: List[int], nums2: List[int]) -> int:
        n = len(nums1)
        c1 = Counter(nums1)
        c2 = Counter(nums2)
        unique1 = []
        for k in c1:
            if not c2[k]:
                unique1.append(k)
        unique2 = []
        for k in c2:
            if not c1[k]:
                unique2.append(k)
        shared = set()
        for k in c1:
            if k in c2:
                shared.add(k)
        for k in c2:
            if k in c1:
                shared.add(k)
        ans = min(n // 2, len(unique1)) + min(n // 2, len(unique2))
        ans += len(shared)
        ans = min(ans, n)
        return ans
            
            
            
            
        
        