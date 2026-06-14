class Spreadsheet:

    def __init__(self, rows: int):
        self.vals = defaultdict(int) # maps coords to value

    def setCell(self, cell: str, value: int) -> None:
        self.vals[cell] = value
        

    def resetCell(self, cell: str) -> None:
        self.vals[cell] = 0
        

    def getValue(self, formula: str) -> int:
        terms = formula[1:]
        terms = terms.split('+')
        print(terms)
        tot = 0
        for term in terms:
            if term.isdigit():
                tot += int(term)
                continue
            else:
                tot += self.vals[term]
        return tot
        


# Your Spreadsheet object will be instantiated and called as such:
# obj = Spreadsheet(rows)
# obj.setCell(cell,value)
# obj.resetCell(cell)
# param_3 = obj.getValue(formula)