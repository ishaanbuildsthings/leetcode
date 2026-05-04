#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Fenwick {
    int n;
    vector<ll> bit;

    Fenwick(int _n) : n(_n), bit(_n + 1, 0) {}

    // add v to position i (0-indexed)
    void add(int i, ll v) {
        for (i++; i <= n; i += i & -i) bit[i] += v;
    }

    // sum of positions 0..i (0-indexed, inclusive)
    ll prefSum(int i) {
        if (i < 0) return 0;
        ll s = 0;
        for (i++; i > 0; i -= i & -i) s += bit[i];
        return s;
    }

    // sum of positions l..r (0-indexed, inclusive)
    ll rangeSum(int l, int r) {
        if (l > r) return 0;
        return prefSum(r) - prefSum(l - 1);
    }
};

struct Query {
    int j; // this query is for 0...j
    int R; // with values 0...R
    int qid; // original query id
    int sign;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<pair<int,int>> ranges; // holds (l, r), ...
    vector<int> numToIdx(n + 1, -1); // maps number -> where it occurs
    for (int i = 0; i < n; i++) {
        numToIdx[A[i]] = i;
    }
    for (int num = 1; num <= n; num++) {
        for (int dupe = num; dupe <= n; dupe += num) {
            int l = numToIdx[num];
            int r = numToIdx[dupe];
            ranges.push_back({min(l, r), max(l, r)});
        }
    }

    sort(ranges.begin(), ranges.end(), [](const pair<int,int>& A, const pair<int,int>& B) {
        return A.first < B.first;
    });

    
    vector<int> Rs(ranges.size());
    for (int i = 0; i < ranges.size(); i++) {
        int r = ranges[i].second;
        Rs[i] = r;
    }

    vector<Query> events;
    events.reserve(2 * m);

    Fenwick fw(n);

    for (int qi = 0; qi < m; qi++) {
        int L, R; cin >> L >> R; L--; R--;
        // binary search, smallest index in `ranges` where the i in that range is >= L
        int leftIdx = lower_bound(ranges.begin(), ranges.end(), make_pair(L, INT_MIN),
        [](const pair<int,int>& a, const pair<int,int>& b) {
            return a.first < b.first;
        }) - ranges.begin();
        // largest index in `ranges` where the L in that range is <= R
        int rightIdx = upper_bound(ranges.begin(), ranges.end(), make_pair(R, INT_MAX),
                [](const pair<int,int>& a, const pair<int,int>& b) {
                    return a.first < b.first;
                }) - ranges.begin() - 1;
        

        // okay so now we have indices leftIdx...rightIdx in our ranges tuple array
        // in this range, we want to query how many values are <= R
        events.push_back({rightIdx, R, qi, +1});
        if (leftIdx > 0) {
            events.push_back({leftIdx - 1, R, qi, -1});
        }       
    }


    // map r -> all events
    vector<vector<Query>> eventsByJ(Rs.size());
    for (auto& e : events) {
        eventsByJ[e.j].push_back(e);
    }

    // sweep on R one at a time, adding that to the fenwick tree, then do the query to update the result
    vector<ll> result(m, 0);
    for (int j = 0; j < (int)Rs.size(); j++) {
        fw.add(Rs[j], 1);
        for (auto& e : eventsByJ[j]) {
            result[e.qid] += (ll)e.sign * fw.prefSum(e.R);
        }
    }

    string out;
    out.reserve(m * 12);
    for (int i = 0; i < m; i++) {
        out += to_string(result[i]);
        out += '\n';
    }
    cout << out;
}