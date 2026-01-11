#include<bits/stdc++.h>
using namespace std;

struct SlidingMedianAndSum {
    multiset<int> low;
    multiset<int> high;
    long long totLow = 0;
    long long totHigh = 0;

    void add(int x) {
        if (!low.size()) {
            low.insert(x);
            totLow += x;
            return;
        }
        if (x <= lowMax()) {
            totLow += x;
            low.insert(x);
        } else {
            totHigh += x;
            high.insert(x);
        }
        rebalance();
    }

    void removeOne(int x) {
        if (x <= lowMax()) {
            auto lowIt = low.find(x);
            low.erase(lowIt);
            totLow -= x;
        } else {
            auto highIt = high.find(x);
            high.erase(highIt);
            totHigh -= x;
        }
        rebalance();
    }

    void rebalance() {
        // move high to low
        while (high.size() > low.size()) {
            auto it = high.begin();
            int v = *it;
            high.erase(it);
            totHigh -= v;
    
            low.insert(v);
            totLow += v;
        }

        // move low to high
        while (low.size() > high.size() + 1) {
            auto it = prev(low.end());
            int v = *it;
            low.erase(it);
            totLow -= v;

            high.insert(v);
            totHigh += v;
        }
    }

    int lowMax() const { return *prev(low.end()); }
    int highMin() const { return *high.begin(); }

    int median() {
        return lowMax();
    }

    long long costToMakeAllSame() {
        long long lowDesiredSize = lowMax() * low.size();
        long long lowCost = lowDesiredSize - totLow;
        long long highDesiredSize = lowMax() * high.size();
        long long highCost = totHigh - highDesiredSize;
        return lowCost + highCost;
    }

    int size() {
        return low.size() + high.size();
    }

    bool empty() {
        return size() == 0;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    SlidingMedianAndSum sm;
    for (int i = 0; i < k; i++) {
        sm.add(A[i]);
    }
    cout << sm.costToMakeAllSame() << " ";
    for (int r = k; r < n; r++) {
        sm.add(A[r]);
        sm.removeOne(A[r-k]);
        cout << sm.costToMakeAllSame() << " ";
    }
}
