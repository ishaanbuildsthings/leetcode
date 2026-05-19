// TEMPLATE FROM MY GITHUB: ishaanbuildsthings
// Multiset over non-negative integers in [0, maxVal].
// Supports add, remove, kth element, median, sum, and cost-to-target queries.
//
// USAGE:
//   FenwickMedianSet fms(1000000);  // values in [0, 10^6]
//   fms.add(5);
//   fms.add(3);
//   fms.add(7);
//   fms.median();         // 5
//   fms.costToMedian();   // 4 (|3-5| + |5-5| + |7-5|)
//   fms.costToTarget(4);  // 5 (|3-4| + |5-4| + |7-4|)
//   fms.countLTE(5);      // 2
//   fms.sumGT(4);         // 12 (5 + 7)
//   fms.kthSmallest(0);   // 3 (smallest)
//   fms.remove(5);
struct FenwickMedianSet {
    int n;
    vector<ll> cntTree, sumTree;
    vector<int> cnt;
    ll size_ = 0;
    ll totalSum = 0;
    
    FenwickMedianSet(int maxVal) : n(maxVal) {
        cntTree.assign(n + 2, 0);
        sumTree.assign(n + 2, 0);
        cnt.assign(n + 1, 0);
    }
    
    void _updateCnt(int i, ll delta) {
        i++;
        while (i <= n + 1) {
            cntTree[i] += delta;
            i += i & -i;
        }
    }
    
    void _updateSum(int i, ll delta) {
        i++;
        while (i <= n + 1) {
            sumTree[i] += delta;
            i += i & -i;
        }
    }
    
    ll _queryCnt(int i) {
        // prefix count [0..i]
        i++;
        ll s = 0;
        while (i > 0) {
            s += cntTree[i];
            i -= i & -i;
        }
        return s;
    }
    
    ll _querySum(int i) {
        // prefix sum [0..i]
        i++;
        ll s = 0;
        while (i > 0) {
            s += sumTree[i];
            i -= i & -i;
        }
        return s;
    }
    
    // insert a value
    void add(int val) {
        cnt[val]++;
        _updateCnt(val, 1);
        _updateSum(val, val);
        size_++;
        totalSum += val;
    }
    
    // remove one occurrence of value
    bool remove(int val) {
        if (cnt[val] == 0) return false;
        cnt[val]--;
        _updateCnt(val, -1);
        _updateSum(val, -val);
        size_--;
        totalSum -= val;
        return true;
    }
    
    // total number of elements
    ll size() const { return size_; }
    
    // true if no elements
    bool empty() const { return size_ == 0; }
    
    // count of elements < x
    ll countLT(int x) {
        if (x <= 0) return 0;
        return _queryCnt(min(x - 1, n));
    }
    
    // count of elements <= x
    ll countLTE(int x) {
        if (x < 0) return 0;
        return _queryCnt(min(x, n));
    }
    
    // count of elements > x
    ll countGT(int x) {
        return size_ - countLTE(x);
    }
    
    // count of elements >= x
    ll countGTE(int x) {
        return size_ - countLT(x);
    }
    
    // sum of elements < x
    ll sumLT(int x) {
        if (x <= 0) return 0;
        return _querySum(min(x - 1, n));
    }
    
    // sum of elements <= x
    ll sumLTE(int x) {
        if (x < 0) return 0;
        return _querySum(min(x, n));
    }
    
    // sum of elements > x
    ll sumGT(int x) {
        return totalSum - sumLTE(x);
    }
    
    // sum of elements >= x
    ll sumGTE(int x) {
        return totalSum - sumLT(x);
    }
    
    // find the kth smallest element (0-indexed), O(log n)
    int kthSmallest(ll k) {
        int idx = 0;
        int step = 1;
        while (step * 2 <= n + 1) step *= 2;
        while (step > 0) {
            if (idx + step <= n + 1 && cntTree[idx + step] <= k) {
                idx += step;
                k -= cntTree[idx];
            }
            step >>= 1;
        }
        return idx;
    }
    
    // lower median (for odd: middle; for even: lower middle)
    int median() {
        return kthSmallest((size_ - 1) / 2);
    }
    
    // sum of all elements
    ll sum() const { return totalSum; }
    
    // smallest element
    int minVal() { return kthSmallest(0); }
    
    // largest element
    int maxVal() { return kthSmallest(size_ - 1); }
    
    // total cost to make every element equal to target t
    ll costToTarget(ll t) {
        ll cnt_LTE = countLTE((int)t);
        ll sum_LTE = sumLTE((int)t);
        ll cntGreater = size_ - cnt_LTE;
        ll sumGreater = totalSum - sum_LTE;
        return t * cnt_LTE - sum_LTE + sumGreater - t * cntGreater;
    }
    
    // total cost to make every element equal to the median
    ll costToMedian() {
        return costToTarget(median());
    }
};