// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAddArithSeq/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeq
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAdd: log(N)
//   rangeAddArithSeq: log(N)
//   build: N
// @memory:
//   layout: none
//   node: c[1*N] s[1*N]
//   tags: none
//   other: none
//   note: two Fenwick trees over differences; a[i] = prefix(c, i) + i * prefix(s, i)

// Range add of an arithmetic sequence, point get. 0-based, inclusive. T: int, long long, ...
// rangeAddArithSeq(l, r, start, step) adds start + (i - l) * step to a[i], i.e. the line
// (start - l * step) + i * step, so it is one difference update on c and one on s.
template <typename T>
struct ArithSeqBIT {
    int n;
    vector<T> c, s;  // a[i] = prefix(c, i) + i * prefix(s, i)

    // O(N)
    explicit ArithSeqBIT(const vector<T>& a) : n((int)a.size()), c(n + 1), s(n + 1) {
        T prev = 0;
        for (int i = 1; i <= n; i++) {
            c[i] += a[i - 1] - prev;
            prev = a[i - 1];
            int j = i + (i & -i);
            if (j <= n) c[j] += c[i];
        }
    }

    void add(int i, T k, T step) {
        for (i++; i <= n; i += i & -i) c[i] += k, s[i] += step;
    }

    // O(logN) -- a[l + j] += start + j * step for j in [0, r - l]
    void rangeAddArithSeq(int l, int r, T start, T step) {
        T k = start - T(l) * step;
        add(l, k, step);
        if (r + 1 < n) add(r + 1, -k, -step);
    }

    // O(logN) -- a[i] += v for i in [l, r]
    void rangeAdd(int l, int r, T v) {
        for (int i = l + 1; i <= n; i += i & -i) c[i] += v;
        for (int i = r + 2; i <= n; i += i & -i) c[i] -= v;
    }

    // O(logN) -- a[i]
    T pointGet(int i) const {
        T k = 0, coef = 0;
        for (int j = i + 1; j > 0; j &= j - 1) k += c[j], coef += s[j];
        return k + T(i) * coef;
    }

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAdd(i, i, v - pointGet(i)); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        T cur = pointGet(i);
        if (v > cur) rangeAdd(i, i, v - cur);
    }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        T cur = pointGet(i);
        if (v < cur) rangeAdd(i, i, v - cur);
    }
};
