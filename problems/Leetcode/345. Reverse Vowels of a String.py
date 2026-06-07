class Solution:
    def reverseVowels(self, s: str) -> str:
        arr = list(s)
        l = 0
        r = len(arr) - 1
        while l < r:
            if arr[l] not in 'aeiouAEIOU':
                l += 1
                continue
            if arr[r] not in 'aeiouAEIOU':
                r -= 1
                continue
            arr[l], arr[r] = arr[r], arr[l]
            l += 1
            r -= 1
        
        return ''.join(arr)