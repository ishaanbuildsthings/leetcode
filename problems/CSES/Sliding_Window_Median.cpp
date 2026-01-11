#include <bits/stdc++.h>
using namespace std;

struct SlidingMedian {
    multiset<int> low;
    multiset<int> high;


    int lowMax() const { return *prev(low.end()); }
    int highMin() const { return *high.begin(); }

    void add(int x) {
        if (!low.size()) {
            low.insert(x);
            return;
        }
        if (x <= lowMax()) {
            low.insert(x);
        } else {
            high.insert(x);
        }
        rebalance();
    };

    void removeOne(int x) {
        if (x <= lowMax()) {
            auto itLow = low.find(x);
            low.erase(itLow);
        } else {
            auto itHigh = high.find(x);
            high.erase(itHigh);
        }
        rebalance();
    }

    int median() {
        return lowMax();
    }

    void rebalance() {
        while ((int)low.size() > (int)high.size() + 1) {
            auto it = prev(low.end());
            high.insert(*it);
            low.erase(it);
        }
        while ((int)low.size() < (int)high.size()) {
            auto it = high.begin();
            low.insert(*it);
            high.erase(it);
        }
    }
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);

    int n, k; cin >> n >> k;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];

    SlidingMedian sm;
    for (int i = 0; i < k; i++) {
        sm.add(A[i]);
    }
    cout << sm.median() << " ";
    for (int r = k; r < n; r++) {
        sm.add(A[r]);
        sm.removeOne(A[r-k]);
        cout << sm.median() << " ";
    }
}