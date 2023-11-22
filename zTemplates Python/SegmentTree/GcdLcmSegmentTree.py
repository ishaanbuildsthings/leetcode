# ______________________________________________________________________
# TEMPLATE - GCD and LCM segment tree

# FUNCTIONS:
# Query GCD of range O(log(max number) * logN)
# Query LCM of range O(log(max number) * logN)
# Update value O(log(max number) * logN)

# General reqs:
# An array of integers, can be positive or negative (or 0)

# Notes:
# I define GCD(0, a) to be a, which is how math.gcd works. If we get GCD(0, 0), the LCM equation would error (divide by 0), so I define the LCM(0, 0) to be 0, which can be edited in the _lcmRange function.

# Complexities:
# Build: O(n)
# Space: O(n)

class GcdLcmSegmentTree:

    def __init__(self, data):
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n  # each element of the tree will hold a tuple (GCD, LCM) for that range
        self._build(0, 0, self.n - 1)

    def _gcd(self, a, b):
      # formal definition for GCD with negatives
      a = abs(a)
      b = abs(b)
      while b != 0:
        a, b = b, a % b
      return a

    # take the GCD of two separate ranges and combine them, different from normal LCM calculation
    def _lcmRange(self, lcmA, lcmB):
      # NOT A FORMAL DEFINTION. LCM(0, 0) MAY BE DEFINED DIFFERENTLY.
      if lcmA == 0 and lcmB == 0:
        return 0
      return (lcmA // self._gcd(lcmA, lcmB)) * abs(lcmB) # avoid large integers

    # i is the index of the vertex we are at, tl is the left boundary, tr is the right boundary
    def _build(self, i, tl, tr):
        if tl == tr:
            self.tree[i] = (abs(self.data[tl]), abs(self.data[tl])) # GCD and LCM are always >= 0
            return
        tm = (tr + tl) // 2
        self._build(2*i + 1, tl, tm)
        self._build(2*i + 2, tm + 1, tr)
        leftGcd, leftLcm = self.tree[2*i + 1]
        rightGcd, rightLcm = self.tree[2*i + 2]
        self.tree[i] = self._combine(leftGcd, rightGcd, leftLcm, rightLcm)

    def _combine(self, leftGcd, rightGcd, leftLcm, rightLcm):
        newGcd = self._gcd(leftGcd, rightGcd)
        newLcm = self._lcmRange(leftLcm, rightLcm)
        return (newGcd, newLcm)

    # tl and tr are the boundaries of the current node
    # l and r are boundaries we need a max from, in the current node
    def _queryRecurse(self, i, tl, tr, l, r):
        # simplify the code
        if l > r:
            return (0, 1) # GCD of (a, 0) is always a, LCM of (a, 1) is always a
        # perfect match
        if l == tl and r == tr:
            return self.tree[i]
        tm = (tr + tl) // 2 # calculate the middle of our node, basically get the two children
        leftGcd, leftLcm = self._queryRecurse(2*i + 1, tl, tm, l, min(r, tm))
        rightGcd, rightLcm = self._queryRecurse(2*i + 2, tm + 1, tr, max(l, tm + 1), r)
        return self._combine(leftGcd, rightGcd, leftLcm, rightLcm)

    def _updateRecurse(self, i, tl, tr, posToBeUpdated, newVal):
        if tl == tr:
            self.tree[i] = (newVal, newVal)
            return

        tm = (tr + tl) // 2
        if posToBeUpdated <= tm:
            self._updateRecurse(2*i + 1, tl, tm, posToBeUpdated, newVal)
        else:
            self._updateRecurse(2*i + 2, tm + 1, tr, posToBeUpdated, newVal)
        leftGcd, leftLcm = self.tree[2*i + 1]
        rightGcd, rightLcm = self.tree[2*i + 2]
        self.tree[i] = self._combine(leftGcd, rightGcd, leftLcm, rightLcm)

    ################################## PUBLIC METHODS START HERE ##################################

    # Update the value of a cell in the segment tree in O(logN)
    def update(self, index, newVal) -> None:
        self._updateRecurse(0, 0, self.n - 1, index, newVal)

    # Query the GCD from [l:r] in O(logN)
    def queryGcd(self, l, r) -> int:
        return self._queryRecurse(0, 0, self.n - 1, l, r)[0]

    # Query the LCM from [l:r] in O(logN)
    def queryLcm(self, l, r) -> int:
        return self._queryRecurse(0, 0, self.n - 1, l, r)[1]
