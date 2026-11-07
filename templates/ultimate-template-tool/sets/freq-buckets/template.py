# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/sets/freq-buckets/template.py
# @operations: add clear count countDistinct maxFreq minFreq remove size valuesWithMaxFreq valuesWithMinFreq
# @data-structure-type: freq-buckets
# @values: online
# @keys: numbers
# @tracks: none
# @complexities:
#   add: 1 expected
#   clear: N
#   count: 1 expected
#   countDistinct: 1
#   maxFreq: 1
#   minFreq: 1
#   remove: 1 expected
#   size: 1
#   valuesWithMaxFreq: N
#   valuesWithMinFreq: N
#   build: 1
# @memory:
#   layout: none
#   node: key[1*N] cnt[1*N] links[3*N]
#   tags: none
#   other: hash[4*N] buckets[4*N]
#   note: N = distinct values ever added; a hash table of at most 4*N ints and at most N + 1 buckets

from random import getrandbits


# Multiset of any hashable values (online: nothing known ahead). Add, remove, the highest and the lowest frequency are
# all O(1): values sit in buckets by how many copies they have, and the buckets that exist form a sorted linked list.
# Adding or removing one copy only ever moves a value to the neighbouring bucket, and the two frequencies are the ends
# of the list.
class FreqBuckets:
    __slots__ = ("salt", "slotOf", "vals", "cnt", "bucketOf", "prevInBucket", "nextInBucket", "freq", "firstValue",
                 "prevBucket", "nextBucket", "freeBuckets", "n", "d")

    # O(1)
    def __init__(self):
        self.salt = getrandbits(60)  # hash containers key on this, so no fixed input can force collisions
        self.slotOf = {}  # value -> its slot, 1 and up; each value's fields below are per slot
        self.vals, self.cnt, self.bucketOf = [None], [0], [0]
        self.prevInBucket, self.nextInBucket = [0], [0]  # the values of one bucket: a linked list, 0 ends it
        # bucket 0 joins the list's two ends: nextBucket[0] has the lowest frequency, prevBucket[0] the highest
        self.freq, self.firstValue, self.prevBucket, self.nextBucket = [0], [0], [0], [0]
        self.freeBuckets = []
        self.n = self.d = 0

    def _newBucket(self, f, left):  # a bucket for frequency f, right after bucket left
        if self.freeBuckets:
            b = self.freeBuckets.pop()
        else:
            b = len(self.freq)
            for field in (self.freq, self.firstValue, self.prevBucket, self.nextBucket):
                field.append(0)
        right = self.nextBucket[left]
        self.freq[b], self.firstValue[b] = f, 0
        self.prevBucket[b], self.nextBucket[b] = left, right
        self.nextBucket[left] = self.prevBucket[right] = b
        return b

    def _join(self, slot, b):
        first = self.firstValue[b]
        self.bucketOf[slot], self.prevInBucket[slot], self.nextInBucket[slot] = b, 0, first
        if first:
            self.prevInBucket[first] = slot
        self.firstValue[b] = slot

    def _leave(self, slot):  # an emptied bucket leaves the list
        b, before, after = self.bucketOf[slot], self.prevInBucket[slot], self.nextInBucket[slot]
        if before:
            self.nextInBucket[before] = after
        else:
            self.firstValue[b] = after
        if after:
            self.prevInBucket[after] = before
        if not self.firstValue[b]:
            left, right = self.prevBucket[b], self.nextBucket[b]
            self.nextBucket[left], self.prevBucket[right] = right, left
            self.freeBuckets.append(b)
        self.bucketOf[slot] = 0

    def _values(self, b):
        res, slot = [], self.firstValue[b]
        while slot:
            res.append(self.vals[slot])
            slot = self.nextInBucket[slot]
        return res

    # O(1 expected) -- add one copy of x
    def add(self, x):
        key = x ^ self.salt if x.__class__ is int else x
        slot = self.slotOf.get(key)
        if slot is None:
            slot = self.slotOf[key] = len(self.vals)
            self.vals.append(x)
            for field in (self.cnt, self.bucketOf, self.prevInBucket, self.nextInBucket):
                field.append(0)
        f = self.cnt[slot]
        b = self.bucketOf[slot]
        up = self.nextBucket[b]
        if self.freq[up] != f + 1:
            up = self._newBucket(f + 1, b)
        if f:
            self._leave(slot)
        else:
            self.d += 1
        self._join(slot, up)
        self.cnt[slot] = f + 1
        self.n += 1

    # O(1 expected) -- remove one copy of x if present; returns how many were removed (0 or 1)
    def remove(self, x):
        slot = self.slotOf.get(x ^ self.salt if x.__class__ is int else x)
        if slot is None or not self.cnt[slot]:
            return 0
        f = self.cnt[slot]
        down = self.prevBucket[self.bucketOf[slot]]
        if f > 1 and self.freq[down] != f - 1:
            down = self._newBucket(f - 1, down)
        self._leave(slot)
        if f > 1:
            self._join(slot, down)
        else:
            self.d -= 1
        self.cnt[slot] = f - 1
        self.n -= 1
        return 1

    # O(1 expected) -- how many copies of x
    def count(self, x):
        slot = self.slotOf.get(x ^ self.salt if x.__class__ is int else x)
        return 0 if slot is None else self.cnt[slot]

    # O(1) -- how many values (copies count)
    def size(self):
        return self.n

    # O(1) -- so len(ms) works too
    def __len__(self):
        return self.n

    # O(1) -- how many distinct values
    def countDistinct(self):
        return self.d

    # O(1) -- how many copies the most frequent value has; 0 if empty
    def maxFreq(self):
        return self.freq[self.prevBucket[0]]

    # O(1) -- how many copies the least frequent value in the set has; 0 if empty
    def minFreq(self):
        return self.freq[self.nextBucket[0]]

    # O(how many are tied) -- every value tied for the most copies, in no particular order; empty if the set is empty
    def valuesWithMaxFreq(self):
        return self._values(self.prevBucket[0])

    # O(how many are tied) -- every value tied for the fewest copies, in no particular order; empty if the set is empty
    def valuesWithMinFreq(self):
        return self._values(self.nextBucket[0])

    # O(N) -- remove everything: afterwards it is as if newly built, so reuse it
    def clear(self):
        for slot in range(1, len(self.vals)):
            self.cnt[slot] = self.bucketOf[slot] = 0
        self.freq, self.firstValue, self.prevBucket, self.nextBucket = [0], [0], [0], [0]
        self.freeBuckets = []
        self.n = self.d = 0
