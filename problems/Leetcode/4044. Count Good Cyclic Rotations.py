class Solution:
    def countGoodRotations(self, nums: list[int]) -> int:
        n = len(nums)
        left = deque([nums[i] for i in range(n // 2)])
        right = deque([nums[i] for i in range(n // 2, n)])
        leftSum = sum(left)
        rightSum = sum(right)
        # print(f'{left=} {right=}')
        # print(f'{leftSum=} {rightSum=}')
        res = 0

        for _ in range(n):
            if leftSum > rightSum:
                res += 1

            popped = left.popleft()
            leftSum -= popped
            right.append(popped)
            rightSum += popped
            lostRight = right.popleft()
            rightSum -= lostRight
            left.append(lostRight)
            leftSum += lostRight

            # print('======')
            # print(f'left: {left}')
            # print(f'right: {right}')
            # print(f'{leftSum=} {rightSum=}')
            

        return res