class Solution:
    def decode(self, encoded: List[int], first: int) -> List[int]:
        res = [first]
        for i in range(len(encoded)):
            newNum = encoded[i] ^ res[i]
            res.append(newNum)
        return res