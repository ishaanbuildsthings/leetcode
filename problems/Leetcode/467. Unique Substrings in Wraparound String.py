class Solution:
    def findSubstringInWraproundString(self, s: str) -> int:

        # NOTE, i think there is an O(n) not 26n dp worth studying
        
        def getNext(char):
            if char == 'z':
                return 'a'
            return chr(ord(char) + 1)

        furthestRight = defaultdict(int)
        ABC = 'abcdefghijklmnopqrstuvwxyz'
        for letter in ABC:
            reqNext = letter
            currStreak = 0
            bigStreak = 0
            for i in range(len(s)):
                if s[i] == reqNext:
                    currStreak += 1
                    bigStreak = max(bigStreak, currStreak)
                    reqNext = getNext(reqNext)
                else:
                    if s[i] == letter:
                        currStreak = 1
                        bigStreak = max(bigStreak, currStreak)
                        reqNext = getNext(letter)
                    else:
                        currStreak = 0
                        reqNext = letter
            furthestRight[letter] = bigStreak
        
        res = 0
        for letter in ABC:
            right = furthestRight[letter]
            res += right
        
        return res

