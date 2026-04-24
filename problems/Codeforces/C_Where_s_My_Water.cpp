#include <bits/stdc++.h>
using namespace std;

#define LOCAL

#ifdef LOCAL
#define dbg(x) cerr << #x << " = " << (x) << endl
#define dbgv(v) do { cerr << #v << " = ["; for (auto& _x : v) cerr << _x << ", "; cerr << "]\n"; } while(0)
#define dbg2d(v) do { cerr << #v << ":\n"; for (auto& _r : v) { cerr << "  ["; for (auto& _x : _r) cerr << _x << ", "; cerr << "]\n"; } } while(0)
#else
#define dbg(x)
#define dbgv(v)
#define dbg2d(v)
#endif

void solve() {
    int n, h; cin >> n >> h;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];

    // ideas

    // try all pairs somehow do things in O(1)

    // define a cut point where everything to the left drains left everything to the right drains right

    // for each prefix, for each drain position, compute how much it drains, naive is O(n^3) but if we did that we could do it for a suffix too
    // and then take best with cuts

    // for each drain position, for each prefix, compute how much it can drain !!!

    vector<vector<long long>> pf(n, vector<long long>(n, 0)); // pf[drainPos][i] is the amount ot drains for ...i with that drain pos

    vector<long long> pfBest(n); // best of any amount with a drain for ...i region

    for (int i = 0; i < n; i++) {
        long long drained = h - arr[i];
        int peak = arr[i]; // max amount of dirt blocker
        // walk left
        // dbg(drained);
        for (int l = i - 1; l >= 0; l--) {
            peak = max(peak, arr[l]);
            drained += h - peak;
        }
        pf[i][i] = drained;
        pfBest[i] = max(pfBest[i], pf[i][i]);
        // walk right
        peak = arr[i];
        for (int r = i + 1; r < n; r++) {
            peak = max(peak, arr[r]);
            drained += h - peak;
            pf[i][r] = drained;
            pfBest[r] = max(pfBest[r], pf[i][r]);
        }
    }

    // dbgv(pfBest);

    // dbg2d(pf);

    vector<vector<long long>> sf(n, vector<long long>(n, 0));

    vector<long long> sfBest(n);

    for (int i = 0; i < n; i++) {
        long long drained = h - arr[i];
        int peak = arr[i];
        // walk right
        for (int r = i + 1; r < n; r++) {
            peak = max(peak, arr[r]);
            drained += h - peak;
        }
        peak = arr[i];
        sf[i][i] = drained;
        sfBest[i] = max(sfBest[i], sf[i][i]);
        // walk left
        for (int l = i - 1; l >= 0; l--) {
            peak = max(peak, arr[l]);
            drained += h - peak;
            sf[i][l] = drained;
            sfBest[l] = max(sfBest[l], sf[i][l]);
        }
    }

    // dbgv(sfBest);

    long long out = 0;
    for (int allLeft = 0; allLeft < n; allLeft++) {
        long long bestLeft = pfBest[allLeft];
        long long bestRight = (allLeft + 1) < n ? sfBest[allLeft + 1] : 0;
        out = max(out, bestLeft + bestRight);
    }

    cout << out << endl;
}

int main() {
    int t; cin >> t;
    while (t--) {
        solve();
    }
}