class Solution:
    def findPermutation(self, s: str) -> List[int]:
        n = len(s) + 1 # length of result
        res = list(range(1, n + 1))
        i = 0
        while i < len(s):
            if s[i] == 'I':
                i += 1
                continue
            j = i
            while j < len(s) and s[j] == 'D':
                j += 1
            # i...j-1 is the D chain
            # a chain of length 3 is responsible for 3 gaps, so 4 elements
            chainWidth = (j - 1 - i + 1)
            elementsAffected = chainWidth + 1
            res[i:i+elementsAffected] = res[i:i+elementsAffected][::-1]
            i = i + elementsAffected
        
        return res


# String:    I   I   D   D   D   I

# === i=0: 'I', skip ===
# === i=1: 'I', skip ===

# === D-chain: i=2 ===

# j scans: s[2]='D' ✓  s[3]='D' ✓  s[4]='D' ✓  s[5]='I' ✗ → j=5

# Index:    0   1   2   3   4   5   6
#         [ 1 , 2 , 3 , 4 , 5 , 6 , 7 ]
#                   \___________/
#                      reverse!
#         [ 1 , 2 , 6 , 5 , 4 , 3 , 7 ]
#               2<6 ✓ 6>5 ✓ 5>4 ✓ 4>3 ✓ 3<7 ✓


        # blocks = [] # holds [I, I, DDD, I, DD, I, D] like that, single I
#         cntD = 0
#         for i, v in enumerate(s):
#             if v == 'I':
#                 if cntD:
#                     blocks.append('D' * cntD)
#                     cntD = 0
#                 blocks.append('I')
#             else:
#                 cntD += 1
#         if cntD:
#             blocks.append('D' * cntD)
        

#         # print(f'{blocks=}')
                

#         lo = 1
#         res = []
#         i = 0
#         while i < len(blocks):
#             # print(f'res now: {res}')
#             block = blocks[i]
#             if block == 'I':
#                 # an I followed by an I, we can place the smallest
#                 if i < len(blocks) - 1 and blocks[i + 1] == 'I':
#                     res.append(lo)
#                     lo += 1
#                     i += 1
#                     continue
#                 # # I followed by a D
#                 # elif i < len(blocks) - 1:
#                 #     nxtD = len(blocks[i + 1])
#                 #     top = lo + nxtD
#                 #     for num in range(top, lo - 1, -1):
#                 #         res.append(num)
#                 #     lo = top + 1
#                 #     i += 2
#                 #     continue


#                 # I followed by a D block
#                 elif i < len(blocks) - 1:
#                     nxtD = len(blocks[i + 1])
#                     # EDGE CASE, if nxtD is only one, we cannot just place lo then above it, or we might simply place like [4, 5] where the 5 doesn't descend since it was a chain of length 1
#                     # but if it is the last D block like s='ID' then we can because we make [1, 3, 2]
#                     # if nxtD == 1:
#                     #     if i + 1 == len(blocks) - 1:
#                     #         res.append(lo)
#                     #         res.append(lo + 2)
#                     #         res.append(lo + 1)
#                     #         break
#                     #     res.append(lo + 1)
#                     #     res.append(lo)
#                     #     lo += 2
#                     #     i += 2
#                     #     continue

#                     res.append(lo)        # I gets the smallest
#                     lo += 1
#                     top = lo + nxtD - 1   # D-block of length k needs k+1 numbers,
#                                         # but first one is shared with I's "next"
#                     for num in range(top, lo - 1, -1):
#                         res.append(num)
#                     lo = top + 1
#                     i += 2


#                 # I followed by nothing
#                 else:
#                     res.append(lo)
#                     lo += 1
#                     i += 1
#                     continue

#             # D block means we just go down
#             else:
#                 top = lo + len(block)
#                 for num in range(top, lo - 1, -1):
#                     res.append(num)
#                 lo = top + 1
#                 i += 1
#                 continue

#         # print(f'init res: {res}')
#         if len(res) < len(s) + 1:
#             res.append(lo)
        
#         return res


#         # 3 2 1 4 5 

# #         blocks=['DD', 'I', 'I', 'D', 'I']
# # init res: [3, 2, 1, 4, 5, 7, 6, 8]

# # cant just greedy^ because we run out of numbers less than 5


# # DD

# # Can start with 3 cause we make 3 2 1

# # Now we just have some other subproblem of X...Y with a new sequence

# # but if we start with I and put 1 2 then need to drop

# # i cant put the lowest if i need to drop right after


# # 3 2 1 4 6 5 7