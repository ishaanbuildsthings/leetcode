class Solution:
    # can sort also
    def countElements(self, arr: List[int]) -> int:
        c = Counter(arr)
        return sum(
            c[i] if c[i + 1] else 0 for i in c
        )
        