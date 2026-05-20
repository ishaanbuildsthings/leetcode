# SOLUTION 1, stack
class Solution:
    def getCollisionTimes(self, cars: List[List[int]]) -> List[float]:
        stack = []
        # loop from the last car first
        # we hold a stack of cars that are driving
        # we want to know cars that we might HIT in the future, example speeds:
        # [10, 5, 2]
        # if there is a very fast car like this then we don't care about it since we cannot catch it
        # so it should not be in the stack:
        # [10, 5, 2, 100 <- fast]
        # if we add a new slow car to the front:
        # [1 <- added, 10, 5, 2]
        # then we never can reach the 10 (at least not until the 10 collides with something) so we pop it
        # [1 do we reach this? -> 5, 2]
        # keep popping while we never reach a car

        # but we might have a case where our fast car will catch up to the one in front of it
        # but not until the car in front hit ITS car in front
        # [30 <- this reaches the 20 but only after the 20 already hit the 15   20, 15]

        n = len(cars)
        res = [-1.0] * n
        stack = [] # holds indices
        for i in range(n - 1, -1, -1):
            pos, speed = cars[i]
            while stack:
                nxtPos, nxtSpeed = cars[stack[-1]]
                # condition 1: we cannot catch this car
                if nxtSpeed >= speed:
                    stack.pop()
                    continue
                
                # we could catch this car but only after it hits another car
                dist = abs(pos - nxtPos)
                gain = abs(speed - nxtSpeed)
                timeToCatch = dist / gain
                nextCarAnswer = res[stack[-1]]
                if nextCarAnswer != -1 and timeToCatch > nextCarAnswer:
                    stack.pop()
                    continue
                
                # we truly catch this next car before it hits another car
                res[i] = timeToCatch
                break
            stack.append(i)
        
        return res

