// // Solution 1, TLE to constant factor, dnc dp with mo's trick + queues to store early and last positions of things
// // #include <bits/stdc++.h>
// // using namespace std;
// // using ll = long long;

// // inline int readInt() {
// //     int x = 0, c = getchar();
// //     while (c < '0') c = getchar();
// //     while (c >= '0') { x = x * 10 + c - '0'; c = getchar(); }
// //     return x;
// // }

// // int main() {
// //     int n = readInt(), k = readInt();
// //     vector<int> arr(n);
// //     for (int i = 0; i < n; i++) arr[i] = readInt();
// //     vector<ll> dp(n);
// //     vector<vector<int>> occsSeed(n + 1);
// //     ll totCost = 0;
// //     for (int i = 0; i < n; i++) {
// //         int v = arr[i];
// //         auto& bucket = occsSeed[v];
// //         int oldCost = bucket.size() > 0 ? (bucket[bucket.size() - 1] - bucket[0]) : 0; 
// //         bucket.push_back(i);
// //         int newCost = bucket[bucket.size() - 1] - bucket[0];
// //         totCost -= oldCost;
// //         totCost += newCost;
// //         dp[i] = totCost;
// //     }

// //     // globals
// //     vector<deque<int>> occs(n + 1);
// //     ll cost = 0;
// //     int s = 0, e = -1;
    
// //     auto addR = [&](int pos) {
// //         int v = arr[pos];
// //         int oldSpan = occs[v].empty() ? 0 : occs[v].back() - occs[v].front();
// //         occs[v].push_back(pos);
// //         int newSpan = occs[v].back() - occs[v].front();
// //         cost += newSpan - oldSpan;
// //     };
// //     auto addL = [&](int pos) {
// //         int v = arr[pos];
// //         int oldSpan = occs[v].empty() ? 0 : occs[v].back() - occs[v].front();
// //         occs[v].push_front(pos);
// //         int newSpan = occs[v].back() - occs[v].front();
// //         cost += newSpan - oldSpan;
// //     };
// //     auto remR = [&](int pos) {
// //         int v = arr[pos];
// //         int oldSpan = occs[v].back() - occs[v].front();
// //         occs[v].pop_back();
// //         int newSpan = occs[v].empty() ? 0 : occs[v].back() - occs[v].front();
// //         cost += newSpan - oldSpan;
// //     };
// //     auto remL = [&](int pos) {
// //         int v = arr[pos];
// //         int oldSpan = occs[v].back() - occs[v].front();
// //         occs[v].pop_front();
// //         int newSpan = occs[v].empty() ? 0 : occs[v].back() - occs[v].front();
// //         cost += newSpan - oldSpan;
// //     };
// //     auto val = [&](int l, int r) -> ll {
// //         while (s > l) addL(--s);
// //         while (e < r) addR(++e);
// //         while (s < l) remL(s++);
// //         while (e > r) remR(e--);
// //         return cost;
// //     };

// //     vector<ll> ndp(n + 1);
// //     for (int p = 2; p <= k; p++) {
// //         auto solve = [&](auto&& self, int fillL, int fillR, int leftJ, int rightJ) -> void {
// //             if (fillL > fillR) return;
// //             int mid = fillL + (fillR - fillL) / 2;
// //             ll best = LLONG_MAX;
// //             int bestJ = -1;
// //             for (int j = leftJ; j <= min(mid, rightJ); j++) {
// //                 ll scoreHere = val(j, mid);
// //                 ll scoreBefore = j > 0 ? dp[j - 1] : 0;
// //                 ll totScore = scoreHere + scoreBefore;
// //                 if (totScore < best) {
// //                     best = totScore;
// //                     bestJ = j;
// //                 }
// //             }
// //             ndp[mid] = best;
// //             self(self, fillL, mid - 1, leftJ, bestJ);
// //             self(self, mid + 1, fillR, bestJ, rightJ);
// //         };
// //         solve(solve, 0, n - 1, 0, n - 1);
// //         swap(dp, ndp);
// //     }
// //     cout << dp[n - 1] << '\n';
// // }



// // Solution 2, dnc dp but we don't use queues, we precompute prv/nxt pointers for things giving array access which is fastor constant
// // #include <bits/stdc++.h>
// // using namespace std;
// // using ll = long long;

