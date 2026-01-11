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
    }

    int lowMax() const { return *prev(low.end()); }
    int highMin() const { return *high.begin(); }

    int median() {
        return lowMax();
    }

    long long costToMakeAllSame() {
        long long lowDesiredSize = lowMax() * low.size();
        cerr << "cost 1" << endl;
        long long lowCost = lowDesiredSize - totLow;
        long long highDesiredSize = highMin() * high.size();
        cerr << "cost 2" << endl;
        long long highCost = totHigh - highDesiredSize;
        cerr << "returning" << endl;
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
    cerr << "made it after filling sm" << endl;
    cout << sm.costToMakeAllSame() << " ";
    cerr << "first log" << endl;
    for (int r = k; r < n; r++) {
        cerr << "r is: " << r << " ";
        sm.add(A[r]);
        cerr << "added " << endl;
        sm.removeOne(A[r-k]);
        cerr << "removed " << endl;
        cerr << sm.costToMakeAllSame() << " ";
        cerr << "logged" << endl;
    }
}
