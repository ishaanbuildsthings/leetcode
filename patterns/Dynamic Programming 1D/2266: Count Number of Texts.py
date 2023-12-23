# https://leetcode.com/problems/count-number-of-texts/description/
# difficulty: medium
# tags: dynamic programming 1d

# problem
# Alice is texting Bob using her phone. The mapping of digits to letters is shown in the figure below.


# In order to add a letter, Alice has to press the key of the corresponding digit i times, where i is the position of the letter in the key.

# For example, to add the letter 's', Alice has to press '7' four times. Similarly, to add the letter 'k', Alice has to press '5' twice.
# Note that the digits '0' and '1' do not map to any letters, so Alice does not use them.
# However, due to an error in transmission, Bob did not receive Alice's text message but received a string of pressed keys instead.

# For example, when Alice sent the message "bob", Bob received the string "2266622".
# Given a string pressedKeys representing the string received by Bob, return the total number of possible text messages Alice could have sent.

# Since the answer may be very large, return it modulo 109 + 7.

# Solution, O(n) time and space, just try all possible combos with dp

MOD = 10**9 + 7

class Solution:
    def countTexts(self, pressedKeys: str) -> int:
        @cache
        def dp(i):
            # base case
            if i == len(pressedKeys):
                return 1
            resForThis = 0
            # if we press once
            resForThis += dp(i + 1)
            # if we press twice
            if i < len(pressedKeys) - 1 and pressedKeys[i + 1] == pressedKeys[i]:
                resForThis += dp(i + 2)
                # three times
                if i < len(pressedKeys) - 2 and pressedKeys[i + 2] == pressedKeys[i]:
                    resForThis += dp(i + 3)
                    # four times
                    if (pressedKeys[i] == '9' or pressedKeys[i] == '7') and i < len(pressedKeys) - 3 and pressedKeys[i + 3] == pressedKeys[i]:
                        resForThis += dp(i + 4)
            return resForThis % MOD
        return dp(0)
