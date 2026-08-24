class Solution:
    def numMovesStones(self, a: int, b: int, c: int) -> List[int]:
        a, b, c = sorted([a, b, c])

        # 'a' always at 0
        # returns min, max
        @cache
        def dp(b, c):
            b, c = min(b, c), max(b, c)
            if b == 1 and c == 2:
                return 0, 0
            
            
            resMin = inf
            resMax = -inf

            # move the first stone, made helper function to simplify code
            def handle(positionsTwoAndThree):
                nonlocal resMin
                nonlocal resMax

                for newFirstPos in range(1, positionsTwoAndThree[1]):
                    if newFirstPos == positionsTwoAndThree[0]:
                        continue
                    newPositions = sorted([*positionsTwoAndThree, newFirstPos])
                    normalized = [newPositions[i] - newPositions[0] for i in range(3)]
                    resMin = min(resMin, 1 + dp(normalized[1], normalized[2])[0])
                    resMax = max(resMax, 1 + dp(normalized[1], normalized[2])[1])
            
            handle([b, c])
            handle([c - b, c])
            return resMin, resMax
        
        return dp(b - a, c - a)[0], dp(b - a, c - a)[1]