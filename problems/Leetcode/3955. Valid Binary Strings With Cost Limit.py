class Solution:
    def generateValidStrings(self, n: int, k: int) -> list[str]:
        res = []
        def bt(bucket, bucketCost):
            if len(bucket) == n:
                res.append(''.join(bucket))
                return

            # only put a 0
            if len(bucket) >= 1 and bucket[-1] == '1':
                bucket.append('0')
                bt(bucket, bucketCost)
                bucket.pop()
                return

            # can put 0 or one
            bucket.append('0')
            bt(bucket, bucketCost)
            bucket.pop()

            bucket.append('1')
            ncost = bucketCost + len(bucket) - 1
            if ncost <= k:
                bt(bucket, ncost)
            bucket.pop()

        x = []
        bt(x, 0)

        return res
                

            