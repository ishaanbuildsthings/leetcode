class Solution:
    def getHint(self, secret: str, guess: str) -> str:
        bulls = defaultdict(int) # maps a number to the amount of times that bull occurs
        c1 = Counter() # secret
        c2 = Counter() # guess
        for i, c in enumerate(secret):
            bulls[c] += c == guess[i]
            c1[c] += 1
            c2[guess[i]] += 1
        
        totalBulls = sum(bulls.values())
        totalCows = 0
        for digit in range(10):
            strDigit = str(digit)
            cowsForDigit = min(c1[strDigit], c2[strDigit]) - bulls[strDigit] 
            totalCows += cowsForDigit
        
        return f'{totalBulls}A{totalCows}B'

