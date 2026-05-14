# https://leetcode.com/problems/reconstruct-itinerary/?envType=daily-question&envId=2023-09-14
# Difficulty: Hard
# Tags: Backtracking, dfs

# Problem
# You are given a list of airline tickets where tickets[i] = [fromi, toi] represent the departure and the arrival airports of one flight. Reconstruct the itinerary in order and return it.

# All of the tickets belong to a man who departs from "JFK", thus, the itinerary must begin with "JFK". If there are multiple valid itineraries, you should return the itinerary that has the smallest lexical order when read as a single string.

# For example, the itinerary ["JFK", "LGA"] has a smaller lexical order than ["JFK", "LGB"].
# You may assume all tickets form at least one valid itinerary. You must use all the tickets once and only once.

# Solution
# First, sort tickets, so when we consider a departure city, the arrivals we consider are in order. Then restructure tickets to map a departure city to a dictionary that maps arrival cities to the number of times we can visit that arrival city.
# Now, dfs. We consider the earliest arrival city for the city we are currently at. We trackw hich tickets we have used with a dictionary counter and skip flights if we've used all of that flight type. We also accumulate the path and depth to be able to return the right value and to know when our base case is hit (though we could derive the depth from the total # of tickets used).

class Solution:
    def findItinerary(self, tickets: List[List[str]]) -> List[str]:
        # sort the tickets so arrivals are sorted
        tickets.sort()

        flights = defaultdict(lambda: defaultdict(int)) # maps a departure to a dictionary which maps a city to # times can go to that city
        for ticket in tickets:
            dictionaryFromCity = flights[ticket[0]]
            arrivalCity = ticket[1]
            dictionaryFromCity[arrivalCity] += 1

        seenCount = defaultdict(int) # maps a ticket to the amount of times we have used that ticket, tickets are `from,to`

        def dfs(fromCity, depth, accPath):
            # base case, we have used all tickets
            if depth == len(tickets):
                return accPath

            for arrivalCity in flights[fromCity]:
                travelStr = f'{fromCity},{arrivalCity}'
                # if the amount of tickets we had for a certain path is the amount of times we have flown that path, we cannot fly it
                if flights[fromCity][arrivalCity] == seenCount[travelStr]:
                    continue

                # try a valid ticket
                # add our visit
                seenCount[travelStr] += 1
                accPath.append(arrivalCity)
                ifTravelHere = dfs(arrivalCity, depth + 1, accPath)
                if ifTravelHere:
                    return ifTravelHere
                # pop our visit
                seenCount[travelStr] -= 1
                accPath.pop()
            return False
            # start from JFK, with 0 tickets used, our path starts with JFK
        return dfs('JFK', 0, ['JFK'])



