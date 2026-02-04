class Solution:
    def reverseBits(self, n: int) -> int:
        reversed = 0

        # get the last bit, then shift our working number to the right, and add our new bit
        for i in range(1, 33):
            last_bit = n & 1
            n = n >> 1  # next time we need the new last bit of n

            # shift over our reversed number
            reversed = reversed << 1
            # add a digit to the end of the reversed number
            reversed = reversed | last_bit

        return reversed