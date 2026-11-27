class Solution:
    def maxVacationDays(self, flights: List[List[int]], days: List[List[int]]) -> int:
        # maybe some weird segment tree optimization?
        # can precompute dense graph if the flightmap is sparse
        
        k = len(days[0])
        n = len(flights)
        @cache
        def dp(city, week):
            if week == k:
                return 0
            ifStayHereVacationDays = days[city][week]
            ifStayHere = ifStayHereVacationDays + dp(city, week + 1)
            resHere = ifStayHere
            for adjCity in range(n):
                if flights[city][adjCity] == 0:
                    continue
                ifFlyHere = days[adjCity][week] + dp(adjCity, week + 1)
                resHere = max(resHere, ifFlyHere)
            
            return resHere
        
        return dp(0, 0)
                
                