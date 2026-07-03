# TEMPLATE BY LEETGOAT_DOT_IO
# ============================================================================
# 1. FastSet  -  bit-trie over a bounded integer universe [0, n)
#    insert / erase / prev / next : O(log_64 n)      contains : O(1)
#    Python port of the classic C++ "FastSet" (van Emde Boas / bitset layout).
# ============================================================================
class FastSet:
    __slots__ = ("n", "seg", "levels")
    B = 64

    def __init__(self, n: int):
        # universe = [0, n); inserted values must lie in this range
        self.n = n
        self.seg = []
        width = max(n, 1)
        while True:
            num_words = (width + 63) >> 6            # ceil(width / 64)
            self.seg.append([0] * num_words)
            if num_words == 1:
                break
            width = num_words                        # next level summarizes these words
        self.levels = len(self.seg)

    def insert(self, i: int) -> None:
        if i < 0 or i >= self.n:
            return
        seg = self.seg
        for h in range(self.levels):
            seg[h][i >> 6] |= (1 << (i & 63))
            i >>= 6

    def erase(self, i: int) -> None:
        if i < 0 or i >= self.n:
            return
        seg = self.seg
        for h in range(self.levels):
            idx = i >> 6
            seg[h][idx] &= ~(1 << (i & 63))
            if seg[h][idx]:                          # word still non-empty -> parents unchanged
                break
            i = idx                                  # word emptied -> clear its bit in the parent

    def contains(self, i: int) -> bool:
        if i < 0 or i >= self.n:
            return False
        return bool((self.seg[0][i >> 6] >> (i & 63)) & 1)

    def next(self, i: int) -> int:
        """Smallest element >= i, or -1."""
        if i < 0:
            i = 0
        if i >= self.n:
            return -1
        seg = self.seg
        for h in range(self.levels):
            idx = i >> 6
            if idx >= len(seg[h]):
                break
            v = seg[h][idx] >> (i & 63)
            if v:
                i = i + ((v & -v).bit_length() - 1)          # ctz
                for g in range(h - 1, -1, -1):
                    w = seg[g][i]
                    i = (i << 6) + ((w & -w).bit_length() - 1)
                return i
            i = idx + 1
        return -1

    def prev(self, i: int) -> int:
        """Largest element <= i, or -1."""
        if i >= self.n:
            i = self.n - 1
        if i < 0:
            return -1
        seg = self.seg
        for h in range(self.levels):
            idx = i >> 6
            v = seg[h][idx] & ((1 << ((i & 63) + 1)) - 1)    # keep bits <= i%64
            if v:
                i = (idx << 6) + (v.bit_length() - 1)         # highest set bit
                for g in range(h - 1, -1, -1):
                    i = (i << 6) + (seg[g][i].bit_length() - 1)
                return i
            if idx == 0:
                return -1
            i = idx - 1
        return -1