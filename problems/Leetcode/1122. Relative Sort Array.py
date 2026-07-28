class Solution:
    def relativeSortArray(self, arr1: List[int], arr2: List[int]) -> List[int]:
        # can also use a custom comparator for the whole thing
        
        c = Counter(arr1)
        res = []
        for i in range(len(arr2)):
            res.extend(
                [arr2[i]] * c[arr2[i]]
            )
        c2 = Counter(arr2)
        # can use bucket
        for key in sorted(c.keys()):
            if not c2[key]:
                res.extend(
                    [key] * c[key]
                )
            
        return res