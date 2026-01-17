#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, k; cin >> n >> k;
    string s; cin >> s;
    int q; cin >> q;

    // for each subsequence, we need to know the index it ends at in the sequence

    vector<int> mx(n, -1); // precompute the max (worst) option to take for an index
    vector<vector<int>> nxt(n, vector<int>(k, n)); // nxt[i][letter] is the next occurrence of this letter, exclusive
    vector<int> early(k, n);
    for (int i = n - 1; i >= 0; i--) {
        char chr = s[i];
        int ord = chr - 'a';
        int mxHere = -1;
        for (int order = 0; order < k; order++) {
            mxHere = max(mxHere, early[order]);
            nxt[i][order] = early[order];
        }
        mx[i] = mxHere;
        early[ord] = i;
    }

    vector<int> first(k, 2 * n + 5);
    for (int i = 0; i < s.size(); i++) {
        char c = s[i];
        int ord = c - 'a';
        first[ord] = min(first[ord], i);
    }

    vector<int> worst(n); // worst[i] is the most number of ops to reach n
    worst[worst.size() - 1] = 0; // base case
    for (int i = n - 1; i >= 0; i--) {
        int furthest = mx[i];
        if (furthest == n) {
            worst[i] = 1;
        } else {
            worst[i] = 1 + worst[furthest];
        }
    }

    for (int i = 0; i < q; i++) {
        string t; cin >> t;
        // see what index we end at to deplete this 
        int idx = first[t[0] - 'a'];
        if (idx >= n) {
            cout << 0 << "\n";
            continue;
        }
        int jdx = 1;
        bool ZERO = false;
        while (jdx < t.size()) {
            int newIdx = nxt[idx][t[jdx] - 'a'];
            if (newIdx >= n) {
                ZERO = true;
                break;
            }
            idx = newIdx;
            jdx++;
        }
        if (ZERO || idx >= n) {
            cout << 0 << "\n";
            continue;
        }
        // Now we are at some index, greedily take the worst until we reach n
        cout << worst[idx] << "\n";
    }
}