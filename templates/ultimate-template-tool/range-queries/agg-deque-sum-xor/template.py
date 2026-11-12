# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/agg-deque-sum-xor/template.py
# @operations: append appendLeft getAll pointGet pop popLeft size sumAll xorAll
# @data-structure-type: agg-deque
# @complexities:
#   append: 1
#   appendLeft: 1
#   getAll: N
#   pointGet: 1
#   pop: 1 amortized
#   popLeft: 1 amortized
#   size: 1
#   sumAll: 1
#   xorAll: 1
#   build: N
# @memory:
#   layout: none
#   node: front[1*N] back[1*N]
#   tags: none
#   other: none
#   note: the front half (stored last to first) and the back half hold the window; a pop that empties a half moves half of the other over and rebuilds both (amortized O(1)); the sum and xor are running totals
# Aggregate deque (two stacks): a window that grows and shrinks at both ends (sliding windows, deques) with the sum
# and xor of the whole window in O(1). Each half is a stack that keeps the aggregates of its bottom..top, so a push
# or pop is O(1) and the whole window is one combine of the two tops; a pop that empties its half moves half of the
# other over and rebuilds both, amortized O(1). The sum and xor are running totals. No point assign or range query:
# for those, use a seg tree or treap. All indices 0-based.


class AggDeque:
    __slots__ = ("front", "back", "sm", "xr")

    # O(N) -- arr: the initial array (a list), or left out to start empty
    def __init__(self, arr=()):
        self.front, self.back = [], []  # front: the first values, stored last to first
        self.sm = self.xr = 0
        for v in arr:
            self.append(v)

    # O(1) -- the current length of the window
    def size(self):
        return len(self.front) + len(self.back)

    # O(N) -- the whole window as a list
    def getAll(self):
        return self.front[::-1] + self.back

    # O(1) -- a[i]; needs 0 <= i < size(), else raises IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        f = len(self.front)
        return self.front[f - 1 - i] if i < f else self.back[i - f]

    # O(1) -- append v at the right end
    def append(self, v):
        self.sm += v
        self.xr ^= v
        self.back.append(v)

    # O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    def appendLeft(self, v):
        self.sm += v
        self.xr ^= v
        self.front.append(v)

    # O(1) amortized -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        if self.size() < 1:
            raise IndexError("pop: needs size() >= 1")
        if not self.back:
            self._moveToBack()
        v = self.back.pop()
        self.sm -= v
        self.xr ^= v
        return v

    # O(1) amortized -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises
    # IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        if not self.front:
            self._moveToFront()
        v = self.front.pop()
        self.sm -= v
        self.xr ^= v
        return v

    # O(1) -- a[0] + ... + a[n-1]; needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.size() < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.sm

    # O(1) -- xor of the whole window; needs n >= 1, else raises IndexError
    def xorAll(self):
        if self.size() < 1:
            raise IndexError("xorAll: needs n >= 1")
        return self.xr

    # ---- internals ----

    def _moveToFront(self):  # the back half's first half becomes the front (the front is empty)
        k = (len(self.back) + 1) // 2
        self.front = self.back[:k][::-1]
        self.back = self.back[k:]
        self._rebuild()

    def _moveToBack(self):  # the front half's values nearest the middle (stored first) become the back
        k = (len(self.front) + 1) // 2
        self.back = self.front[:k][::-1]
        self.front = self.front[k:]
        self._rebuild()

    def _rebuild(self):  # every half's aggregates, O(size())
        pass
