# https://leetcode.com/problems/strong-password-checker-ii/description/
# difficulty: easy

# Problem
# A password is said to be strong if it satisfies all the following criteria:

# It has at least 8 characters.
# It contains at least one lowercase letter.
# It contains at least one uppercase letter.
# It contains at least one digit.
# It contains at least one special character. The special characters are the characters in the following string: "!@#$%^&*()-+".
# It does not contain 2 of the same character in adjacent positions (i.e., "aab" violates this condition, but "aba" does not).
# Given a string password, return true if it is a strong password. Otherwise, return false.

# Solution, O(n) time and O(1) space

class Solution:
    def strongPasswordCheckerII(self, password: str) -> bool:
        if len(password) < 8:
            return False

        lowercase = False
        uppercase = False
        digit = False
        special = False


        for i in range(len(password)):
            char = password[i]
            if char.islower():
                lowercase = True
            elif char.isupper():
                uppercase = True
            elif char in '!@#$%^&*()-+':
                special = True
            elif char.isdigit():
                digit = True
            if i < len(password) - 1:
                if char == password[i + 1]:
                    return False

        return lowercase and uppercase and digit and special


