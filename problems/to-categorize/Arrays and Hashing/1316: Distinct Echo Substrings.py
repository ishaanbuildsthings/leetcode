# https://leetcode.com/problems/distinct-echo-substrings/
# difficulty: hard
# tags: rolling hash

# Problem
# Return the number of distinct non-empty substrings of text that can be written as the concatenation of some string with itself (i.e. it can be written as a + a where a is some string).

# Solution, O(n^2) time, O(n) space
# For each length, do two back to back rolling hashes and compare them. I had to memoize cBasePow to make it run in time. An easier to implement solution is get all hash codes for each position, then for each position check if the prior position has a matching hash code, and compare it.

MOD = 10**9 + 7

# a=1, b=2, ...
def charNum(letter):
    return ord(letter) - ord('a') + 1

@cache
def cBasePow(c, base, pow):
    return c * base**pow

class Solution:
    def distinctEchoSubstrings(self, text: str) -> int:
        # char * 26^3 + char * 26^2 + char * 26^1 + char * 26^0...

        res = 0

        def checkSize(doubledSize):
            nonlocal res
            size = int(doubledSize / 2)
            maxExponent = size - 1

            firstR = size - 1
            firstHash = 0

            seen = set() # prevent duplicate echos

            exponent = maxExponent
            for i in range(0, firstR + 1):
                rank = charNum(text[i])
                firstHash += cBasePow(rank, 26, exponent)
                firstHash %= MOD
                exponent -= 1

            secondR = 2 * size - 1
            secondHash = 0

            exponent = maxExponent
            for i in range(secondR - size + 1, secondR + 1):
                rank = charNum(text[i])
                secondHash += cBasePow(rank, 26, exponent)
                secondHash %= MOD
                exponent -= 1

            if secondHash == firstHash:
                firstStr = text[:size]
                secondStr = text[size:2*size]
                if firstStr == secondStr:
                    seen.add(firstHash)
                    res += 1

            for rightEdge in range(secondR + 1, len(text)):
                secondGainedChar = text[rightEdge]
                secondLostChar = text[rightEdge - size]
                secondHash -= cBasePow(charNum(secondLostChar), 26, maxExponent)
                secondHash *= 26
                secondHash += charNum(secondGainedChar)
                secondHash %= MOD

                firstGainedChar = secondLostChar
                firstLostChar = text[rightEdge - 2*size]
                firstHash -= cBasePow(charNum(firstLostChar), 26, maxExponent)
                firstHash *= 26
                firstHash += charNum(firstGainedChar)
                firstHash %= MOD

                if secondHash == firstHash and firstHash not in seen:
                    firstStr = text[rightEdge - (2*size) + 1: rightEdge - size + 1]
                    secondStr = text[rightEdge - size + 1:rightEdge + 1]
                    if firstStr == secondStr:
                        res += 1
                        seen.add(firstHash)

        for doubledSize in range(2, (len(text)) + 1, 2):
            checkSize(doubledSize)

        return res
