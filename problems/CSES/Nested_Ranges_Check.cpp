// Approach 2, O(n log n), TLE in python
// Sort ranges by (L, -R)
// To see if our range [L1, R1] contains a range, as we sweep right we are going to get increasing L2 which is required for containing
// But we need to know the smallest R2 on the right (either via suffix array, or sweep right to left), R2 has to be <= R
// But we need bigger ranges on the left still, consider [1, 3] and [1, 5] if sorted by (L, R), we won't see [1, 5] contains any range to its right
// So we want bigger ranges to be able to "see" smaller ranges on the right
// These issues occur only when L = L2, I thnk we could maybe sort by (L, R) and get it working still but with extra bookkeeping
// For the inverse question (are we contained in a range it is similar logic)
// n = int(input())
// ranges = []
// for i in range(n):
//     l, r = map(int, input().split())
//     ranges.append([l, r, i])
// ranges.sort(key=lambda x: (x[0], -x[1]))
// doesContainAnother = [False] * n
// isContained = [False] * n
// maxR = -1
// for l, r, i in ranges:
//     if r <= maxR:
//         isContained[i] = True
//     maxR = max(maxR, r)
// minR = 10000000000
// for j in range(len(ranges) - 1, -1, -1):
//     l, r, i = ranges[j]
//     if r >= minR:
//         doesContainAnother[i] = True
//     minR = min(minR, r)

// print(*list(map(int, doesContainAnother)))
// print(*list(map(int, isContained)))


// I think we could do a normal (L, R) sort but it would require some extra bookkeeping to handle the 
// APPROACH 1
// Sort each range by (L, R)
// For each intervals [L, R], find the i...j range in our sorted array with an L_2 >= L and < R
// Find the smallest R out of elements in that range with a sparse table or seg tree, if R_2 < R, we contain a range
// Also check the edge case where R_2 = R, we can manually store the largest L for each R_2
// Repeat process for second part of the question
// O(n log n) time, TLE in python
// #include <bits/stdc++.h>
// using namespace std;

// TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
// O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant

class SparseTable {
public:
    vector<vector<int>> sparse;
    function<int(int, int)> combineFn;
    vector<int> pow2;

    SparseTable() {}

    SparseTable(const vector<int>& nums, function<int(int, int)> combineFn) {
        int n = (int)nums.size();
        this->combineFn = combineFn;

        if (n == 0) {
            sparse.clear();
            pow2.clear();
            return;
        }

        // Calculate number of bits needed
        int BITS = 0;
        int temp = n;
        while (temp) {
            BITS += 1;
            temp >>= 1;
        }
        BITS += 1;

        // Initialize the sparse table
        sparse.assign(BITS, vector<int>(n, 0));
        for (int left = 0; left < n; left++) {
            sparse[0][left] = nums[left];
        }

        // Precompute powers of 2
        pow2.assign(BITS, 1);
        for (int log = 1; log < BITS; log++) {
            pow2[log] = pow2[log - 1] * 2;
        }

        for (int log = 1; log < BITS; log++) {
            int step = pow2[log - 1];
            for (int left = 0; left + pow2[log] <= n; left++) {
                sparse[log][left] = combineFn(sparse[log - 1][left], sparse[log - 1][left + step]);
            }
        }
    }

