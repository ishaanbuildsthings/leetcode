#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct BitTrie {
    ll B;
    ll maxNodes;
    vector<array<int, 2>> children;
    int nextNode = 1;
    vector<int> passed;

    BitTrie(ll _b, ll inserts) {
        B = _b;
        maxNodes = B * (2 * inserts) + 1; // for root
        children.assign(maxNodes, {-1, -1});
        passed.resize(maxNodes, 0);
    }

    void add(ll x) {
        passed[0]++;
        ll idx = 0;
        for (ll b = B - 1; b >= 0; b--) {
            ll bit = (x >> b) & 1;
            if (children[idx][bit] == -1) {
                children[idx][bit] = nextNode++;
            }
            idx = children[idx][bit];
            passed[idx]++;
        }
    }

    void remove(ll x) {
        passed[0]--;
        ll idx = 0;
        for (ll b = B - 1; b >= 0; b--) {
            ll bit = (x >> b) & 1;
            idx = children[idx][bit];
            passed[idx]--;
        }
    }

    ll xorAgainst(ll x) {
        ll res = 0;
        ll idx = 0;
        for (ll b = B - 1; b >= 0; b--) {
            ll bit = (x >> b) & 1;
            ll want = bit ^ 1;
            if (children[idx][want] != -1 && passed[children[idx][want]]) {
                res ^= (1LL << b);
                idx = children[idx][want];
            } else {
                if (children[idx][bit] == -1) return 0;
                idx = children[idx][bit];
            }
        }
        return res;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<ll> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    BitTrie bt(42, n);

    vector<ll> pf;
    ll curr = 0;
    for (auto x : A) {
        curr ^= x;
        pf.push_back(curr);
    }
    
    ll res = *max_element(pf.begin(), pf.end());
    // for every suffix xor, consider it against all prefixes
    for (auto pfXor : pf) {
        bt.add(pfXor);
    }
    ll suffXor = 0;
    for (int i = n - 1; i >= 0; i--) {
        suffXor ^= A[i];
        bt.remove(pf[i]);
        res = max(res, bt.xorAgainst(suffXor));
    }
    
    // for every prefix xor, consider it against all suffixes
    suffXor = 0;
    vector<ll> suffs(n);
    for (int i = n - 1; i>= 0; i--) {
        suffXor ^= A[i];
        bt.add(suffXor);
        suffs[i] = suffXor;
    }
    ll pfXor = 0;
    for (int i = 0; i < n; i++) {
        pfXor ^= A[i];
        bt.remove(suffs[i]);
        res = max(res, bt.xorAgainst(pfXor));
    }
    res = max(res, *max_element(suffs.begin(), suffs.end()));
    res = max(res, *max_element(pf.begin(), pf.end()));

    cout << res;

}