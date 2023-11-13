# https://leetcode.com/problems/minimum-difficulty-of-a-job-schedule/description/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# You want to schedule a list of jobs in d days. Jobs are dependent (i.e To work on the ith job, you have to finish all the jobs j where 0 <= j < i).

# You have to finish at least one task every day. The difficulty of a job schedule is the sum of difficulties of each day of the d days. The difficulty of a day is the maximum difficulty of a job done on that day.

# You are given an integer array jobDifficulty and an integer d. The difficulty of the ith job is jobDifficulty[i].

# Return the minimum difficulty of a job schedule. If you cannot find a schedule for the jobs return -1.

# Solution
# Standard DP. Solution 1: states are the index, prev jobs finished, and prev max of whatever current job we are in. This is n^2 * d complexity. I pruned when finished jobs was >d, but it isn't needed. We can even prune when we won't have enough jobs left compared to the amount we need to complete.
# Solution 2: We have n*d states but do an n scan each time. Same time complexity, better space.

# 1
class Solution:
    def minDifficulty(self, jobDifficulty: List[int], d: int) -> int:
        @cache
        def dp(i, prevFinishedJobs, prevMax):
            if prevFinishedJobs > d:
                return float('inf') # pruning
            # print(f'dp called on i={i}, prevFinishedJobs={prevFinishedJobs}, prevMax={prevMax}')
            # base case
            if i == len(jobDifficulty):
                # print(f"base case, ret: {0 if prevFinishedJobs == d else float('inf')}")
                if prevFinishedJobs == d and prevMax == -1: # we have to do the -1 to prevent unfinished jobs existing at the end
                    return 0
                return float('inf') # if we didn't do the right amount of jobs we will say this is impossible

            newJob = jobDifficulty[i]

            # if we add on this job to our current pool
            newMax = max(prevMax, newJob)
            ifAddToPool = dp(i + 1, prevFinishedJobs, newMax)

            # if we make a split here, meaning we use our current element in the left region, then end it
            ifSplitHere = newMax + dp(i + 1, prevFinishedJobs + 1, -1)

            # print(f'res for i={i}, prevFinishedJobs={prevFinishedJobs}, prevMax={prevMax} is: {min(ifAddToPool, ifSplitHere)}')
            return min(ifAddToPool, ifSplitHere)

        res = dp(0, 0, -1)
        return res if res != float('inf') else -1

# 2
#  @cache
# def dp(i, prevJobsFinished):
#     if prevJobsFinished > d:
#         return float('inf')
#     # base case
#     if i == len(jobDifficulty):
#         return 0 if prevJobsFinished == d else float('inf')

#     resForThis = float('inf')
#     runningMax = 0
#     # consider all splits where we keep j and to the left
#     for j in range(i, len(jobDifficulty)):
#         runningMax = max(runningMax, jobDifficulty[j])
#         ifSplitHere = runningMax + dp(j + 1, prevJobsFinished + 1)
#         resForThis = min(resForThis, ifSplitHere)

#     return resForThis

# res = dp(0, 0)
# return res if res != float('inf') else -1