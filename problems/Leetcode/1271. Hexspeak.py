class Solution:
    def toHexspeak(self, num: str) -> str:
        hexed = hex(int(num))[2:].replace('0', 'O').replace('1', 'I').upper()
        if any(s not in 'ABCDEFIO' for s in hexed):
            return 'ERROR'
        return hexed