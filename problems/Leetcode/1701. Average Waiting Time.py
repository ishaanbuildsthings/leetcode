class Solution:
    def averageWaitingTime(self, customers: List[List[int]]) -> float:
        totalWait = 0
        currentTime = 0
        for customer in customers:
            arrival, duration = customer
            # # if the chef isn't waiting for anything, teleport to when the customer comes
            if arrival > currentTime:
              currentTime = arrival
            # if the customer already arrived, they were waiting
            elif arrival <= currentTime:
                totalWait += (currentTime - arrival)
            currentTime += duration
            totalWait += duration
        return totalWait / len(customers)
                
