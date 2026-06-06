# O(n) space, allocate for each level of the merge

class Solution:
    def sortArray(self, nums: List[int]) -> List[int]:
        def merge(sorted1, sorted2):
            res = []
            i = 0
            j = 0
            while i < len(sorted1) and j < len(sorted2):
                if sorted1[i] <= sorted2[j]:
                    res.append(sorted1[i])
                    i += 1
                else:
                    res.append(sorted2[j])
                    j += 1
            if i < len(sorted1):
                res += sorted1[i:]
            elif j < len(sorted2):
                res += sorted2[j:]
            return res
        
        def mergeSort(arr):
            # base case
            if len(arr) == 1:
                return arr
            
            midPoint = len(arr) // 2

            leftMerged = mergeSort(arr[:midPoint])
            rightMerged = mergeSort(arr[midPoint:])

            res = merge(leftMerged, rightMerged)
            return res
        
        return mergeSort(nums)

# class Solution:
#     def sortArray(self, nums: List[int]) -> List[int]:

#         def mergeInPlace(arr, l, m, r):
#             start2 = m + 1
#             # If the direct merge is already sorted
#             if arr[m] <= arr[start2]:
#                 return

#             # Two pointers to maintain start of both arrays to merge
#             while l <= m and start2 <= r:

#                 # If element 1 is in right place
#                 if arr[l] <= arr[start2]:
#                     l += 1
#                 else:
#                     value = arr[start2]
#                     index = start2

#                     # Shift all the elements between element 1
#                     # element 2, right by 1.
#                     while index != l:
#                         arr[index] = arr[index - 1]
#                         index -= 1

#                     arr[l] = value

#                     # Update all the pointers
#                     l += 1
#                     m += 1
#                     start2 += 1
        
#         def mergeSort(l, r):
#             # print(f'called on l, r: {l} {r}')
#             # base case
#             if l == r:
#                 return

#                 # 0 1 2 3
#                 #     ^

#             midPoint = (r + l) // 2

#             # merge left
#             mergeSort(l, midPoint)
#             # merge right
#             mergeSort(midPoint + 1, r)

#             # combine
#             mergeInPlace(nums, l, midPoint, r)
        
#         mergeSort(0, len(nums) - 1)
#         return nums
            