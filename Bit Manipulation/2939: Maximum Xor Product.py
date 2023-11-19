# https://leetcode.com/contest/weekly-contest-372/problems/maximum-xor-product/
# difficulty: medium
# tags: bit manipulation, greedy, contest

class Solution:
    def maximumXorProduct(self, a: int, b: int, n: int) -> int:
        def num(binaryArr):
            return int(''.join(binaryArr), 2)

        bits1 = list(bin(a)[2:].zfill(50))
        bits2 = list(bin(b)[2:].zfill(50))
        # print(f'bits 1: {bits1}')
        # print(f'bits 2: {bits2}')
        # print(f'num1: {num(bits1)} num2: {num(bits2)}')

        startingBit = 50 - n
        # print(f'starting bit is: {startingBit}')
        for bit in range(startingBit, 50):
            currentNum1 = num(bits1)
            currentNum2 = num(bits2)
            currentMult = currentNum1 * currentNum2
            # if we change the bit
            copy1 = bits1.copy()
            copy1[bit] = '1' if copy1[bit] == '0' else '0'
            copy2 = bits2.copy()
            copy2[bit] = '1' if copy2[bit] == '0' else '0'
            newMult = num(copy1) * num(copy2)
            # print(f'new mult is: {newMult}')
            if newMult > currentMult:
                # print(f'new mult is greater, changing')
                bits1 = copy1
                bits2 = copy2
            # not sure
            elif newMult == currentMult:
                oldDiff = abs(currentNum2 - currentNum1)
                newDiff = abs(num(copy1) - num(copy2))
                if newDiff < oldDiff:
                    bits1 = copy1
                    bits2 = copy2

        return (num(bits1) * num(bits2)) % ((10**9) + 7)










#         print(f'bit str 1: {bitStr1}')
#         print(f'bit str 2: {bitStr2}')
