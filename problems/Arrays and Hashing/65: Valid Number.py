# https://leetcode.com/problems/valid-number/
# Difficulty: hard
# tags: dfa

# Solution, O(n) time and space as we create a substring, I'm sure O(1) space is doable
# I just coded multiple states, a DFA is better, what I did can also be improved I just wrote something simple that works

class Solution:
    def isNumber(self, s: str) -> bool:
        def isInt(str):
            if len(str) == 0 or str == '+' or str == '-':
                return False
            start = 0
            if str[0] == '+' or str[0] == '-':
                start += 1

            for j in range(start, len(str)):
                if not str[j].isdigit():
                    return False
            return True

        def isEInt(str):
            return (str[0] == 'e' or str[0] == 'E') and isInt(str[1:])

        def isDecimal(str):
            dotsSeen = 0
            digitsSeen = 0
            start = 0
            if str[0] == '+' or str[0] == '-':
                start += 1
            for j in range(start, len(str)):
                char = str[j]
                if char == '.':
                    dotsSeen += 1
                elif char.isdigit():
                    digitsSeen += 1
                else:
                    return False
            if dotsSeen != 1:
                return False
            if digitsSeen == 0:
                return False
            return True

        def isValidNumber(str):
            for splitPoint in range(len(s)):
                left = s[:splitPoint + 1]
                right = s[splitPoint + 1:] if splitPoint != len(s) - 1 else ''
                if (isDecimal(left) or isInt(left)):
                    if right == '':
                        return True
                    if isEInt(right):
                        return True
            return False

        return isValidNumber(s)