// // inline int readInt() {
// //     int x = 0, c = getchar();
// //     while (c < '0') c = getchar();
// //     while (c >= '0') { x = x * 10 + c - '0'; c = getchar(); }
// //     return x;
// // }

// // int main() {
// //     int n = readInt(), k = readInt();
// //     vector<int> arr(n);
// //     for (int i = 0; i < n; i++) arr[i] = readInt();

// //     // precompute prev/next occurrence of same value
// //     vector<int> prv(n, -1), nxt(n, n);
// //     {
// //         vector<int> last(n + 1, -1);
// //         for (int i = 0; i < n; i++) {
// //             prv[i] = last[arr[i]];
// //             last[arr[i]] = i;
// //         }
// //         fill(last.begin(), last.end(), n);
// //         for (int i = n - 1; i >= 0; i--) {
// //             nxt[i] = last[arr[i]];
// //             last[arr[i]] = i;
// //         }
// //     }

// //     // seed dp for 1 partition
// //     vector<ll> dp(n);
// //     {
// //         vector<int> cnt(n + 1, 0), lo(n + 1), hi(n + 1);
// //         ll tot = 0;
// //         for (int i = 0; i < n; i++) {
// //             int v = arr[i];
// //             int oldSpan = cnt[v] ? hi[v] - lo[v] : 0;
// //             if (!cnt[v]) lo[v] = i;
// //             hi[v] = i;
// //             cnt[v]++;
// //             tot += hi[v] - lo[v] - oldSpan;
// //             dp[i] = tot;
// //         }
// //     }

// //     vector<int> cnt(n + 1, 0), lo(n + 1, 0), hi(n + 1, 0);
// //     ll cost = 0;
// //     int s = 0, e = -1;

// //     auto addR = [&](int pos) {
// //         int v = arr[pos];
// //         if (cnt[v]) {
// //             cost += pos - hi[v];
// //             hi[v] = pos;
// //         } else {
// //             lo[v] = hi[v] = pos;
// //         }
// //         cnt[v]++;
// //     };
// //     auto addL = [&](int pos) {
// //         int v = arr[pos];
// //         if (cnt[v]) {
// //             cost += lo[v] - pos;
// //             lo[v] = pos;
// //         } else {
// //             lo[v] = hi[v] = pos;
// //         }
// //         cnt[v]++;
// //     };
// //     auto remR = [&](int pos) {
// //         int v = arr[pos];
// //         cnt[v]--;
// //         if (cnt[v]) {
// //             cost -= pos - prv[pos];
// //             hi[v] = prv[pos];
// //         }
// //     };
// //     auto remL = [&](int pos) {
// //         int v = arr[pos];
// //         cnt[v]--;
// //         if (cnt[v]) {
// //             cost -= nxt[pos] - pos;
// //             lo[v] = nxt[pos];
// //         }
// //     };
// //     auto val = [&](int l, int r) -> ll {
// //         while (s > l) addL(--s);
// //         while (e < r) addR(++e);
// //         while (s < l) remL(s++);
// //         while (e > r) remR(e--);
// //         return cost;
// //     };

// //     vector<ll> ndp(n);
// //     for (int p = 2; p <= k; p++) {
// //         fill(ndp.begin(), ndp.end(), LLONG_MAX);
// //         fill(cnt.begin(), cnt.end(), 0);
// //         cost = 0; s = 0; e = -1;
// //         auto solve = [&](auto&& self, int fillL, int fillR, int leftJ, int rightJ) -> void {
// //             if (fillL > fillR) return;
// //             int mid = fillL + (fillR - fillL) / 2;
// //             ll best = LLONG_MAX;
// //             int bestJ = leftJ;
// //             for (int j = leftJ; j <= min(mid, rightJ); j++) {
// //                 ll scoreHere = val(j, mid);
// //                 ll scoreBefore = j > 0 ? dp[j - 1] : 0;
// //                 ll totScore = scoreHere + scoreBefore;
// //                 if (totScore < best) {
// //                     best = totScore;
// //                     bestJ = j;
// //                 }
// //             }
// //             ndp[mid] = best;
// //             self(self, fillL, mid - 1, leftJ, bestJ);
// //             self(self, mid + 1, fillR, bestJ, rightJ);
// //         };
// //         solve(solve, 0, n - 1, 0, n - 1);
// //         swap(dp, ndp);
// //     }
// //     cout << dp[n - 1] << '\n';
// // }


