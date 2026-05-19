def isPrime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

class Solution:
    def sumOfLargestPrimes(self, s: str) -> int:
        primes = []
        seen = set()
        for l in range(len(s)):
            for r in range(l, len(s)):
                string = s[l:r+1]
                # print(string)
                number = int(string)
                if number in seen:
                    continue
                seen.add(number)
                if isPrime(number):
                    primes.append(number)
        primes = list(set(primes))
        primes.sort(reverse=True)
        return sum(primes[0:3])
    
                