# takes a string '255.0.0.7' -> some 32 bit int
def ipToNum(s):
    a, b, c, d = s.split('.')
    res = 0
    res |= int(a) << 24
    res |= int(b) << 16
    res |= int(c) << 8
    res |= int(d)
    return res

# takes a 32 bit int and produces a string
def numToIp(num):
    mask = (1 << 8) - 1
    fourth = num & mask
    third = (num >> 8) & mask
    second = (num >> 16) & mask
    first = (num >> 24) & mask
    return f'{str(first)}.{str(second)}.{str(third)}.{str(fourth)}'

class Solution:
    def ipToCIDR(self, ip: str, n: int) -> List[str]:
        res = []
        curr = ipToNum(ip)


class Solution:
    def ipToCIDR(self, ip: str, n: int) -> List[str]:
        cur = ipToNum(ip)
        res = []
        # we need to process n total IPs
        while n:
            lsb = cur & -cur if cur != 0 else (1 << 32)
            # say our LSB is like 000101010....1000 <- lsb is here
            # in this case lsb=8 (1<<3)
            # that means the block of 000 can take on 8 values uniquely, so if we used this LSB prefix
            # we would need to cover 8 values

            # but maybe we can't take a block of size lsb because that exceeds n
            # so cap by largest power of 2 <= n
            countSize = 1 << (n.bit_length() - 1)
            size = min(lsb, countSize)

            prefixLength = 32 - (size.bit_length() - 1)
            res.append(f"{numToIp(cur)}/{prefixLength}")

            cur += size
            n -= size
        return res

