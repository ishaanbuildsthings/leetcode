# The rand7() API is already defined for you.
# def rand7():
# @return a random integer in the range 1 to 7

class Solution:
    def rand10(self):
        """
        :rtype: int
        """
        f = rand7() - 1
        s = rand7()

        bij = f * 7 + s

        if bij > 40:
            return self.rand10()
        
        bij -= 1

        return bij // 4 + 1
        