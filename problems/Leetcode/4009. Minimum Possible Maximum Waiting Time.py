class Solution:
    def minMaxWaitingTime(self, demand: List[int], fuel: List[int]) -> int:
        # i is the next car ready to fuel

        # returns the max # of cars served, and then min waiting time
        # fuel1 and fuel2 are amounts left after the current cars at them are done
        # s1 and s2 are seconds left until the refueling finishes
        @cache
        def dp(fuel1, fuel2, i, s1, s2):
            if i == len(demand):
                return 0, 0 # no cars served, min wait is 0
            req = demand[i]
            # cannot serve this car due to no fuel
            if req > max(fuel1, fuel2):
                return 0, 0
            
            resMaxCars = -inf
            resMinWait = inf

            # wait for first pump and take that
            if req <= fuel1:
                waitTime = s1
                hereMaxCars, hereMinWait = dp(fuel1 - req, fuel2, i + 1, req, max(0, s2 - waitTime))
                hereMaxCars += 1
                worstWait = max(waitTime, hereMinWait)
                resMaxCars = hereMaxCars
                resMinWait = worstWait
            
            # wait for second pump and take that
            if req <= fuel2:
                waitTime = s2
                hereMaxCars, hereMinWait = dp(fuel1, fuel2 - req, i + 1, max(0, s1 - waitTime), req)
                worstWait = max(waitTime, hereMinWait)
                hereMaxCars += 1
                if hereMaxCars > resMaxCars:
                    resMaxCars = hereMaxCars
                    resMinWait = worstWait
                elif hereMaxCars == resMaxCars:
                    resMinWait = min(resMinWait, worstWait)


            return resMaxCars, resMinWait
        
        mxCars, mnWait = dp(fuel[0], fuel[1], 0, 0, 0)
        if mxCars == 0:
            return -1
        return mnWait