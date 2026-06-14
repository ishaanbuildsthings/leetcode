class Solution:
    def phonePrefix(self, numbers: List[str]) -> bool:
        # can put everything in a trie
        for i in range(len(numbers)):
            for j in range(len(numbers)):
                if i == j:
                    continue
                len1 = len(numbers[i])
                len2 = len(numbers[j])
                if numbers[j][:len1] == numbers[i]:
                    return False
        return True