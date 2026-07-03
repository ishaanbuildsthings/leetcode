class Solution:
    def invalidTransactions(self, transactions: List[str]) -> List[str]:
        resIdx = set()

        for i in range(len(transactions)):
            name1, time1, amt1, city1 = transactions[i].split(',')
            time1=int(time1)
            amt1=int(amt1)
            if amt1 >= 1000:
                resIdx.add(i)
            for j in range(len(transactions)):
                if i == j: continue
                name2, time2, amt2, city2 = transactions[j].split(',')
                time2=int(time2)
                amt2=int(amt2)
                if name1 == name2 and city1 != city2 and abs(time1 - time2) <= 60:
                    resIdx.add(j)
        
        return [transactions[i] for i in resIdx]




