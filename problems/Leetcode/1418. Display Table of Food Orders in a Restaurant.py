class Solution:
    def displayTable(self, orders: List[List[str]]) -> List[List[str]]:
        tables = set()
        foods = set()
        tableToFoodToCounts = defaultdict(lambda: defaultdict(int))
        for name, table, food in orders:
            tables.add(table)
            foods.add(food)
            tableToFoodToCounts[table][food] += 1
        tables = sorted(tables,key=lambda x: int(x))
        foods = sorted(foods)
        
        out = [['' for _ in range(len(foods) + 1)] for _ in range(len(tables))]
        out.insert(0, ['Table'] + foods)
        for i in range(len(tables)):
            out[i+1][0] = tables[i]
        
        for r in range(1, len(out)):
            table = out[r][0]
            for c in range(1, len(out[0])):
                food = out[0][c]
                out[r][c] = str(tableToFoodToCounts[table][food])
                
        return out
        

