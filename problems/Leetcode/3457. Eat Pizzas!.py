class Solution:
    def maxWeight(self, pizzas: List[int]) -> int:
        pizzas.sort()
        d = deque(pizzas)
        
        days = len(pizzas) // 4
        
        oddDays = ceil(days / 2)
        evenDays = days - oddDays
        res = 0
        
        for i in range(oddDays):
            res += d.pop()
            d.popleft()
            d.popleft()
            d.popleft()
        for i in range(evenDays):
            d.pop()
            res += d.pop()
            d.popleft()
            d.popleft()
        
        return res