// Solution 3, seg tree dp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const ll INF = LLONG_MAX / 4;
struct SegTree {
    int n;
    vector<ll> tree, lazy;

    void build(vector<ll>& vals) {
        n = vals.size();
        tree.assign(4 * n, INF);
        lazy.assign(4 * n, 0);
        _build(1, 0, n - 1, vals);
    }
    void rangeAdd(int l, int r, ll val) {
        _rangeAdd(1, 0, n - 1, l, r, val);
    }
    ll queryMin(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }

private:
    void push(int v) {
        if (lazy[v]) {
            for (int c : {2*v, 2*v+1}) {
                tree[c] += lazy[v];
                lazy[c] += lazy[v];
            }
            lazy[v] = 0;
        }
    }
    void _build(int v, int tl, int tr, vector<ll>& vals) {
        if (tl == tr) { tree[v] = vals[tl]; return; }
        int tm = (tl + tr) / 2;
        _build(2*v, tl, tm, vals);
        _build(2*v+1, tm+1, tr, vals);
        tree[v] = min(tree[2*v], tree[2*v+1]);
    }
    void _rangeAdd(int v, int tl, int tr, int l, int r, ll val) {
        if (l > r || tl > r || tr < l) return;
        if (l <= tl && tr <= r) { tree[v] += val; lazy[v] += val; return; }
        push(v);
        int tm = (tl + tr) / 2;
        _rangeAdd(2*v, tl, tm, l, r, val);
        _rangeAdd(2*v+1, tm+1, tr, l, r, val);
        tree[v] = min(tree[2*v], tree[2*v+1]);
    }
    ll _query(int v, int tl, int tr, int l, int r) {
        if (l > r || tl > r || tr < l) return INF;
        if (l <= tl && tr <= r) return tree[v];
        push(v);
        int tm = (tl + tr) / 2;
        return min(_query(2*v, tl, tm, l, r), _query(2*v+1, tm+1, tr, l, r));
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];

    vector<ll> dp(n, LLONG_MAX / 4); // partition to size 1
    ll costSeed = 0;

    vector<int> lastSeed(n + 1, -1); // maps number -> last occurrence so far
    for (int i = 0; i < n; i++) {
        int v = arr[i];
        if (lastSeed[v] == -1) {
            lastSeed[v] = i;
            dp[i] = costSeed;
            continue;
        }
        int prev = lastSeed[v];
        int ndist = i - prev;
        costSeed += ndist;
        lastSeed[v] = i;
        dp[i] = costSeed;
    }

    vector<ll> ndp(n, LLONG_MAX / 4);

    SegTree st = SegTree();
    for (int p = 2; p <= k; p++) {
        st.build(dp);
        vector<int> last(n + 1, -1); // maps number -> last occurrence so far

        // the seg tree is going to store dp[i] + cost(i + 1, j)
        // so the cost to partition 0...i with p-1 partitions, and then some section after
        // so every time we add a j, we need to update things in the dp
        // initially we load the seg tree with just the old dp, and it is right, because j is basically like -1, we haven't introduced any elements yet


        for (int j = 0; j < n; j++) {
            int v = arr[j];
            int prevPos = last[v];
            // if there was a previous number, some new rightmost partitions get more expensive
            // this means we need to update some seg tree values
            // every seg tree index which is dp[i] + cost(i + 1, j) becomes more expensive if i+1...j has 2 occurrences of the number

            // 1 5 0 1 2 3 [0] (introducing a 0 at the end)
            // ^
            // this used to refer to the cost to partition ...0, PLUS some section [5 0 1 2 3]
            // but now it is more expensive since that section gained
            // we need to update 0...1, both the 1 and 5 are penalized since the cut after contains a 0

            if (prevPos != -1) {
                st.rangeAdd(0, prevPos - 1, j - prevPos);
            }
            
            last[v] = j;

            // If we cannot even fit 0...j into p partitions, just call it INF
            if (j + 1 > p) {
                ndp[j] = LLONG_MAX / 4;
            }

            // Our best answer is any of the previous dps since those dps are 0...i + cost(i + 1, j)
            if (j > 0) ndp[j] = st.queryMin(0, j - 1);
        }

        swap(dp, ndp);
    }

    cout << dp[n - 1] << endl;
}
