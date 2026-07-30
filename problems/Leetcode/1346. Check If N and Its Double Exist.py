class Solution:
    def checkIfExist(self, arr: List[int]) -> bool:
        # can be done in O(1) space with sorting, or maybe really jank O(1) space where we use extra space on the integers, i think there might be a way where we determine how many numbers there are and thus how much storage we have, not sure though
        seen = set()
        for num in arr:
            if num / 2 in seen or num * 2 in seen:
                return True
            seen.add(num)
        return False