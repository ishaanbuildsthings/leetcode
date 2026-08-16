# https://leetcode.com/problems/online-election/description/
# difficulty: medium
# tags: binary search

# Problem
# You are given two integer arrays persons and times. In an election, the ith vote was cast for persons[i] at time times[i].

# For each query at a time t, find the person that was leading the election at time t. Votes cast at time t will count towards our query. In the case of a tie, the most recent vote (among tied candidates) wins.

# Implement the TopVotedCandidate class:

# TopVotedCandidate(int[] persons, int[] times) Initializes the object with the persons and times arrays.
# int q(int t) Returns the number of the person that was leading the election at time t according to the mentioned rules.

# Solution, O(n) time and space for init, O(log n) time for q, standard binary search, we could binary search on timeToWinningArr instead of remapping self.times


class TopVotedCandidate:

    # assume a query is never called when no one is winning?

    def __init__(self, persons: List[int], times: List[int]):
        # want a mapping of time to who was winning, for each time
        timeToWinning = {}
        votes = defaultdict(int)
        maxVotes = 0
        winning = None
        for i in range(len(persons)):
            votes[persons[i]] += 1
            if votes[persons[i]] >= maxVotes:
                maxVotes = votes[persons[i]]
                winning = persons[i]
            timeToWinning[times[i]] = winning
        self.timeToWinningArr = [[time, timeToWinning[time]] for time in timeToWinning]
        self.times = [time for time, _ in self.timeToWinningArr]

    def q(self, t: int) -> int:
        i = bisect.bisect_right(self.times, t)
        i -= 1
        return self.timeToWinningArr[i][1]



# Your TopVotedCandidate object will be instantiated and called as such:
# obj = TopVotedCandidate(persons, times)
# param_1 = obj.q(t)