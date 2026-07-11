class APDiff:
    """
    Offline range arithmetic-progression add. No queries during updates.

    Second-difference array: diff[i] is the change in the step at position i.
    Two prefix sums at the end recover the values.

    mod defaults to 0, which means no modular arithmetic at all.
    Pass a mod to reduce everything into [0, mod); start and step may then
    still be negative, they get normalized on the way in.

    Public operations:
      APDiff(n) or APDiff(n, mod)     O(n)
      rangeAddAP(l, r, start, step)   O(1)
      build()                         O(n)  -- returns the final list of n values
    """

    def __init__(self, n, mod=0):
        self.n = n
        self.MOD = mod
        self.diff = [0] * (n + 2)

    def rangeAddAP(self, l, r, start, step):
        if l > r:
            return
        mod = self.MOD
        diff = self.diff
        if mod:
            start %= mod
            step %= mod
            end = (start + step * (r - l)) % mod
            diff[l] = (diff[l] + start) % mod
            diff[l + 1] = (diff[l + 1] + step - start) % mod
            diff[r + 1] = (diff[r + 1] - end - step) % mod
            diff[r + 2] = (diff[r + 2] + end) % mod
        else:
            end = start + step * (r - l)
            diff[l] += start
            diff[l + 1] += step - start
            diff[r + 1] -= end + step
            diff[r + 2] += end

    def build(self):
        mod = self.MOD
        diff = self.diff
        res = [0] * self.n
        step = 0
        total = 0
        if mod:
            for i in range(self.n):
                step = (step + diff[i]) % mod
                total = (total + step) % mod
                res[i] = total
        else:
            for i in range(self.n):
                step += diff[i]
                total += step
                res[i] = total
        return res