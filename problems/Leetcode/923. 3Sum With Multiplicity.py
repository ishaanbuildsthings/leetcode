MOD = 10**9 + 7
class Solution:
    def threeSumMulti(self, arr: List[int], target: int) -> int:
        singleLeft = Counter()
        doubleLeft = Counter()
        res = 0
        for i in range(len(arr)):
            res += doubleLeft[target - arr[i]]
            for sg in singleLeft:
                nv = sg + arr[i]
                doubleLeft[nv] += singleLeft[sg]
            singleLeft[arr[i]] += 1
        return res % MOD