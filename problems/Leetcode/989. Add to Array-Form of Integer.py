class Solution:
    def addToArrayForm(self, num: List[int], k: int) -> List[int]:
        sys.set_int_max_str_digits(10001)
        # bitset shenanigans
        res = 0
        for i in range(len(num)):
            power = len(num) - i - 1
            res += (num[i] * 10 ** power)
        return [int(digit) for digit in str(res + k)]
            