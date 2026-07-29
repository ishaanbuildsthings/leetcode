class Solution:
    def arraysIntersection(self, arr1: List[int], arr2: List[int], arr3: List[int]) -> List[int]:
        res = []
        a = b = c = 0
        while a < len(arr1) and b < len(arr2) and c < len(arr3):
            if arr1[a] == arr2[b] == arr3[c]:
                res.append(arr1[a])
                a += 1
                b += 1
                c += 1
                continue
            small = min(arr1[a], arr2[b], arr3[c])
            if arr1[a] == small:
                a += 1
            if arr2[b] == small:
                b += 1
            if arr3[c] == small:
                c += 1
        
        return res