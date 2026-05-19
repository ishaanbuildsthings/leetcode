#include <bits/stdc++.h>
using namespace std;
using ll = long long;


// TEMPLATE FROM MY GITHUB: ishaanbuildsthings
// tested here: https://cses.fi/problemset/result/17227257/
struct MedianWindow {
    multiset<ll> lo, hi; // lo: smaller half, hi: larger half
    // Invariant: |lo| >= |hi|, |lo| - |hi| <= 1, every elem in lo <= every elem in hi
    ll loSum = 0, hiSum = 0;
    
    // maintain size invariants
    void _rebalance() {
        while ((ll)lo.size() > (ll)hi.size() + 1) {
            auto it = prev(lo.end());
            ll x = *it; lo.erase(it); loSum -= x;
            hi.insert(x); hiSum += x;
        }
        while (hi.size() > lo.size()) {
            auto it = hi.begin();
            ll x = *it; hi.erase(it); hiSum -= x;
            lo.insert(x); loSum += x;
        }
    }
    
    // insert a value
    void add(ll x) {
        if (lo.empty() || x <= *prev(lo.end())) {
            lo.insert(x); loSum += x;
        } else {
            hi.insert(x); hiSum += x;
        }
        _rebalance();
    }
    
    // remove one occurrence of x
    void remove(ll x) {
        auto it = lo.find(x);
        if (it != lo.end()) { lo.erase(it); loSum -= x; }
        else { it = hi.find(x); hi.erase(it); hiSum -= x; }
        _rebalance();
    }
    
    // total number of elements
    size_t size() const { return lo.size() + hi.size(); }
    
    // true if no elements
    bool empty() const { return size() == 0; }
    
    // current median (lower median for even-sized windows)
    ll median() const { return *prev(lo.end()); }
    
    // sum of all elements
    ll sum() const { return loSum + hiSum; }
    
    // sum of the smaller half
    ll lowerSum() const { return loSum; }
    
    // sum of the larger half
    ll upperSum() const { return hiSum; }
    
    // count of elements in the smaller half
    size_t lowerSize() const { return lo.size(); }
    
    // count of elements in the larger half
    size_t upperSize() const { return hi.size(); }
    
    // smallest element
    ll minVal() const { return *lo.begin(); }
    
    // largest element
    ll maxVal() const { return hi.empty() ? *prev(lo.end()) : *prev(hi.end()); }
    
    // total cost to make every element equal to the median
    ll costToMedian() const {
        ll m = median();
        return m * (ll)lo.size() - loSum + hiSum - m * (ll)hi.size();
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    MedianWindow window;
    int n, k; cin >> n >> k;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    for (int r = 0; r < k; r++) {
        window.add(A[r]);
    }
    cout << window.median() << " ";
    for (int r = k; r < n; r++) {
        window.add(A[r]);
        window.remove(A[r-k]);
        cout << window.median() << " ";
    }
}