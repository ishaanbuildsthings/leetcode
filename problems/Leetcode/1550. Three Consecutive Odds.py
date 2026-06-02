class Solution:
    def threeConsecutiveOdds(self, arr: List[int]) -> bool:
        # isnt this bad just iterate and keep a count lol
        
        for i in range(len(arr) - 2):
            if arr[i]*arr[i+1]*arr[i+2] % 2 == 1: # don't want to type each mod
                return True
        return False