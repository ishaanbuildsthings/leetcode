class Solution:
    def minOperations(self, s1: str, s2: str) -> int:
        s1 = list(s1)
        s2 = list(s2)
        
        # 11
        # 00

        # 0
        # 1

        res = 0
        n = len(s1)

        for i in range(n - 1, 0, -1):
            req = s2[i]
            have = s1[i]

            if req == '0':
                # if the right is a 0, we must zero it out
                if have == '1':
                    if i == 0:
                        return -1
                    # turn the previous into a 1 and zero them out
                    prevHave = s1[i - 1]
                    if prevHave == '0':
                        s1[i - 1] = '1'
                        res += 1
                    # zero them out
                    s1[i - 1] = '0'
                    s1[i] = '0'
                    res += 1
                    continue
                # if we have two zeroes for now do nothing
                elif have == '0':
                    continue
                    
            elif req == '1':
                if have == '1':
                    continue
                elif have == '0':
                    res += 1
                    s1[i] = '1'
                    continue

        # handle the very first index last
        if s1[0] == s2[0]:
            return res

        if s2[0] == '1':
            return 1 + res # change from 0->1

        if len(s1) == 1:
            return -1

        # now we have a
        # 1
        # 0

        nxt = s1[1]
        # zero out then reset the right
        if nxt == '1':
            return 2 + res
        # flip right then zero out
        elif nxt == '0':
            return 2 + res
        