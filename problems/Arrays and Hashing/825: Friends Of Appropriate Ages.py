# https://leetcode.com/problems/friends-of-appropriate-ages/
# difficulty: medium
# tags: range query

# Problem
# There are n persons on a social media website. You are given an integer array ages where ages[i] is the age of the ith person.

# A Person x will not send a friend request to a person y (x != y) if any of the following conditions is true:

# age[y] <= 0.5 * age[x] + 7
# age[y] > age[x]
# age[y] > 100 && age[x] < 100
# Otherwise, x will send a friend request to y.

# Note that if x sends a request to y, y will not necessarily send a request to x. Also, a person will not send a friend request to themself.

# Return the total number of friend requests made.

# Solution, I don't remember this problem that much, would need to re-read code

class Solution:
    def numFriendRequests(self, ages: List[int]) -> int:
        # tells us the lower bound, lower bound means we cannot send a request to that age
        def getLowerBound(age):
            lowerBound = 0.5 * age + 7
            return math.floor(lowerBound)
        counts = collections.Counter(ages)

        runningSum = 0
        prefixSums = [] # store sums of inclusive elements
        prefixSums.append(0)
        for i in range(1, 121):
            if i in counts:
                runningSum += counts[i]
            prefixSums.append(runningSum)
        def sumQuery(l, r):
            return prefixSums[r] - prefixSums[l-1]

        res = 0
        for age in ages:
            upperBound = age + 1 # can't send to this
            lowerBound = getLowerBound(age)
            if lowerBound < upperBound - 1:
                res += sumQuery(lowerBound + 1, upperBound - 1)
            if age > lowerBound and age < upperBound:
                res -= 1
        return res

# 1 3 20 77 80 98 101 109 114




        # never send requests to older people

        # age[y] > 0.5 * x + 7 # when we can send requests

        # y - 7 > 0.5x
        # 2(y - 7) > x is when we can send a request


        # # never send requests to people

        # res = 0

        # 10->12
        # 20->17
        # 100->57