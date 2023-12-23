# https://leetcode.com/problems/bold-words-in-string/description/
# difficulty: medium
# tags: sweep line

# Problem
# Given an array of keywords words and a string s, make all appearances of all keywords words[i] in s bold. Any letters between <b> and </b> tags become bold.

# Return s after adding the bold tags. The returned string should use the least number of tags possible, and the tags should form a valid combination.

# Solution, I was keen on making a sweep line work, there's other solutions like iterating over each word instead.

class Solution:
    def boldWords(self, words: List[str], s: str) -> str:
        wordSet = set(words)
        furthestRightCovered = -1
        ranges = []
        sweep = [0 for _ in range(len(s))]
        sweep.append(0)

        for startLetter in range(len(s)):
            maxRightEdge = min(len(s) - 1, startLetter + 9)
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