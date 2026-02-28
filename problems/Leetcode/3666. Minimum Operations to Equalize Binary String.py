class Solution:
    def minOperations(self, s: str, k: int) -> int:
        # version 1, hall's theorem
        # n = len(s)
        # ones = sum(int(x) for x in s)
        # zeroes = n - ones

        # # 1 zero -> we have odd parity to flip that many
        # parityToFlipAll0s = zeroes % 2

        # for ops in range(10**5 + 1):
        #     totalFlips = ops * k
        #     # we need to flip all the 0s an odd number of times
        #     # we will always spend an even amount of flip parity on the 1s
        #     if totalFlips % 2 != parityToFlipAll0s:
        #         continue
        #     if totalFlips < zeroes:
        #         continue
        #     if ops % 2:
        #         maxPerEven = ops - 1
        #         maxPerOdd = ops
        #     else:
        #         maxPerEven = ops
        #         maxPerOdd = ops - 1
        #     totalMax = ones * maxPerEven + zeroes * maxPerOdd
        #     if totalFlips > totalMax:
        #         continue
        #     return ops
        
        # return -1



        # version 2, bfs
        n = len(s)
        ones = sum(int(x) for x in s)
        zeroes = n - ones
        from sortedcontainers import SortedList
        evenOnesStates = SortedList()
        oddOnesStates = SortedList()
        for amtOnes in range(n + 1):
            if amtOnes % 2:
                oddOnesStates.add(amtOnes)
            else:
                evenOnesStates.add(amtOnes)

        def getSmallestInRange(sortedList, lo, hi):
            idx = sortedList.bisect_left(lo)
            if idx < len(sortedList) and sortedList[idx] <= hi:
                return sortedList[idx]
            return -1

        q = deque()
        q.append(ones)
        steps = 0
        while q:
            length = len(q)
            for _ in range(length):
                poppedOnes = q.popleft()
                if poppedOnes == n:
                    return steps
                
                zeroesHere = n - poppedOnes

                # max amount of 1s we can have is if we flip all 0s, and any leftover is flip a 1
                if k <= zeroesHere:
                    maxOnes = poppedOnes + k
                else:
                    leftover = k - zeroesHere
                    maxOnes = n - leftover
                
                # min 1s is flip all 1s, same logic
                if k <= poppedOnes:
                    minOnes = poppedOnes - k
                else:
                    minOnes = k - poppedOnes
                
                # flipped range
                currentParity = poppedOnes % 2
                if k % 2:
                    nextSet = evenOnesStates if currentParity else oddOnesStates
                else:
                    nextSet = oddOnesStates if currentParity else evenOnesStates
                
                while True:
                    smallest = getSmallestInRange(nextSet, minOnes, maxOnes)
                    if smallest == -1:
                        break
                    nextSet.remove(smallest)
                    q.append(smallest)
            
            steps += 1
            
        return -1
