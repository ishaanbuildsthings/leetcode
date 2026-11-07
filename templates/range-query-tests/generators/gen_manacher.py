"""Manacher's algorithm as a range-query template: a static array, O(N) build, then the longest palindrome around any
centre and any palindrome check in O(1). No hashing, so no collisions.

    python3 gen_manacher.py      # then gen_fast.py, then npm run gen:range-queries in site/
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from note_lang import write_template  # noqa: E402

DIR = os.environ.get("RANGE_DIR") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries"
FOLDER = "manacher-palindromes"
OPS = ["getAll", "isPalindrome", "longestPalCenteredAtI", "longestPalCenteredAtIPlusOne", "pointGet"]


def header(cm):
    lines = [f"@operations: {' '.join(OPS)}", "@data-structure-type: manacher", "@letters: same", "@complexities:"]
    lines += [f"  {op}: {'N' if op == 'getAll' else '1'}" for op in OPS] + ["  build: N", "@memory:", "  layout: none",
              "  node: odd[1*N] even[1*N]", "  tags: none", "  other: A[1*N]",
              "  note: odd[i] = how far the palindrome centred on a[i] reaches (its radius, counting a[i]), even[i] = how many pairs the one centred between a[i-1] and a[i] has; Manacher's reuse of the mirrored centre inside the rightmost palindrome makes the build linear"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


ABOUT = ["Manacher's algorithm over a static array: the radius of the longest palindrome around every centre (on a value, and",
         "between two values), built in O(N), so the longest palindrome around a centre and any palindrome check are O(1)",
         "with no hashing. Values are numbers or single characters. All indices 0-based, ranges inclusive."]

PY = '''class Manacher:
    # O(N) -- arr: the array (a list or a string, non-empty)
    def __init__(self, arr):
        self.A = A = list(arr)
        self.n = n = len(A)
        # odd[i]: the largest k with a[i-k+1..i+k-1] a palindrome (so at least 1)
        self.odd = odd = [0] * n
        l, r = 0, -1
        for i in range(n):
            k = 1 if i > r else min(odd[l + r - i], r - i + 1)
            while 0 <= i - k and i + k < n and A[i - k] == A[i + k]:
                k += 1
            odd[i] = k
            if i + k - 1 > r:
                l, r = i - k + 1, i + k - 1
        # even[i]: the largest k with a[i-k..i+k-1] a palindrome (the centre is between a[i-1] and a[i]; 0 when none)
        self.even = even = [0] * n
        l, r = 0, -1
        for i in range(n):
            k = 0 if i > r else min(even[l + r - i + 1], r - i + 1)
            while 0 <= i - k - 1 and i + k < n and A[i - k - 1] == A[i + k]:
                k += 1
            even[i] = k
            if i + k - 1 > r:
                l, r = i - k, i + k - 1

    # O(N) -- the whole array
    def getAll(self):
        return list(self.A)

    # O(1) -- a[i]; needs 0 <= i < n, else raises IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.A[i]

    # O(1) -- is a[l..r] a palindrome; needs 0 <= l <= r < n, else raises IndexError
    def isPalindrome(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"isPalindrome: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        m = r - l + 1
        if m & 1:
            return self.odd[(l + r) // 2] >= (m + 1) // 2
        return self.even[(l + r + 1) // 2] >= m // 2

    # O(1) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)); needs 0 <= i < n, else
    # raises IndexError
    def longestPalCenteredAtI(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"longestPalCenteredAtI: needs 0 <= i < n, got i = {i}, n = {self.n}")
        k = self.odd[i] - 1
        return i - k, i + k

    # O(1) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty range,
    # when there is none (so also for i = n - 1); needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtIPlusOne(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"longestPalCenteredAtIPlusOne: needs 0 <= i < n, got i = {i}, n = {self.n}")
        k = self.even[i + 1] if i + 1 < self.n else 0
        return i - k + 1, i + k
'''

CPP = '''template <typename T>
struct Manacher {
    int n;
    vector<T> A;
    vector<int> odd;  // odd[i]: the largest k with a[i-k+1..i+k-1] a palindrome (so at least 1)
    vector<int> even;  // even[i]: the largest k with a[i-k..i+k-1] a palindrome (the centre is between a[i-1] and a[i]; 0 when none)

    // O(N) -- arr: the array (non-empty); T: int, long long, char, ...
    explicit Manacher(const vector<T>& arr) : n((int)arr.size()), A(arr), odd(n, 0), even(n, 0) {
        for (int i = 0, l = 0, r = -1; i < n; i++) {
            int k = i > r ? 1 : min(odd[l + r - i], r - i + 1);
            while (0 <= i - k && i + k < n && A[i - k] == A[i + k]) k++;
            odd[i] = k;
            if (i + k - 1 > r) l = i - k + 1, r = i + k - 1;
        }
        for (int i = 0, l = 0, r = -1; i < n; i++) {
            int k = i > r ? 0 : min(even[l + r - i + 1], r - i + 1);
            while (0 <= i - k - 1 && i + k < n && A[i - k - 1] == A[i + k]) k++;
            even[i] = k;
            if (i + k - 1 > r) l = i - k, r = i + k - 1;
        }
    }

    // O(N) -- the whole array
    vector<T> getAll() const { return A; }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return A[i];
    }

    // O(1) -- is a[l..r] a palindrome; needs 0 <= l <= r < n, else throws out_of_range
    bool isPalindrome(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("isPalindrome: needs 0 <= l <= r < n");
        int m = r - l + 1;
        if (m & 1) return odd[(l + r) / 2] >= (m + 1) / 2;
        return even[(l + r + 1) / 2] >= m / 2;
    }

    // O(1) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)); needs 0 <= i < n, else
    // throws out_of_range
    pair<int, int> longestPalCenteredAtI(int i) const {
        if (i < 0 || i >= n) throw out_of_range("longestPalCenteredAtI: needs 0 <= i < n");
        int k = odd[i] - 1;
        return {i - k, i + k};
    }

    // O(1) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the empty range,
    // when there is none (so also for i = n - 1); needs 0 <= i < n, else throws out_of_range
    pair<int, int> longestPalCenteredAtIPlusOne(int i) const {
        if (i < 0 || i >= n) throw out_of_range("longestPalCenteredAtIPlusOne: needs 0 <= i < n");
        int k = i + 1 < n ? even[i + 1] : 0;
        return {i - k + 1, i + k};
    }
};
'''


def main():
    path = os.path.join(DIR, FOLDER)
    os.makedirs(path, exist_ok=True)
    top = lambda c, name: f"{c} Template by https://github.com/ishaanbuildsthings\n{c} {URL}/{FOLDER}/{name}\n"  # noqa: E731
    about = "".join
    write_template(os.path.join(path, "template.py"), top("#", "template.py") + header("#") + "\n" + about(f"# {x}\n" for x in ABOUT) + "\n\n" + PY)
    write_template(os.path.join(path, "template.cpp"), top("//", "template.cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" +
                   header("//") + "\n" + about(f"// {x}\n" for x in ABOUT) + CPP)
    print(f"manacher template in {DIR}")


if __name__ == "__main__":
    main()
