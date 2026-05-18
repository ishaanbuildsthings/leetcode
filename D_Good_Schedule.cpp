#include <bits/stdc++.h>
using namespace std;
using ll = long long;

void solve() {
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<int> B(n); for (int i = 0; i < n; i++) cin >> B[i];
    // cerr << "=============" << endl;
    // for (auto x : A) cerr << x << " ";
    // cerr << endl;
    // for (auto y : B) cerr << y << " ";
    // cerr << endl;

    // cerr << "making "

    vector<vector<int>> numToPosA(n + 1);
    vector<vector<int>> numToPosB(n + 1);
    for (int i = 0; i < n; i++) {
        int a = A[i];
        numToPosA[a].push_back(i);
        int b = B[i];
        numToPosB[b].push_back(i);
    }

    // cerr << "num to pos generated" << endl;

    // gives us the earliest index in A where a number appears, and B, or n if it does not appear
    auto earliestOccs = [&](int left, int num) -> pair<int,int> {
        // cerr << "earliest occs called on left=" << left << " num=" << num << endl;
        // search A
        auto& bucket = numToPosA[num];
        int l = 0;
        int r = bucket.size() - 1;
        int resA = -1;

        // cerr << "searching 1..." << endl;
        while (l <= r) {
            int m = (l + r) / 2;
            int idx = bucket[m];
            if (idx >= left) {
                resA = m;
                r = m - 1;
            } else {
                l = m + 1;
            }
        }

        // cerr << "searching 2..." << endl;

        // search B
        auto& bucket2 = numToPosB[num];
        l = 0;
        r = bucket2.size() - 1;
        int resB = -1;
        while (l <= r) {
            int m = (l + r) / 2;
            int idx = bucket2[m];
            if (idx >= left) {
                resB = m;
                r = m - 1;
            } else {
                l = m + 1;
            }
        }

        if (resA == -1) {
            resA = n;
        }
        if (resB == -1) {
            resB = n;
        }
        if (resA != n) {
            resA = bucket[resA];
        }
        if (resB != n) {
            resB = bucket2[resB];
        }
        // cerr << "returning resA=" << resA << " resB=" << resB << endl;
        return {resA, resB};
    };

    // for each starting index we find the first two 1s
    // now we do dp from those ones, what is the earliest 2s after it? if they match we can jump

    vector<int> cache(n + 1, -1);
    // int cnt = 0;
    // gives us furthest right we can go, assuming A[i] = B[i]
    auto dp = [&](auto&& self, int i) -> int {
        // cerr << "dp called on i=" << i << endl;
        // cnt++;
        // if (cnt > 10) return 0;
        if (i == n) {
            return i - 1;
        }
        if (i == n - 1) {
            return i;
        }
        if (cache[i] != -1) {
            return cache[i];
        }
        int num = A[i];
        int nextNum = num + 1;
        auto [earlyA, earlyB] = earliestOccs(i, nextNum);
        // if they are equal, we can jump to them
        if (earlyA == earlyB) {
            int ans = self(self, earlyA);
            cache[i] = ans;
            return ans;
        }
        // if they are different, we jump up to the smaller one
        int mn = min(earlyA, earlyB);
        cache[i] = mn - 1;
        return mn - 1;
    };

    ll out = 0;
    for (int i = 0; i < n; i++) {
        // cerr << "==========" << endl;
        // if these are both 1, we start here
        int a = A[i];
        int b = B[i];
        if (a == 1 && b == 1) {
            // cerr << "a and b are both 1, we start here" << endl;
            int right = dp(dp, i);
            int width = right - i + 1;
            out += width;
            continue;
        }

        // if only one is 1, we fail
        else if (a == 1 || b == 1) {
            // cerr << "only one of a or b is a 1, we fail immediately" << endl;
            continue;
        }

        // if neither is 1, find the ones
        auto [earlyA, earlyB] = earliestOccs(i, 1);
        // cerr << "we found the ones at earlyA=" << earlyA << " earlyB=" << earlyB << endl;
        // if those ones are in equal spots, we can jump
        if (earlyA == earlyB) {
            int right = dp(dp, earlyA);
            int width = right - i + 1;
            out += width;
            continue;
        }
        // but if not equal, we go up to before them
        int mn = min(earlyA, earlyB);
        int right = mn - 1;
        int width = right - i + 1;
        out += width;
    }

    // cerr << "test terminated" << endl;

    // cerr << "OUT: " << endl;
    cout << out << '\n';
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    
    int t; cin >> t;
    while (t--) {
        solve();
    }
}