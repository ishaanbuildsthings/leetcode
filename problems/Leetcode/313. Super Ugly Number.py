class Solution:
    def nthSuperUglyNumber(self, n: int, primes: List[int]) -> int:
        heap = primes[::]
        heapq.heapify(heap)
        seen = set()
        for x in primes:
            seen.add(x)
        small = 1
        for i in range(n - 1):
            small = heapq.heappop(heap)
            for mult in primes:
                if small * mult not in seen:
                    seen.add(small * mult)
                    heapq.heappush(heap, small * mult)
        return small
g