    int query(int l, int r) {
        int width = r - l + 1;
        // Find largest power of 2 <= width using bit operations
        int power = 0;
        int temp = width;
        while (temp > 1) {
            power += 1;
            temp >>= 1;
        }
        int windowWidth = pow2[power];
        return combineFn(sparse[power][l], sparse[power][r - windowWidth + 1]);
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    struct custom_hash {
        static uint64_t splitmix64(uint64_t x) {
            x += 0x9e3779b97f4a7c15ULL;
            x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
            x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
            return x ^ (x >> 31);
        }
        size_t operator()(uint64_t x) const {
            static const uint64_t FIXED_RANDOM =
                chrono::steady_clock::now().time_since_epoch().count();
            return (size_t)splitmix64(x + FIXED_RANDOM);
        }
    };
    
    unordered_map<int, int, custom_hash> biggestLPerR;
    unordered_map<int, int, custom_hash> smallestLPerR;
    biggestLPerR.reserve((size_t)n * 2);
    smallestLPerR.reserve((size_t)n * 2);
    biggestLPerR.max_load_factor(0.7f);
    smallestLPerR.max_load_factor(0.7f);
    

    vector<array<int, 3>> ranges; // holds [L, R, i]
    ranges.reserve(n);

    for (int i = 0; i < n; i++) {
        int l, r;
        cin >> l >> r;
        ranges.push_back({l, r, i});

        auto itBig = biggestLPerR.find(r);
        if (itBig != biggestLPerR.end()) {
            if (l > itBig->second) itBig->second = l;
        } else {
            biggestLPerR[r] = l;
        }

        auto itSmall = smallestLPerR.find(r);
        if (itSmall != smallestLPerR.end()) {
            if (l < itSmall->second) itSmall->second = l;
        } else {
            smallestLPerR[r] = l;
        }
    }

    sort(ranges.begin(), ranges.end(), [](const array<int, 3>& a, const array<int, 3>& b) {
        if (a[0] != b[0]) return a[0] < b[0];
        if (a[1] != b[1]) return a[1] < b[1];
        return a[2] < b[2];
    });

    // for each range, find the leftmost range with an L_j >= L_i and L_j < R_i
    // Within that contiguous range, find the smallest R, if it is less than R_i we have a containing range
    // Also check the largest L for a given R_i ending, to handle the edge case of a range sharing an end
    vector<int> L_values(n), R_values(n);
    for (int idx = 0; idx < n; idx++) {
        L_values[idx] = ranges[idx][0];
        R_values[idx] = ranges[idx][1];
    }

    SparseTable minSparse(R_values, [](int x, int y) { return min(x, y); });
    SparseTable maxSparse(R_values, [](int x, int y) { return max(x, y); });

    vector<bool> resultsHasAnotherRangeInside(n, false);
    vector<bool> resultIsInsideAnotherRange(n, false);

    for (auto &triple : ranges) {
        int l = triple[0];
        int r = triple[1];
        int i = triple[2];

        // for each range, find the leftmost range with an L_j >= L_i and L_j < R_i
        // Within that contiguous range, find the smallest R, if it is less than R_i we have a containing range
        // Also check the largest L for a given R_i ending, to handle the edge case of a range sharing an end
        if (biggestLPerR[r] > l) {
            resultsHasAnotherRangeInside[i] = true;
        } else {
            int leftmostI = (int)(lower_bound(L_values.begin(), L_values.end(), l) - L_values.begin());
            int rightmostI = (int)(lower_bound(L_values.begin(), L_values.end(), r) - L_values.begin()) - 1;
            int small = minSparse.query(leftmostI, rightmostI);
            if (small < r) {
                resultsHasAnotherRangeInside[i] = true;
            }
        }

        // Now to find if another range contains us, we need to look at all ranges with an L_j <= L
        // For those, find the biggest R in that range, if it is > r that works
        // Also check the smallest L per R to handle the edge case
        if (smallestLPerR[r] < l) {
            resultIsInsideAnotherRange[i] = true;
        } else {
            // Find rightmost index where L_j <= l
            int rightmostI = (int)(upper_bound(L_values.begin(), L_values.end(), l) - L_values.begin()) - 1;
            if (rightmostI >= 0) {
                int big = maxSparse.query(0, rightmostI);
                if (big > r) {
                    resultIsInsideAnotherRange[i] = true;
                }
            }
        }
    }

    for (int i = 0; i < n; i++) {
        if (i) cout << ' ';
        cout << (resultsHasAnotherRangeInside[i] ? 1 : 0);
    }
    cout << "\n";

    for (int i = 0; i < n; i++) {
        if (i) cout << ' ';
        cout << (resultIsInsideAnotherRange[i] ? 1 : 0);
    }
    cout << "\n";

    return 0;
}

// Approach 1, but in python (TLE)
// if True:
//     from io import BytesIO, IOBase
//     import math

//     import random
//     import sys
//     import os

//     import bisect
//     import typing
//     from collections import Counter, defaultdict, deque
//     from copy import deepcopy
//     from functools import cmp_to_key, lru_cache, reduce
//     from heapq import heapify, heappop, heappush, heappushpop, nlargest, nsmallest
//     from itertools import accumulate, combinations, permutations, count
//     from operator import add, iand, ior, itemgetter, mul, xor
//     from string import ascii_lowercase, ascii_uppercase, ascii_letters
//     from typing import *
//     BUFSIZE = 4096

//     class FastIO(IOBase):
//         newlines = 0

//         def __init__(self, file):
//             self._fd = file.fileno()
//             self.buffer = BytesIO()
//             self.writable = "x" in file.mode or "r" not in file.mode
//             self.write = self.buffer.write if self.writable else None

//         def read(self):
//             while True:
//                 b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
//                 if not b:
//                     break
//                 ptr = self.buffer.tell()
//                 self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(ptr)
//             self.newlines = 0
//             return self.buffer.read()

//         def readline(self):
//             while self.newlines == 0:
//                 b = os.read(self._fd, max(os.fstat(self._fd).st_size, BUFSIZE))
//                 self.newlines = b.count(b"\n") + (not b)
//                 ptr = self.buffer.tell()
//                 self.buffer.seek(0, 2), self.buffer.write(b), self.buffer.seek(ptr)
//             self.newlines -= 1
//             return self.buffer.readline()

//         def flush(self):
//             if self.writable:
//                 os.write(self._fd, self.buffer.getvalue())
//                 self.buffer.truncate(0), self.buffer.seek(0)

//     class IOWrapper(IOBase):
//         def __init__(self, file):
//             self.buffer = FastIO(file)
//             self.flush = self.buffer.flush
//             self.writable = self.buffer.writable
//             self.write = lambda s: self.buffer.write(s.encode("ascii"))
//             self.read = lambda: self.buffer.read().decode("ascii")
//             self.readline = lambda: self.buffer.readline().decode("ascii")

//     sys.stdin = IOWrapper(sys.stdin)
//     sys.stdout = IOWrapper(sys.stdout)
//     input = lambda: sys.stdin.readline().rstrip("\r\n")

//     def I():
//         return input()

//     def II():
//         return int(input())

//     def MII():
//         return map(int, input().split())

//     def LI():
//         return list(input().split())

//     def LII():
//         return list(map(int, input().split()))

//     def GMI():
//         return map(lambda x: int(x) - 1, input().split())

//     def LGMI():
//         return list(map(lambda x: int(x) - 1, input().split()))

//     inf = float('inf')
    
// import bisect, collections
// import math

// TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
// O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant

// class SparseTable:
//     def __init__(self, nums, combineFn):
//         n = len(nums)
//         if n == 0:
//             self.sparse = []
//             self.combineFn = combineFn
//             return
        
//         Calculate number of bits needed
//         BITS = 0
//         temp = n
//         while temp:
//             BITS += 1
//             temp >>= 1
//         BITS += 1

//         Initialize the sparse table
//         sparse = [[0] * n for _ in range(BITS)]
//         for left in range(n):
//             sparse[0][left] = nums[left]

//         Precompute powers of 2
//         pow2 = [1] * BITS
//         for log in range(1, BITS):
//             pow2[log] = pow2[log - 1] * 2

//         for log in range(1, BITS):
//             step = pow2[log - 1]
//             for left in range(n - pow2[log] + 1):
//                 sparse[log][left] = combineFn(sparse[log - 1][left], sparse[log - 1][left + step])

//         self.sparse = sparse
//         self.combineFn = combineFn
//         self.pow2 = pow2

//     def query(self, l, r):
//         width = r - l + 1
//         Find largest power of 2 <= width using bit operations
//         power = 0
//         temp = width
//         while temp > 1:
//             power += 1
//             temp >>= 1
//         windowWidth = self.pow2[power]
//         return self.combineFn(self.sparse[power][l], self.sparse[power][r - windowWidth + 1])

// n = II()
// biggestLPerR = {}
// smallestLPerR = {}
// ranges = [] holds [L, R, i]
// for i in range(n):
//     l, r = MII()
//     ranges.append([l, r, i])
//     if r in biggestLPerR:
//         if l > biggestLPerR[r]:
//             biggestLPerR[r] = l
//     else:
//         biggestLPerR[r] = l
//     if r in smallestLPerR:
//         if l < smallestLPerR[r]:
//             smallestLPerR[r] = l
//     else:
//         smallestLPerR[r] = l
// ranges.sort()

// fmin = lambda x, y: x if x < y else y
// fmax = lambda x, y: x if x > y else y
// for each range, find the leftmost range with an L_j >= L_i and L_j < R_i
// Within that contiguous range, find the smallest R, if it is less than R_i we have a containing range
// Also check the largest L for a given R_i ending, to handle the edge case of a range sharing an end
// L_values = [r[0] for r in ranges]
// R_values = [r[1] for r in ranges]
// minSparse = SparseTable(R_values, fmin)
// maxSparse = SparseTable(R_values, fmax)

// resultsHasAnotherRangeInside = [False] * n
// resultIsInsideAnotherRange = [False] * n

// for l, r, i in ranges:
//     for each range, find the leftmost range with an L_j >= L_i and L_j < R_i
//     Within that contiguous range, find the smallest R, if it is less than R_i we have a containing range
//     Also check the largest L for a given R_i ending, to handle the edge case of a range sharing an end
//     if biggestLPerR[r] > l:
//         resultsHasAnotherRangeInside[i] = True
//     else:
//         leftmostI = bisect.bisect_left(L_values, l)
//         rightmostI = bisect.bisect_left(L_values, r) - 1
//         small = minSparse.query(leftmostI, rightmostI)
//         if small < r:
//             resultsHasAnotherRangeInside[i] = True

//     Now to find if another range contains us, we need to look at all ranges with an L_j <= L
//     For those, find the biggest R in that range, if it is > r that works
//     Also check the smallest L per R to handle the edge case
//     if smallestLPerR[r] < l:
//         resultIsInsideAnotherRange[i] = True
//     else:
//         Find rightmost index where L_j <= l
//         rightmostI = bisect.bisect_right(L_values, l) - 1
//         if rightmostI >= 0:
//             big = maxSparse.query(0, rightmostI)
//             if big > r:
//                 resultIsInsideAnotherRange[i] = True

// res1 = ' '.join(str(int(x)) for x in resultsHasAnotherRangeInside)
// res2 = ' '.join(str(int(x)) for x in resultIsInsideAnotherRange)
// print(res1)
// print(res2)