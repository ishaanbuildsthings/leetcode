# https://leetcode.com/problems/snapshot-array/
# Difficulty: Medium
# Tags: binary search

# Problem
# SnapshotArray(int length) initializes an array-like data structure with the given length. Initially, each element equals 0.
# void set(index, val) sets the element at the given index to be equal to val.
# int snap() takes a snapshot of the array and returns the snap_id: the total number of times we called snap() minus 1.
# int get(index, snap_id) returns the value at the given index, at the time we took the snapshot with the given snap_id

# Solution, O(snapshot length) to init time and space, O(1) time and space to snap, O(1) time and space to set, O(log snapshots) time and O(1) space to get
# Think how to solve it for just one bucket. When we update it, change the value. When we take a snapshot, increase our internal counter. Now, when we update, there's no value to replace, so we push on a value at the new time. If we take 10 snapshots, then we can just push on a new value at time 10 when we go to update. And if we update again we edit that value.

class SnapshotArray:

    def __init__(self, length: int):
        # data[index] holds a list of tuples of data, time
        self.data = [  [ [0, 0] ] for _ in range(length)  ]
        self.currentSnapId = 0

    def set(self, index: int, val: int) -> None:
        bucket = self.data[index]
        lastTime = bucket[-1][1]
        if lastTime == self.currentSnapId:
            self.data[index][-1][0] = val
        else:
            self.data[index].append([val, self.currentSnapId])

    def snap(self) -> int:
        self.currentSnapId += 1
        return self.currentSnapId - 1

    def get(self, index: int, snap_id: int) -> int:
        bucket = self.data[index]
        # we need to find the last index that has time <= snap_id
        l = 0
        r = len(self.data[index]) - 1
        while l <= r:
            m = (r + l) // 2 # m is the index in the bucket we check
            if bucket[m][1] <= snap_id:
                l = m + 1
            else:
                r = m - 1
        return bucket[r][0]


# Your SnapshotArray object will be instantiated and called as such:
# obj = SnapshotArray(length)
# obj.set(index,val)
# param_2 = obj.snap()
# param_3 = obj.get(index,snap_id)