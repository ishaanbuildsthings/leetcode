class Solution:
    def maximumSwap(self, num: int) -> int:
        # Can do O(n) greedy
        res = num
        num = str(num)
        for i in range(len(num) - 1):
            for j in range(i + 1, len(num)):
                new = num[:i] + num[j] + num[i+1:j] + num[i] + num[j+1:]
                res = max(res, int(new))
        return res
        # strNum = str(num)
        # # we need to find first increasing char
        # for i, char in enumerate(strNum):
        #     if i == 0 or int(char) <= int(strNum[i - 1]):
        #         continue
        #     print(f'we are increasing at index: {i}')
        #     for j in range(i):
        #         if int(strNum[j]) < int(char):
        #             print(f'at index j we are smaller: {j}')
        #             return int(
        #                 ''.join(strNum[:j]) if j > 0 else '' +
        #                 char +
        #                 ''.join(strNum[j + 1: i]) +
        #                 strNum[j] +
        #                 strNum[i + 1:]
        #             )
        # return num


        #     # # find biggest digit to the right
        #     # biggestRight = max(int(char) for char in strNum[i + 1:])
        #     # print(f'biggest right: {biggestRight}')
        #     # return int(
        #     #     ''.join(strNum[:i]) + 
        #     #     str(biggestRight) + 
        #     #     strNum[i + 1: -1] +
        #     #     char
        #     # )

        #     # 538
        #     #   ^ first increasing
        #     # ^ smallest, this is j

        #     # now we return everything before j
        #     # plus our first increasing char
        #     # plus everything between j and i
        #     # plus i
        #     # plus everything sfter i


