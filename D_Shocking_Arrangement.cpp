#include <bits/stdc++.h>
using namespace std;

struct OrderedMultiSet {
    using ll = long long;

    vector<ll> values;
    vector<ll> bit;
    int n = 0;

    OrderedMultiSet() = default;

    explicit OrderedMultiSet(vector<ll> allValues) {
        sort(allValues.begin(), allValues.end());
        allValues.erase(unique(allValues.begin(), allValues.end()), allValues.end());
        values = std::move(allValues);
        n = (int)values.size();
        bit.assign(n + 1, 0);
    }

    int indexOf(ll x) const {
        auto it = lower_bound(values.begin(), values.end(), x);
        if (it == values.end() || *it != x) throw invalid_argument("value not in universe");
        return (int)(it - values.begin()) + 1;
    }

    int lowerIndex(ll x) const {
        return (int)(lower_bound(values.begin(), values.end(), x) - values.begin()) + 1;
    }

    int upperIndex(ll x) const {
        return (int)(upper_bound(values.begin(), values.end(), x) - values.begin()) + 1;
    }

    ll prefixCountByIndex(int i1Based) const {
        ll res = 0;
        for (int i = i1Based; i > 0; i -= i & -i) res += bit[i];
        return res;
    }

    ll size() const {
        return prefixCountByIndex(n);
    }

    ll countAtIndex(int i1Based) const {
        return prefixCountByIndex(i1Based) - prefixCountByIndex(i1Based - 1);
    }

    void add(ll x, ll cnt = 1) {
        if (cnt <= 0) return;
        int i = indexOf(x);
        for (; i <= n; i += i & -i) bit[i] += cnt;
    }

    void remove(ll x, ll cnt = 1) {
        if (cnt <= 0) return;
        if (count(x) < cnt) throw out_of_range("remove more than present");
        int i = indexOf(x);
        for (; i <= n; i += i & -i) bit[i] -= cnt;
    }

    ll count(ll x) const {
        int i = indexOf(x);
        return countAtIndex(i);
    }

    bool contains(ll x) const {
        return count(x) > 0;
    }

    ll kthSmallest(ll k) const {
        ll total = size();
        if (k < 0 || k >= total) throw out_of_range("k out of range");
        int idx = 0;
        ll cur = 0;
        int step = 1;
        while ((step << 1) <= n) step <<= 1;
        for (; step > 0; step >>= 1) {
            int nxt = idx + step;
            if (nxt <= n && cur + bit[nxt] <= k) {
                idx = nxt;
                cur += bit[nxt];
            }
        }
        return values[idx];
    }

    ll kthLargest(ll k) const {
        ll total = size();
        if (k < 0 || k >= total) throw out_of_range("k out of range");
        return kthSmallest(total - 1 - k);
    }

    ll minValue() const {
        if (size() == 0) throw out_of_range("empty");
        return kthSmallest(0);
    }

    ll maxValue() const {
        if (size() == 0) throw out_of_range("empty");
        return kthSmallest(size() - 1);
    }

    ll countLessThan(ll x) const {
        int i = lowerIndex(x);
        return prefixCountByIndex(i - 1);
    }

    ll countLessThanOrEqual(ll x) const {
        int i = upperIndex(x);
        return prefixCountByIndex(i - 1);
    }

    ll countGreaterThanOrEqual(ll x) const {
        return size() - countLessThan(x);
    }

    ll countGreaterThan(ll x) const {
        return size() - countLessThanOrEqual(x);
    }

    ll countInRangeInclusive(ll l, ll r) const {
        if (l > r) return 0;
        return countLessThanOrEqual(r) - countLessThan(l);
    }

    ll largestLessThan(ll x) const {
        int i = lowerIndex(x) - 1;
        if (i <= 0) throw out_of_range("no value < x");
        ll cnt = prefixCountByIndex(i);
        if (cnt == 0) throw out_of_range("no value < x");
        return kthSmallest(cnt - 1);
    }

    ll largestLessThanOrEqual(ll x) const {
        int i = upperIndex(x) - 1;
        if (i <= 0) throw out_of_range("no value <= x");
        ll cnt = prefixCountByIndex(i);
        if (cnt == 0) throw out_of_range("no value <= x");
        return kthSmallest(cnt - 1);
    }

    ll smallestGreaterThanOrEqual(ll x) const {
        int i = lowerIndex(x);
        ll before = prefixCountByIndex(i - 1);
        if (before >= size()) throw out_of_range("no value >= x");
        return kthSmallest(before);
    }

    ll smallestGreaterThan(ll x) const {
        int i = upperIndex(x);
        ll before = prefixCountByIndex(i - 1);
        if (before >= size()) throw out_of_range("no value > x");
        return kthSmallest(before);
    }
};

void solve() {
    // cout << "==============" << endl;
    int n; cin >> n;
    vector<long long> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    // for (auto x : A) cout << x << " ";
    // cout << endl;
    int mx = *max_element(A.begin(), A.end());
    int mn = *min_element(A.begin(), A.end());
    if (mx == 0) {
        cout << "No" << endl;
        return;
    }
    int cantGoTo = mx - mn;
    vector<int> res;
    int zeroes = 0;
    // OrderedMultiSet pos(A);
    // OrderedMultiSet neg(A);
    OrderedMultiSet others(A);
    for (auto x : A) {
        if (x == 0) zeroes += 1;
        if (x < 0 || x > 0) others.add(x);
        // if (x > 0) pos.insert(x);
        // if (x < 0) neg.insert(x);
    }
    // keep placing the maximum element that we can place 
    int pf = 0;
    for (int i = 0; i < n; i++) {
        if (zeroes > 0) {
            res.push_back(0);
            zeroes--;
            continue;
        }
        int highestCanPlace = cantGoTo - pf - 1;
        int largest = others.largestLessThanOrEqual(highestCanPlace);
        res.push_back(largest);
        others.remove(largest);
        pf += largest;
        if (pf < 0) pf = 0;
    }
    cout << "Yes" << endl;
    for (auto x : res) cout << x << " ";
    cout << endl;

}

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}