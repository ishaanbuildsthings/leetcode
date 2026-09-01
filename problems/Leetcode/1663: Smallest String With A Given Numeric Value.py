# https://leetcode.com/problems/smallest-string-with-a-given-numeric-value/description/
# difficulty: medium
# tags: greedy

# Solution, O(n) time O(n) space, can do O(1) space with low level string building

class Solution:
    def getSmallestString(self, n: int, k: int) -> str:
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        alphaToNum = {
            ABC[i] : i + 1 for i in range(len(ABC))
        }
        numToAlpha = {
            i + 1 : ABC[i] for i in range(len(ABC))
        }
        resArr = []
        currScore = 0

        def smallestDoableChar(charsLeft, scoreLeft):
            zEnds = 26 * (charsLeft - 1)
            firstCharScoreNeeded = max(scoreLeft - zEnds, 1)
            return numToAlpha[firstCharScoreNeeded]

        for i in range(n):
            nextChar = smallestDoableChar(n - i, k - currScore)
            currScore += alphaToNum[nextChar]
            resArr.append(nextChar)

        return ''.join(resArr)