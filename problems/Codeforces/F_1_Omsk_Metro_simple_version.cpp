// #include <bits/stdc++.h>
// using namespace std;

// int main() {
//   ios::sync_with_stdio(false);
//   cin.tie(nullptr);
//   int T; cin >> T;

//   while (T--) {

//     int n; cin >> n;
//     int LOG = 32;
//     vector<vector<int>> up(LOG, vector<int>(n + 1));
//     vector<vector<int>> mx(LOG, vector<int>(n + 1));
//     vector<vector<int>> mn(LOG, vector<int>(n + 1));
//     vector<int> depths(n + 1);
//     depths[1] = 0;
//     for (int k = 0; k < LOG; k++) {
//       up[k][1] = 1;
//       mx[k][1] = 1;
//       mn[k][1] = 1;
//     }

//     function<void(int,int,int)> add = [&](int node, int parent, int val) {
//       depths[node] = 1 + depths[parent];
//       up[0][node] = parent;
//       mx[0][node] = max(val, mx[0][parent]);
//       mn[0][node] = min(val, mn[0][parent]);
//       for (int k = 1; k < LOG; k++) {
//         int mid = up[k-1][node];
//         up[k][node] = up[k-1][mid];
//         mx[k][node] = max(mx[k-1][node], mx[k-1][mid]);
//         mn[k][node] = min(mn[k-1][node], mn[k-1][mid]);
//       }
//     };

//     function<pair<int,int>(int,int)> data = [&](int a, int b) {
//       if (depths[a] < depths[b]) swap(a, b);
//       int mnHere = 1000000000;
//       int mxHere = -1000000000;
//       int diff = depths[a] - depths[b];
//       for (int k = 0; k < LOG; k++) {
//         if (diff >> k & 1) {
//           mnHere = min(mnHere, mn[k][a]);
//           mxHere = max(mxHere, mx[k][a]);
//           a = up[k][a];
//         }

//       }
//       if (a == b) return make_pair(mnHere, mxHere);
//       for (int k = LOG - 1; k >= 0; k--) {
//         if (up[k][a] != up[k][b]) {
//           mnHere = min(mnHere, min(mn[k][a], mn[k][b]));
//           mxHere = max(mxHere, max(mx[k][a], mx[k][b]));
//           a = up[k][a];
//           b = up[k][b];
//         }
//       }

//       return make_pair(mnHere, mxHere);
//     };


//     for (int i = 0; i < n; i++) {
//       string s; cin >> s;
//       if (s == "+") {
//         int parent, diff; cin >> parent >> diff;
//         int node = i + 2;
//         add(node, parent, diff);
//         continue;
//       }
//       int a, b, target; cin >> a >> b >> target;
//       auto [small, big] = data(a, b);
//       cout << ((small <= target && target <= big) ? "YES" : "NO") << endl;
//     }
//   }
// }

#include <bits/stdc++.h>
using namespace std;

using ll = long long;

struct S { ll sum, pref, suff, best, prefMin, suffMin, bestMin; };
static const ll INF = (ll)4e18;

S make_val(ll v) { return {v, v, v, v, v, v, v}; }

S combine(const S &a, const S &b) {
  S c;
  c.sum = a.sum + b.sum;
  c.pref = max(a.pref, a.sum + b.pref);
  c.suff = max(b.suff, a.suff + b.sum);
  c.best = max({a.best, b.best, a.suff + b.pref});
  c.prefMin = min(a.prefMin, a.sum + b.prefMin);
  c.suffMin = min(b.suffMin, a.suffMin + b.sum);
  c.bestMin = min({a.bestMin, b.bestMin, a.suffMin + b.prefMin});
  return c;
}

S revS(const S &x) {
  S r = x;
  swap(r.pref, r.suff);
  swap(r.prefMin, r.suffMin);
  return r;
}

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);

  int T;
  cin >> T;

  while (T--) {
    int n;
    cin >> n;
    int LOG = 32, N = n + 2;

    vector<vector<int>> up(LOG, vector<int>(N, 0));
    vector<vector<S>> seg(LOG, vector<S>(N));
    vector<int> depth(N, -1);

    int cur = 1;
    depth[1] = 0;
    up[0][1] = 0;
    seg[0][1] = make_val(1);
    for (int k = 1; k < LOG; k++) {
      int mid = up[k - 1][1];
      if (mid) {
        up[k][1] = up[k - 1][mid];
        seg[k][1] = combine(seg[k - 1][1], seg[k - 1][mid]);
      } else {
        up[k][1] = 0;
        seg[k][1] = seg[k - 1][1];
      }
    }

    function<void(int, int, ll)> add = [&](int node, int parent, ll v) {
      depth[node] = depth[parent] + 1;
      up[0][node] = parent;
      seg[0][node] = make_val(v);
      for (int k = 1; k < LOG; k++) {
        int mid = up[k - 1][node];
        if (mid) {
          up[k][node] = up[k - 1][mid];
          seg[k][node] = combine(seg[k - 1][node], seg[k - 1][mid]);
        } else {
          up[k][node] = 0;
          seg[k][node] = seg[k - 1][node];
        }
      }
    };

    function<S(int, int)> data = [&](int a, int b) {
      if (depth[a] < depth[b]) swap(a, b);
      int diff = depth[a] - depth[b];

      vector<S> leftParts, rightParts;

      for (int k = 0; k < LOG; k++) if (diff >> k & 1) {
        leftParts.push_back(seg[k][a]);
        a = up[k][a];
      }

      if (a == b) {
        S res = seg[0][a];
        for (int i = (int)leftParts.size() - 1; i >= 0; --i) res = combine(leftParts[i], res);
        return res;
      }

      for (int k = LOG - 1; k >= 0; k--) if (up[k][a] != up[k][b]) {
        leftParts.push_back(seg[k][a]);
        rightParts.push_back(seg[k][b]);
        a = up[k][a];
        b = up[k][b];
      }

      int lca = up[0][a];
      leftParts.push_back(seg[0][a]);
      rightParts.push_back(seg[0][b]);

      S res = seg[0][lca];
      for (int i = (int)leftParts.size() - 1; i >= 0; --i) res = combine(leftParts[i], res);
      for (int i = (int)rightParts.size() - 1; i >= 0; --i) res = combine(res, revS(rightParts[i]));
      return res;
    };

    for (int i = 0; i < n; i++) {
      string s;
      cin >> s;
      if (s == "+") {
        int p; ll x;
        cin >> p >> x;
        cur++;
        add(cur, p, x);
      } else {
        int a, b; ll k;
        cin >> a >> b >> k;
        if (k == 0) {
          cout << "YES" << endl;
          continue;
        }
        S res = data(a, b);
        cout << ((res.bestMin <= k && k <= res.best) ? "YES" : "NO") << endl;
      }
    }
  }
}