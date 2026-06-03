class Solution:
    def toHexspeak(self, num: str) -> str:
        # convert to base 16
        num = int(num)
        base16 = []
        while num:
            last = num % 16
            base16.append(last)
            num -= last
            num //= 16
        base16 = base16[::-1]
        base16 = [
            str(x) if x <= 9 else 'ABCDEF'[x - 10] for x in base16]
        base16 = ['I' if x == '1' else 'O' if x == '0' else x for x in base16]
        if any(x not in 'ABCDEFGIO' for x in base16):
            return 'ERROR'
        return ''.join(base16)