class Solution:
    def numDifferentIntegers(self, word: str) -> int:
        block = []
        blocks = []
        for i, v in enumerate(word):
            if v.isalpha():
                if block:
                    blocks.append(int(''.join(block)))
                    block = []
                continue
            block.append(v)
        if block:
            blocks.append(int(''.join(block)))
        return len(set(blocks))