#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct BitTrie {
    int B;
    int maxNodes;
    vector<array<int, 2>> children;
    int nextNode = 1;
    vector<int> passed;

    BitTrie(int _b, int inserts) {
        B = _b;
        maxNodes = (B + 1) * inserts + 1;
        children.assign(maxNodes, {-1, -1});
        passed.assign(maxNodes, 0);
    }

    bool _alive(int nid) {
        return nid != -1 && passed[nid] > 0;
    }

    void add(ll x) {
        int idx = 0;
        passed[0]++;
        for (int b = B - 1; b >= 0; b--) {
            int bit = (x >> b) & 1;
            if (children[idx][bit] == -1) {
                children[idx][bit] = nextNode++;
            }
            idx = children[idx][bit];
            passed[idx]++;
        }
    }

    void remove(ll x) {
        int idx = 0;
        passed[0]--;
        for (int b = B - 1; b >= 0; b--) {
            int bit = (x >> b) & 1;
            idx = children[idx][bit];
            passed[idx]--;
        }
    }

    int size() { return passed[0]; }

    // max XOR of x against any number in the trie. -1 if empty.
    ll maxXor(ll x) {
        if (!size()) return -1;
        ll res = 0;
        int idx = 0;
        for (int b = B - 1; b >= 0; b--) {
            int bit = (x >> b) & 1;
            int want = bit ^ 1;
            if (_alive(children[idx][want])) {
                res |= (1LL << b);
                idx = children[idx][want];
            } else {
                idx = children[idx][bit];
            }
        }
        return res;
    }

    // min XOR of x against any number in the trie. -1 if empty.
    ll minXor(ll x) {
        if (!size()) return -1;
        ll res = 0;
        int idx = 0;
        for (int b = B - 1; b >= 0; b--) {
            int bit = (x >> b) & 1;
            // prefer same bit (XOR = 0)
            if (_alive(children[idx][bit])) {
                idx = children[idx][bit];
            } else {
                res |= (1LL << b);
                idx = children[idx][bit ^ 1];
            }
        }
        return res;
    }

    // kth smallest XOR of x against numbers in trie (1-indexed). -1 if k > size.
    ll kthSmallestXor(ll x, int k) {
        if (k <= 0 || k > size()) return -1;
        ll res = 0;
        int idx = 0;
        for (int b = B - 1; b >= 0; b--) {
            int bit = (x >> b) & 1;
            int sameCnt = _alive(children[idx][bit]) ? passed[children[idx][bit]] : 0;
            if (k <= sameCnt) {
                idx = children[idx][bit];
            } else {
                k -= sameCnt;
                res |= (1LL << b);
                idx = children[idx][bit ^ 1];
            }
        }
        return res;
    }

    // kth largest XOR of x against numbers in trie (1-indexed). -1 if k > size.
    ll kthLargestXor(ll x, int k) {
        if (k <= 0 || k > size()) return -1;
        ll res = 0;
        int idx = 0;
        for (int b = B - 1; b >= 0; b--) {
            int bit = (x >> b) & 1;
            int want = bit ^ 1;
            int wantCnt = _alive(children[idx][want]) ? passed[children[idx][want]] : 0;
            if (k <= wantCnt) {
                res |= (1LL << b);
                idx = children[idx][want];
            } else {
                k -= wantCnt;
                idx = children[idx][bit];
            }
        }
        return res;
    }

    // count of numbers y in trie where (x ^ y) >= threshold
    int countXorGTE(ll x, ll threshold) {
        if (!size()) return 0;
        int idx = 0;
        int res = 0;
        for (int b = B - 1; b >= 0; b--) {
            int vbit = (x >> b) & 1;
            int tbit = (threshold >> b) & 1;
            if (tbit == 0) {
                // opposite branch gives XOR=1, exceeds threshold at this bit
                int exceedChild = children[idx][vbit ^ 1];
                if (_alive(exceedChild)) res += passed[exceedChild];
                // continue down same branch (XOR=0, tie)
                int tieChild = children[idx][vbit];
                if (!_alive(tieChild)) return res;
                idx = tieChild;
            } else {
                // must get XOR=1 to keep up with threshold
                int needChild = children[idx][vbit ^ 1];
                if (!_alive(needChild)) return res;
                idx = needChild;
            }
        }
        res += passed[idx]; // exact match
        return res;
    }

    // count of numbers y in trie where (x ^ y) > threshold
    int countXorGT(ll x, ll threshold) {
        return countXorGTE(x, threshold + 1);
    }

    // count of numbers y in trie where (x ^ y) <= threshold
    int countXorLTE(ll x, ll threshold) {
        return size() - countXorGT(x, threshold);
    }

    // count of numbers y in trie where (x ^ y) < threshold
    int countXorLT(ll x, ll threshold) {
        return size() - countXorGTE(x, threshold);
    }

    // count of numbers y in trie where lo <= (x ^ y) <= hi
    int countXorInRange(ll x, ll lo, ll hi) {
        if (lo > hi) return 0;
        return countXorLTE(x, hi) - countXorLT(x, lo);
    }

    // max XOR of x, but only against numbers y where (x ^ y) >= threshold. -1 if none.
    ll maxXorGTE(ll x, ll threshold) {
        int cnt = countXorGTE(x, threshold);
        if (cnt == 0) return -1;
        return kthLargestXor(x, 1);
    }

    // min XOR of x, but only against numbers y where (x ^ y) >= threshold. -1 if none.
    ll minXorGTE(ll x, ll threshold) {
        int cnt = countXorGTE(x, threshold);
        if (cnt == 0) return -1;
        int rank = size() - cnt + 1; // smallest among those >= threshold
        return kthSmallestXor(x, rank);
    }
};


void solve() {
    int n; ll k; cin >> n >> k;
    vector<ll> A(n); for (int i = 0; i < n; i++) cin >> A[i];

    // do we have at least K subarrays with XORs <= x?
    auto canDoXorLte = [&](ll x) -> ll {
        ll subarrays = 0;
        int l = 0;
        int r = 0;
        BitTrie bt(34, n + 10);
        while (r < n) {
            int gained = A[r];
            if (bt.minXor(gained) > x) {
                bt.add(gained);
                r++;
                continue;
            }
            while (l != r && bt.minXor(gained) <= x) {
                int width = n - r;
                subarrays += width;
                int lost = A[l];
                bt.remove(lost);
                l++;
            }
            bt.add(gained);
            r++;
        }
        return subarrays >= k;
    };

    ll res = -1;
    ll l = 0;
    ll r = 10000000000;
    // binary search for the smallest value we have at least K subarrays for
    while (l <= r) {
        ll m = (l + r) / 2LL;
        // do we have at least K subarrays with XOR <= m?
        if (canDoXorLte(m)) {
            res = m;
            r = m - 1;
        } else {
            l = m + 1;
        }
    }
    cout << res << '\n';
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}