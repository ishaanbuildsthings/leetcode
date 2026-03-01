class Excel:

    # single cell like A1 or range A1:B2 to a list
    def toRange(self, string):
        arr = string.split(':')
        left = arr[0]
        right = arr[-1]
        c1 = left[0]
        c2 = right[0]
        r1 = int(left[1:])
        r2 = int(right[1:])
        vals = []
        for r in range(r1, r2 + 1):
            for c in range(ord(c1), ord(c2) + 1):
                letter = chr(c)
                vals.append((r, letter))
        return vals 


    def __init__(self, height: int, width: str):
        self.vals = defaultdict(int) # (r, c) -> value or formula

    def set(self, row: int, column: str, val: int) -> None:
        self.vals[(row, column)] = val

    def get(self, row: int, column: str, memo=None) -> int:
        if memo is None:
            memo = {}
        if (row, column) in memo:
            return memo[(row, column)]

        val = self.vals[(row, column)]
        if isinstance(val, int):
            return val
        # val is a list like ["A1", "A1:B2"]
        total = 0
        for s in val:
            for cell in self.toRange(s):
                total += self.get(*cell, memo=memo)
        memo[(row, column)] = total
        return total

    def sum(self, row: int, column: str, numbers: List[str]) -> int:
        self.vals[(row, column)] = numbers
        return self.get(row, column)


# Your Excel object will be instantiated and called as such:
# obj = Excel(height, width)
# obj.set(row,column,val)
# param_2 = obj.get(row,column)
# param_3 = obj.sum(row,column,numbers)