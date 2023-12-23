# https://leetcode.com/problems/longest-substring-of-one-repeating-character/description/
# difficulty: hard
# tags: avl tree, binary search, segment tree

# Problem
# You are given a 0-indexed string s. You are also given a 0-indexed string queryCharacters of length k and a 0-indexed array of integer indices queryIndices of length k, both of which are used to describe k queries.

# The ith query updates the character in s at index queryIndices[i] to the character queryCharacters[i].

# Return an array lengths of length k where lengths[i] is the length of the longest substring of s consisting of only one repeating character after the ith query is performed.

# Solution, O(n log n) time, O(n) space. I used an AVL on disjoint intervals that partition the space. When I change a character I locate that interval and split and merge (at most 2 merges) as needed. We can also do a pretty elaborate segment tree solution, or even 26 simple segment trees (this will probably TLE).

import sortedcontainers

class Solution:
    def longestRepeating(self, s: str, queryCharacters: str, queryIndices: List[int]) -> List[int]:
        intervals = sortedcontainers.SortedList()
        sizes = sortedcontainers.SortedList()

        l = 0
        for r in range(len(s)):
            if s[r] != s[l]:
                intervals.add([l, r - 1, s[r - 1]])
                sizes.add((r - 1) - l + 1)
                l = r
            if r == len(s) - 1:
                intervals.add([l, r, s[r]])
                sizes.add(r - l + 1)

        def findInterval(queryIndex):
            l = 0
            r = len(intervals) - 1
            while l < r:
                m = (r + l) // 2
                midInterval = intervals[m]
                left, right, _ = midInterval
                if left <= queryIndex <= right:
                    return m
                elif queryIndex < left:
                    r = m
                else:
                    l = m + 1
            return l

        res = []
        for i, queryIndex in enumerate(queryIndices):
            containingIntervalIndex = findInterval(queryIndex)
            newIntervals = []
            newSizes = []
            l, r, oldLetter = intervals[containingIntervalIndex]
            oldSize = r - l + 1

            # add new left interval
            if queryIndex > l:
                newLeft = [l, queryIndex - 1, oldLetter]
                newIntervals.append(newLeft)
                newSizes.append((queryIndex - 1) - l + 1)
            # add new right
            if queryIndex < r:
                newRight = [queryIndex + 1, r, oldLetter]
                newIntervals.append(newRight)
                newSizes.append(r - (queryIndex + 1) + 1)

            # remove old interval and size
            intervals.remove([l, r, oldLetter])
            sizes.remove(oldSize)

            # add new
            for newInterval in newIntervals:
                intervals.add(newInterval)
            for newSize in newSizes:
                sizes.add(newSize)

            # add new middle interval
            newMiddle = [queryIndex, queryIndex, queryCharacters[i]]
            intervals.add(newMiddle)
            sizes.add(1)

            # find the middle interval
            middleIntervalIndex = containingIntervalIndex + (1 if queryIndex > l else 0)

            finalMiddle = [queryIndex, queryIndex, queryCharacters[i]]
            removeLeft = False
            removeRight = False
            finalSize = 1
            # merge with left if applicable
            if middleIntervalIndex > 0:
                leftInterval = intervals[middleIntervalIndex - 1]
                leftL, leftR, leftChar = leftInterval
                if leftChar == queryCharacters[i]:
                    finalMiddle[0] = leftL
                    removeLeft = True
                    finalSize += (leftR - leftL + 1)
            if middleIntervalIndex < len(intervals) - 1:
                rightInterval = intervals[middleIntervalIndex + 1]
                rightL, rightR, rightChar = rightInterval
                if rightChar == queryCharacters[i]:
                    finalMiddle[1] = rightR
                    removeRight = True
                    finalSize += (rightR - rightL + 1)


            # remove the middle interval and the old size
            intervals.remove([queryIndex, queryIndex, queryCharacters[i]])
            sizes.remove(1)

            # remove the left and right intervals
            if removeLeft:
                intervals.remove(leftInterval)
                sizes.remove(leftR - leftL + 1)
            if removeRight:
                intervals.remove(rightInterval)
                sizes.remove(rightR - rightL + 1)

            # add the final new one
            intervals.add(finalMiddle)
            sizes.add(finalSize)

            res.append(sizes[-1])

        return res


            # we have some interval from [l:r] and we need to remove a point from it
            # if the point is in the middle, we split the interval into 2, and add a middle interval
            # if the point is on the edge, we change the edge
            # if the point is the whole thing, we change the entire interval

