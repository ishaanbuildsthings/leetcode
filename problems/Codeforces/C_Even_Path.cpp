#include <bits/stdc++.h>
using namespace std;

// #define LOCAL

#ifdef LOCAL
#define dbg(x) cerr << #x << " = " << (x) << endl
#define dbgv(v) do { cerr << #v << " = ["; for (auto& _x : v) cerr << _x << ", "; cerr << "]\n"; } while(0)
#define dbg2d(v) do { cerr << #v << ":\n"; for (auto& _r : v) { cerr << "  ["; for (auto& _x : _r) cerr << _x << ", "; cerr << "]\n"; } } while(0)
#else
#define dbg(x)
#define dbgv(v)
#define dbg2d(v)
#endif

struct Query {
    int ra, ca, rb, cb;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<int> R(n + 1); for (int i = 0; i < n; i++) cin >> R[i + 1];
    vector<int> C(n + 1); for (int i = 0; i < n; i++) cin >> C[i + 1];
    dbgv(C);
    vector<Query> Q(q);
    for (int i = 0; i < q; i++) {
        cin >> Q[i].ra >> Q[i].ca >> Q[i].rb >> Q[i].cb;
    }
    int N = n + 1; // actual sidelength
    
    // idea
    // if I can go up it means previous row is even
    // so anything where I go, as long as even, I can go up too
    // the moment I cannot go right, I could not go right anywhere

    // see how far right I can go and then how far up I can go

    vector<int> c1(N, -1);
    // gives the furthest right index we can go still being same parity
    auto goRight = [&](auto&& self, int ci) -> int {
        if (ci == N - 1) return ci;
        if (c1[ci] != -1) return c1[ci];
        if (C[ci+1] % 2 != C[ci] % 2) return ci;
        auto ans = self(self, ci + 1);
        c1[ci] = ans;
        return ans;
    };
    for (int ci = 0; ci < N; ci++) goRight(goRight, ci);

    vector<int> cache2(N, -1);
    auto goUp = [&](auto&& self, int ri) -> int {
        if (ri == 0) return ri;
        if (cache2[ri] != -1) return cache2[ri];
        if (R[ri-1] % 2 != R[ri] % 2) return ri;
        auto ans = self(self, ri - 1);
        cache2[ri] = ans;
        return ans;
    };
    for (int ri = 0; ri < N; ri++) goUp(goUp, ri);

    // for (int ci = 0; ci < N; ci++) {
    //     cout << "going right from ci=" << ci << " is: " << goRight(goRight, ci) << endl;
    // }
    // for (int ri = 0; ri < N; ri++) {
    //     cout << "going up from ri=" << ri << " is: " << goUp(goUp, ri) << endl;
    // }

    for (auto quer : Q) {
        vector<int> left = {quer.ra, quer.ca};
        vector<int> right = {quer.rb, quer.cb};
        if (quer.cb < quer.ca) {
            swap(left, right);
        }
        // cout << "queries... " << endl;
        // cout << "left: " << left[0] << " " << left[1] << endl;
        // cout << "right: " << right[0] << " " << right[1] << endl;

        auto toTheRight = goRight(goRight, left[1]);
        if (toTheRight < right[1]) {
            cout << "NO" << endl;
            continue;
        }
        auto lower = max(left[0], right[0]);
        auto toUp = goUp(goUp, lower);
        if (toUp > min(left[0], right[0])) {
            cout << "NO" << endl;
            continue;
        }
        cout << "YES" << endl;
    }

}