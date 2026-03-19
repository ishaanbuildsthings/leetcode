class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        ransomhash = collections.defaultdict(int)
        maghash = collections.defaultdict(int)

        for char in ransomNote:
            ransomhash[char] += 1
        
        for char in magazine:
            maghash[char] += 1
            
        return ransomhash.items() <= maghash.items()