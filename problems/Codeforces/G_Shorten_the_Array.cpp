#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct BitTrie {
    int bits;
    int  maxNodes; // 1 node per bit per inserted number
    vector<vector<int>> children; // children[nodeId][0 or 1] gives us the next id, or -1 if not set
    int nextNode; // our next available id
    vector<int> passed; // how many values have passed through this node in the trie

    BitTrie(int _bits, int _n) {
        bits = _bits;
        maxNodes = bits * _n + 1; // +1 for root!!! important
        children.resize(maxNodes, vector<int>(2, -1));
        passed.assign(maxNodes, 0);
        nextNode = 1; // implcitily make the root at 0
    }

    void add(int num) {
        int currId = 0;
        passed[0]++;
        for (int b = bits - 1; b >= 0; b--) {
            int bit = (num >> b) & 1;
            if (children[currId][bit] == -1) {
                children[currId][bit] = nextNode++;
            }
            currId = children[currId][bit];
            passed[currId]++;
        }
    }

    void remove(int num) {
        int currId = 0;
        passed[0]--;
        for (int b = bits - 1; b >= 0; b--) {
            int bit = (num >> b) & 1;
            currId = children[currId][bit];
            passed[currId]--;
        }
    }

    ll maxXorAgainst(int x) {
        if (passed[0] == 0) return 0; // no possible xor
        ll res = 0;
        int currId = 0;
        for (int b = bits - 1; b >= 0; b--) {
            int bit = (x >> b) & 1;
            int want = bit ^ 1;
            if (children[currId][want] != -1 && passed[children[currId][want]]) {
                res |= (1 << b);
                currId = children[currId][want];
            } else {
                currId = children[currId][bit];
            }
        }
        return res;
    }
};

void solve() {
    int n, k; cin >> n >> k;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    if (k == 0) {
        cout << 1 << '\n';
        return;
    }
    int res = INT_MAX;
    int l = 0;
    int r = 0;
    BitTrie bt(32, n);
    while (r < n) {
        int gain = A[r];
        // shrink while valid
        while (bt.maxXorAgainst(gain) >= k) {
            res = min(res, r - l + 1);
            int lost = A[l];
            bt.remove(lost);
            l++;
        }
        bt.add(gain);
        r++;
    }
    cout << (res == INT_MAX ? -1 : res) << '\n';
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        // cerr << "=======" << endl;
        solve();
    }
}