#include<bits/stdc++.h>
using namespace std;
// #define LOCAL
// #ifdef LOCAL
#define dbg(x) cerr << #x << " = " << (x) << endl
#define dbgv(v) do { cerr << #v << " = ["; for (auto& _x : v) cerr << _x << ", "; cerr << "]\n"; } while(0)
#define dbg2d(v) do { cerr << #v << ":\n"; for (auto& _r : v) { cerr << "  ["; for (auto& _x : _r) cerr << _x << ", "; cerr << "]\n"; } } while(0)
#else
#define dbg(x)
#define dbgv(v)
#define dbg2d(v)
#endif
void solve() {
    int n; cin >> n;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];
    unordered_map<int,int> c;
    for (auto x : arr) c[x]++;
    // long long out = LLONG_MAX / 4;
    int currentMex = 0;
    while (c.count(currentMex)) currentMex++;

    unordered_map<int, long long> cache;

    // cost we have to pay given this current mex, to clear out remaining array
    auto dp = [&](auto&& self, int mex) -> long long {
        if (mex == 0) return 0;
        if (cache.find(mex) != cache.end()) {
            return cache[mex];
        }
        long long best = LLONG_MAX / 4;
        for (auto x : arr) {
            if (x >= mex) continue;
            int frq = c[x];
            long long paid = (long long)(frq - 1) * mex;
            long long nxt = self(self, x);
            long long score = paid + nxt + x;
            best = min(best, score);
        }
        cache[mex] = best;
        return best;
    };

    long long ans = dp(dp, currentMex);

    cout << ans << endl;
}
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}