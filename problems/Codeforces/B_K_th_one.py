import sys
input = sys.stdin.readline

n, m = map(int, input().split())
arr = list(map(int, input().split()))

next_power_of_2 = 1 << (len(arr) - 1).bit_length()
while len(arr) < next_power_of_2:
    arr.append(0)

# Iterative tree with 2*N memory, left child = 2*i, right child = 2*i + 1
#
# Complexities:
#   Build: O(n)
#   Space: O(n)
#   Query/Update: O(log n)
#
# baseFn:    function(value) -> nodeValue
# combineFn: function(leftVal, rightVal) -> newValue
class SegmentTree:
    def __init__(self, arr, baseFn, combineFn):
        self.n = len(arr)
        self._baseFn = baseFn
        self._combine = combineFn
        self.arr = arr

        self.N = self.n
        self.tree = [None] * (2 * self.N)

        # Build leaves at indices [N..2N-1]
        for i in range(self.N):
            self.tree[self.N + i] = self._baseFn(arr[i])

        # Build internal nodes at [1..N-1]
        for i in range(self.N - 1, 0, -1):
            leftVal = self.tree[i << 1]
            rightVal = self.tree[(i << 1) | 1]
            self.tree[i] = self._combine(leftVal, rightVal)

    # O(log n)
    def updateAndMutateArray(self, index, newVal):
        # Update the leaf
        pos = self.N + index
        self.tree[pos] = self._baseFn(newVal)
        # Mutate the array
        self.arr[index] = newVal

        # Recompute internals up to the root
        pos >>= 1
        while pos:
            leftVal = self.tree[pos << 1]
            rightVal = self.tree[(pos << 1) | 1]
            self.tree[pos] = self._combine(leftVal, rightVal)
            pos >>= 1

    def queryKthOne(self, k, currNode):
        # print(f'querying kth one, k: {k}, currNode: {currNode}')
        if currNode >= self.N:
            # print(f'curr node is a leaf, returning original index: {currNode - self.N}')
            originalIndex = currNode - self.N
            return originalIndex
        onesInLeftSegment = self.tree[currNode << 1]
        # print(f'onesInLeftSegment: {onesInLeftSegment}')
        if k <= onesInLeftSegment:
            # print(f'k is less than or equal to onesInLeftSegment, going left')
            return self.queryKthOne(k, currNode << 1)
        else:
            # print(f'k is greater than onesInLeftSegment, going right')
            return self.queryKthOne(k - onesInLeftSegment, (currNode << 1) | 1)

    # O(log n)
    def query(self, l, r):
        l += self.N
        r += self.N
        leftRes = None
        rightRes = None

        while l <= r:
            # If l is a right child, use tree[l] and move to next
            if (l & 1) == 1:
                if leftRes is None:
                    leftRes = self.tree[l]
                else:
                    leftRes = self._combine(leftRes, self.tree[l])
                l += 1

            # If r is a left child, use tree[r] and move to previous
            if (r & 1) == 0:
                if rightRes is None:
                    rightRes = self.tree[r]
                else:
                    rightRes = self._combine(self.tree[r], rightRes)
                r -= 1

            l >>= 1
            r >>= 1

        if leftRes is None:
            return rightRes
        if rightRes is None:
            return leftRes
        return self._combine(leftRes, rightRes)

# how many 1s are in the segment
def baseFn(val):
    return val

def combineFn(leftVal, rightVal):
    return leftVal + rightVal

st = SegmentTree(arr, baseFn, combineFn)

for _ in range(m):
    # print(f'----------------------------')
    query = list(map(int, input().split()))
    # print(f'current array: {arr}')
    if query[0] == 1:
      # print(f'query is to set idx: {query[1]} to inverted value')
      idx = query[1]
      oldValue = arr[idx]
      # print(f'old value: {oldValue}')
      newVal = oldValue^1
      st.updateAndMutateArray(idx, newVal)
      # print(f'mutated, arr now: {arr}')
    else:
        # print(f'querying kth one: {query[1] + 1}')
        k = query[1]
        print(st.queryKthOne(k+1, 1))