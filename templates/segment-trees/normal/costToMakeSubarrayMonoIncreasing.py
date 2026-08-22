# compute the cost to make an array from l...r mono-increasing where a single cost lets us increment an index by 1
# O(n log n) build, O(1) query range
class MonoIncreaseCost:
    """Min increments to make a range non-decreasing (increments only).
    Build: O(n log n) time and space.  query: O(1).  Static array."""

    def __init__(self, arr):
        self.arr = arr
        n = self.n = len(arr)
        self.pf = list(accumulate(arr, initial=0))

        # suff[i] = sum of prefix maxes over [i, n-1], measured from i
        suff = [0] * (n + 1)
        st = []
        for i in range(n - 1, -1, -1):
            while st and arr[st[-1]] <= arr[i]:
                st.pop()
            nxt = st[-1] if st else n
            suff[i] = arr[i] * (nxt - i) + suff[nxt]
            st.append(i)
        self.suff = suff

        # sparse table of argmax
        self.sp = [list(range(n))]
        j = 1
        while (1 << j) <= n:
            prev = self.sp[-1]
            half = 1 << (j - 1)
            cur = [0] * (n - (1 << j) + 1)
            for i in range(len(cur)):
                a, b = prev[i], prev[i + half]
                cur[i] = a if arr[a] >= arr[b] else b
            self.sp.append(cur)
            j += 1

    def rawSum(self, l, r):
        return self.pf[r + 1] - self.pf[l] if r >= l else 0

    def argMax(self, l, r):
        j = (r - l + 1).bit_length() - 1
        a = self.sp[j][l]
        b = self.sp[j][r - (1 << j) + 1]
        return a if self.arr[a] >= self.arr[b] else b

    def query(self, l, r):
        """Min increments to make arr[l..r] non-decreasing. O(1)."""
        m = self.argMax(l, r)
        endsAt = (self.suff[l] - self.suff[m]) + self.arr[m] * (r - m + 1)
        return endsAt - self.rawSum(l, r)