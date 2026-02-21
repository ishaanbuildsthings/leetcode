class Solution:
    def canSeePersonsCount(self, heights: List[int]) -> List[int]:
        n = len(heights)
        
        nextGreater = [n] * n

        # strictly decreasing
        stack = []
        for i in range(n):
            while stack and heights[i] > heights[stack[-1]]:
                popped = stack.pop()
                nextGreater[popped] = i
            stack.append(i)

        LOG = math.ceil(math.log2(n))
        
        @cache
        def powNext(power, i):
            if i == n:
                return n
            if power == 0:
                return nextGreater[i]
            half = powNext(power - 1, i)
            full = powNext(power - 1, half)
            return full
        
        def find(i):
            curr = i + 1
            if i == n - 1:
                return 0
            if heights[i + 1] > heights[i]:
                return 1
            res = 1
            # repeatedly take biggest power of 2 such that we are still smaller
            for power in range(LOG, -1, -1):
                nxt = powNext(power, curr)
                if nxt < n and heights[nxt] < heights[i]:
                    res += 2**power
                    curr = nxt
            
            if nextGreater[curr] != n:
                return res + 1
            return res
        powNext.cache_clear()
        return [find(i) for i in range(n)]



        

            
            




