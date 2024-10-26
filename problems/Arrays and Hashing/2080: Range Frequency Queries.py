# https://leetcode.com/problems/range-frequency-queries/description/
# difficulty: medium
# tags: binary search, segment tree

# Problem
# Design a data structure to find the frequency of a given value in a given subarray.

# The frequency of a value in a subarray is the number of occurrences of that value in the subarray.

# Implement the RangeFreqQuery class:

# RangeFreqQuery(int[] arr) Constructs an instance of the class with the given 0-indexed integer array arr.
# int query(int left, int right, int value) Returns the frequency of value in the subarray arr[left...right].
# A subarray is a contiguous sequence of elements within an array. arr[left...right] denotes the subarray that contains the elements of nums between indices left and right (inclusive).

# Solution 1, I wrote this for practice. I created a segment tree where each ST node stores a hashmap of a number to how many times it occurs in this region. This takes n log n memory (each of the logN layers takes at most n memory). The build also takes n log n time, because to combine two sorted lists takes n time relative to the size of the lists we are combining. To query, I can add up the values for all ST nodes, which is a logN query.
# Note that the code I wrote does something DIFFERENT. Currently, the query function itself combines every key, but we should only care about one. Really, the query function should include the key we care about, and just add up the values from each child dictionary. The actual code presented below should combine up to 2 ST nodes per layer which is n/2 + n/4 + n/8 ... (times 2) for each layer, which is n time for a single query.
# SOLUTION 2, the actual good one is to create a sorted list for every number type (it stores indices) which takes O(n) time and space, then binary search on it. We can use SortedList if we want to support replacement of a number. I think to entirely remove a number we could maybe replace it with a dummy value and dummy sorted list but I haven't really thought about it, I think this goes into more dynamically sized stuff.

IDENTITY = defaultdict(int) # combine(a, IDENTITY) is always a
class FrqsSegmentTree:

    def __init__(self, data):
        self.n = len(data)
        self.data = data
        self.tree = [None] * 4 * self.n
        self._build(1, 0, self.n - 1)

    # returns the data we hold the ST node of width 1, for instance in max + counts we might hold (val, 1)
    def _basefn(self, val):
      # each node should hold the amount of occurences for every number
      nodeDict = defaultdict(int)
      nodeDict[val] += 1
      return nodeDict

    # i is the index of the vertex we are at, tl is the left boundary, tr is the right boundary
    def _build(self, i, tl, tr):
        # base case
        if tl == tr:
            self.tree[i] = self._basefn(self.data[tl])
            return
        tm = (tr + tl) // 2
        self._build(2*i, tl, tm)
        self._build(2*i + 1, tm + 1, tr)
        self.tree[i] = self._combine(self.tree[2*i], self.tree[2*i + 1])

    # takes the result of two children ST nodes (regardless of if they're the value at that node, or some computed value based on l and r bounds), and merges them to get a new parent value
    def _combine(self, a, b):
        newDict = defaultdict(int)
        for key in a:
          newDict[key] += a[key]
        for key in b:
          newDict[key] += b[key]
        return newDict

    # tl and tr are the boundaries of the current node
    # l and r are boundaries we need frqs from, we compare to the current node
    def _queryRecurse(self, i, tl, tr, l, r):
        # if we are contained
        if tl >= l and tr <= r:
            return self.tree[i]

        # if we have no intersection
        if tr < l or tl > r:
            return IDENTITY

        tm = (tr + tl) // 2 # calculate the middle of our node, basically get the two children
        resultLeft = self._queryRecurse(2*i, tl, tm, l, r)
        resultRight = self._queryRecurse(2*i + 1, tm + 1, tr, l, r)
        return self._combine(resultLeft, resultRight)

    ################################## PUBLIC METHODS START HERE ##################################

    # Query the frequencies from [l:r] in O(logN)
    def queryFrqs(self, l, r) -> int:
        return self._queryRecurse(1, 0, self.n - 1, l, r)

class RangeFreqQuery:

    def __init__(self, arr: List[int]):
        self.ST = FrqsSegmentTree(arr)

    def query(self, left: int, right: int, value: int) -> int:
        return self.ST.queryFrqs(left, right)[value]


# Your RangeFreqQuery object will be instantiated and called as such:
# obj = RangeFreqQuery(arr)
# param_1 = obj.query(left,right,value)