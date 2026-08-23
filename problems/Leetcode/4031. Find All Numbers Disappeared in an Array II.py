class Solution:
    def findDisappearedNumbers(self, nums: list[int], lower: int, upper: int) -> list[list[int]]:
        # nums = [1, 3, 9, 7]
        nums = sorted(set(nums))
        nums2 = []
        for v in nums:
            if v < lower or v > upper:
                continue
            nums2.append(v)

        nums2.append(upper + 1)

        # print(nums2)

        # badSet = set(nums2)

        gaps = []
        for i in range(len(nums2)):
            prev = lower if i == 0 else nums2[i - 1]
            # print(f'{prev=}')
            RANGE = [prev + 1 if i != 0 else lower, nums2[i] - 1]
            # print(f'RANGE: {RANGE}')
            if RANGE[0] > RANGE[1]:
                continue
            gaps.append(RANGE)

        return gaps
        

        # # nums2 holds bad numbers in the range
        # L = None
        # Li = None
        # hope = lower
        # for i, v in enumerate(nums2):
        #     if v != hope:
        #         L = hope
        #         Li = i
        #         break
        #     hope += 1
        # if L is None:
        #     print(f'early return from L is none')
        #     return []

        # print(f'L is: {L}')
        # print(f'Li is: {Li}')

        # for j in range(Li + 1, len(nums2)):
        #     v = nums2[j]
            
            
            