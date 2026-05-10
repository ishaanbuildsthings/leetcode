# template by: https://github.com/agrawalishaan/leetcode
# O(n) time / space
class PrimeSieve:
    def __init__(self, n):
        self.sieve = [True for _ in range(n)]
        self.sieve[0] = False
        self.sieve[1] = False
        for i in range(2, n):
            if self.sieve[i]: # linear optimization
                for j in range(i * i, n, i):
                    self.sieve[j] = False
        self.primeList = [i for i in range(n) if self.sieve[i]]

    def isPrime(self, n):
        return self.sieve[n]

    def getPrimeList(self):
        return self.primeList


def make(oldString, i, newDigitStr):
    prefix = oldString[:i]
    post = oldString[i+1:]
    return prefix + newDigitStr + post

sieve = PrimeSieve(2* 10**4)

class Solution:
    def minOperations(self, n: int, m: int) -> int:
        if sieve.isPrime(n):
            return -1
        if sieve.isPrime(m):
            return -1
        
        heap = []
        heap.append((n, n)) # holds (cost, number)
        
        # minDists = defaultdict(lambda: inf) # maps number not string
        seen = set()
        # seen.add(n)
        
        while heap:
            cost, num = heapq.heappop(heap)
            strNum = str(num)
            if num == m:
                return cost
            
            if num in seen:
                continue
            seen.add(num)
                
            # if cost >= minDists[num]:
            #     continue
            # minDists[num] = cost
            
            for index in range(len(strNum)):
                d = int(strNum[index])
                # decrease
                if d > 0:
                    downString = make(strNum, index, str(d - 1))
                    downInt = int(downString)
                    if not sieve.isPrime(downInt) and not downInt in seen:
                        heapq.heappush(heap, (cost + downInt, downInt))
                # increase
                if d < 9:
                    upString = make(strNum, index, str(d + 1))
                    upInt = int(upString)
                    if not sieve.isPrime(upInt) and not upInt in seen:
                        heapq.heappush(heap, (cost + upInt, upInt))
        
        return -1
                    
                    
                
            
        
            