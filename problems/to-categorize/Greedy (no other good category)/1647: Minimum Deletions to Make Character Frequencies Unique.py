# https://leetcode.com/problems/minimum-deletions-to-make-character-frequencies-unique/?envType=daily-question&envId=2023-09-12
# Difficulty: Medium
# Tags: Greedy (no other good category)

# Problem
# A string s is called good if there are no two different characters in s that have the same frequency.

# Given a string s, return the minimum number of characters you need to delete to make s good.

# The frequency of a character in a string is the number of times it appears in the string. For example, in the string "aab", the frequency of 'a' is 2, while the frequency of 'b' is 1.

# Solution, O(n) time O(1) space
# Count the number of each char which is n time and 1 space. Repeatedly remove from the counts the most frequent character, if it is alone in its frequency. Now, once we have matches, take that match, search for a gap of frequency we can set it to, and repeat.

class Solution:
    def minDeletions(self, s: str) -> int:
        counts = Counter(s)

        # repeatedly deletes the most frequent char, if it is unique
        def deleteTopUniqueFreqs():
            while True:
                sortedCounts = counts.most_common()
                # if the length is 1, we are guaranteed done
                if len(sortedCounts) == 1:
                    return
                # if we don't have a match, delete the top
                if sortedCounts[0][1] != sortedCounts[1][1]:
                    key = sortedCounts[0][0]
                    del counts[key]
                else:
                    break

        result = 0
        while True:
            # if all of the counts are unique we are done
            if len(set(counts.values())) == len(counts.values()):
                return result
            # delete any unique top characters over and over
            deleteTopUniqueFreqs()

            # now we have a match with at least the top two frequencies, we have to delete chars from that until it is a unique count
            sortedValues = sorted(counts.values(), reverse=True)
            holeFound = False
            maxKey = max(counts, key = counts.get)
            # iterate over until we find a hole/gap
            for i in range(1, len(sortedValues)):
                if sortedValues[i] < sortedValues[i-1] - 1:
                    holeCount = sortedValues[i-1] - 1
                    deletions = sortedValues[0] - holeCount
                    holeFound = True
                    result += deletions
                    counts[maxKey] = holeCount
                    break
            if not holeFound:
                newHoleSize = sortedValues[-1] - 1
                deletions = sortedValues[0] - newHoleSize
                result += deletions
                if newHoleSize == 0:
                    del counts[maxKey]
                else:
                    counts[maxKey] = sortedValues[-1] - 1