# https://leetcode.com/problems/minimum-number-of-food-buckets-to-feed-the-hamsters/
# difficulty: medium
# tags: greedy

# Solution, O(n) time O(1) space, probably a nice way to roll up the edge cases into the main code

class Solution:
    def minimumBuckets(self, hamsters: str) -> int:
        # edge cases
        if hamsters[0] == 'H' and len(hamsters) > 1 and hamsters[1] == 'H':
            return -1

        if hamsters[-1] == 'H' and len(hamsters) > 1 and hamsters[ - 2] == 'H':
            return -1

        if hamsters == 'H':
            return -1


        # H d . H   (4)

        res = 0
        i = 0
        while i < len(hamsters):
            # 3 in a row
            if hamsters[i] == 'H' and i > 0 and hamsters[i - 1] == 'H' and i < len(hamsters) - 1 and hamsters[i + 1] == 'H':
                return -1

            if hamsters[i] == '.':
                i += 1
                continue

            # if we can place it on the right, do it and skip a hamster if needed
            if i < len(hamsters) - 1 and hamsters[i + 1] == '.':
                res += 1
                if i < len(hamsters) - 2 and hamsters[i + 2] == 'H':
                    i += 3
                else:
                    i += 2
            else:
                res += 1
                i += 1

        return res



