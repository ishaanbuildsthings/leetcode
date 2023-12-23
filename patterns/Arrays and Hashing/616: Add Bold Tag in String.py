# https://leetcode.com/problems/add-bold-tag-in-string/
# difficulty: medium
# tags: sweep line

# Problem
# You are given a string s and an array of strings words.

# You should add a closed pair of bold tag <b> and </b> to wrap the substrings in s that exist in words.

# If two such substrings overlap, you should wrap them together with only one pair of closed bold-tag.
# If two substrings wrapped by bold tags are consecutive, you should combine them.
# Return s after adding the bold tags.

# Solution, I reused code from another solution so this will be slow since it is different constraints. See that solution.

# JUST COPY PASTED CODE FROM https://leetcode.com/problems/bold-words-in-string/description/, NOT DESIGNED TO BE EFFICIENT

class Solution:
    def addBoldTag(self, s: str, words: List[str]) -> str:
        wordSet = set(words)
        furthestRightCovered = -1
        ranges = []
        sweep = [0 for _ in range(len(s))]
        sweep.append(0)

        for startLetter in range(len(s)):
            maxRightEdge = min(len(s) - 1, startLetter + 999)
            maxLeftEdge = max(startLetter, furthestRightCovered + 1)
            for rightEdge in range(maxRightEdge, maxLeftEdge - 1, -1):
                word = s[startLetter:rightEdge + 1]
                if word in wordSet:
                    sweep[startLetter] += 1
                    sweep[rightEdge + 1] -= 1
                    furthestRightCovered = rightEdge
                    ranges.append([startLetter, rightEdge])
                    break
        closeLast = sweep[-1] < 0
        sweep.pop()

        running = 0
        for i in range(len(sweep)):
            diff = sweep[i]
            running += diff
            sweep[i] = running

        resArr = []

        for i in range(len(sweep)):
            # if we are a number and the prior was a 0 or didn't exist, we just bolded
            if sweep[i] > 0:
                if i == 0:
                    resArr.append('<b>')
                else:
                    if sweep[i-1] == 0:
                        resArr.append('<b>')
            # if we are a 0, and the prior was a non zero, we just unbolded
            else:
                if i > 0 and sweep[i - 1] != 0:
                    resArr.append('</b>')
            resArr.append(s[i])

        if closeLast:
            resArr.append('</b>')

        return ''.join(resArr)







