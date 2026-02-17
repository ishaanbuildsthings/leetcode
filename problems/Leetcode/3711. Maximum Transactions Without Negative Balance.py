class Solution:
    def maxTransactions(self, transactions: List[int]) -> int:
        n = len(transactions)
        balance = 0
        taken = []
        up = 0
        for i, v in enumerate(transactions):
            # take a pos
            if v >= 0:
                balance += v
                up += 1
                continue
            # can take a neg
            if balance + v >= 0:
                heapq.heappush(taken, v)
                balance += v
                continue
            # cannot take this negative but can exchange with a better one
            if taken and taken[0] < v:
                popped = heapq.heappop(taken)
                balance -= popped
                heapq.heappush(taken, v)
                balance += v
        
        return up + len(taken)



# [-6,10,-7,-5,5]

# max balance with x transactions

# max transactions with x balance, -inf