def solve(s):
    # print('===============')
    # s = "LIT"
    # print(f'{s=}')
    if len(s) <= 1:
        print(-1)
        return
    
    # s = "LL"

    # idea
    # any two adjacent same letters A, we neutralize by putting B C B C inside them, now that pair is covered
    # if they are different, we neutralize with putting the different character in between them

    # odd = len(s) % 2 == 1

    i = 0
    n = len(s)

    res = []

    # for each index, we will insert 2 after, except for the last index, we insert 2 before
    for i in range(n - 1):
        realI = 3 * i
        res.append(realI + 1)
        res.append(realI + 1)
    
    # for the last index, we insert 2 right before it
    lastI = n - 1
    fullBefore = 3 * lastI
    res.append(fullBefore)
    res.append(fullBefore)
    print(len(res))
    for x in res:
        print(x)
    # A B C <i=2
    # AXX BXX C <i=6

# T I L I I

# T I L   I L T  L I T  I L T  L T   I

        # I X X I X X I < i=2

    # def insert(afterIndex, string):
    #     nonlocal s
    #     before = s[:afterIndex + 1]
    #     after = s[afterIndex + 1:]
    #     s = before + string + after

    #     # A B C D E 
    #     # insert after index 1 XXX

    #     # A B X X X C D E

    # while i < len(s) - 1:
    #     if s[i] == s[i + 1]:
    #         print(f'two chars are equal')
    #         # if the two are equal, we can put 2 after each if its not at the end
    #         if i + 1 < len(s) - 1:
    #             print(f'but the one on the right has even more on its right, inserting 2 blocks of 2')
    #             # but the one on the right has even more on its right
    #             res.extend([i+2] * 2)
    #             insert(i + 1, 'XX')
    #             res.extend([i + 1] * 2)
    #             insert(i, 'XX')
    #         else:
    #             print(f'but the one on the right doesnt have any after, inserting a block of 4')
    #             res.extend([i + 1] * 4)
    #             insert(i, "XXXX")

    #         i += 6
    #         print(f'i now: {i}')
    #         print(f's now: {s}')
    #         continue
        
    #     print(f'the ith chars are different, inserting a single X between them')
        
    #     # if they are different, we simply put a different letter after them
    #     res.append(i + 2)
    #     insert(i + 1, "X")
    #     i += 2
    #     print(f'i now: {i}')
    #     print(f's now: {s}')

    #     # LI
    #     # ^ i=0
    #     # LTI
    #     #    ^ 

        
    #     # return
    
    # # edge case, odd at the end
    # if i == len(s) - 1:
    #     res.append(i)
    #     res.append(i)
    #     insert(i - 1, "XX")
    # # IXXX L
    # # length is 5, i is 4

    # print(len(res))
    # for x in res:
    #     print(x)
    
    # print(f'final s: {s}')


        
        



tests = int(input())
for _ in range(tests):
    n = int(input())
    s = input()
    solve(s)

# L T I L I T

# L L

# L I L

# L T I L

# L T I T L

# L T I T I L

# So L L can balance out

# L L can give us gain of 1 T, 1 I, 1 T+I, 2 T + I, 2 of each


# Basically any pair L L can neutralize itself

# Any pair of different can neutralize themsleves


# (T I) (L I) I

# L L L

# L I T I T L   I L T


# T L I L T I T I

# T I L I I

# TLI LTI LTI


# L I T
# LXI LIT


# T I L I I

# TXI L I I

# TXI LXI I



# LLL

# L I T I T L  L



# L L L


# L I T L I T    L


# L X X L X X X X L 


# T I L I I

# T X I





L I I

L (IT) I I

L (IT) I (LT) I

L (IT) I (LT) I L I 