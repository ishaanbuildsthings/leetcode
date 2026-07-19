# Wrong Answer
# 282 / 998 testcases passed
# Input
# s =
# "01"
# strs =
# ["?0"]
# Use Testcase
# Output
# [true]
# Expected
# [false]


class Solution:
    def transformStr(self, s: str, strs: List[str]) -> List[bool]:
        ones = s.count('1')
        zeros = s.count('0')
        res = []
        for j in range(len(strs)):
            # print(f'{j=}=======')
            string = strs[j]
            c1 = string.count('1')
            c2 = string.count('0')
            if c1 > ones or c2 > zeros:
                res.append(False)
                continue

            mis = []
            for i in range(len(s)):
                if s[i] == string[i]:
                    continue
                mis.append((s[i], string[i]))

            # print(f'{mis=}')

            # loop left to right
            # banking 1? and 0?

            # if we hit 10 we increment by 1
            # if we hit 01 we either decrement from 10, or we take a banked 10

            # validate: does every 01 pair have enough 10 + 1? on its left?

            # validate: does every 10 pair have enough 01 + 0? on its right?

            a10 = 0
            a1q = 0
            a01 = 0
            fail = False
            for i, tup in enumerate(mis):
                if tup == ('1', '0'):
                    a10 += 1
                elif tup == ('1', '?'):
                    a1q += 1
                elif tup == ('0', '1'):
                    a01 += 1
                    if a01 > (a10 + a1q):
                        fail = True
                        break

            if fail:
                # print(f'failed first validation')
                res.append(False)
                continue

            a01 = 0
            a0q = 0
            a10 = 0
            for i in range(len(mis) - 1, -1, -1):
                tup = mis[i]
                if tup == ('0', '1'):
                    a01 += 1
                elif tup == ('0', '?'):
                    a0q += 1
                elif tup == ('1', '0'):
                    a10 += 1
                    if a10 > (a01 + a0q):
                        fail = True
                        break

            if fail:
                # print(f'failed second validation')
                res.append(False)
                continue

            res.append(True)
        
        return res
            