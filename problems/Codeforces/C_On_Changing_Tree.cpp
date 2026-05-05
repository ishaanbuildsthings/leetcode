// SOLUTION 1, LAZY TAG SEG TREE
// #include <bits/stdc++.h>
// using namespace std;
// using ll = long long;
// int MOD = 1000000007;

// inline ll add(ll a, ll b) { return (a + b) % MOD; }
// inline ll sub(ll a, ll b) { return (a - b + MOD) % MOD; }
// inline ll mul(ll a, ll b) { return a * b % MOD; }

// // a node stores the sum of its elements, the sum of depths of its elements, and the size of the range
// struct Node {
//     ll tot;
//     ll width;
//     ll sumDepths;
// };

// // toRoot means a NORMALIZED value, e.g. how much would we apply to something at the root of the tree (depth=0)
// // step is how much we lose by falling down a layer
// // active just means the tag is there or not
// struct Tag {
//     ll toRoot = 0;
//     ll step = 0;
//     bool active = false;
// };

// struct Seg {
//     int n;
//     vector<Node> tree;
//     vector<Tag> lazy;
//     vector<int> depths;
//     Seg(const vector<int>& A, const vector<int>& _depths) {
//         depths = _depths;
//         n = A.size();
//         tree.resize(4 * n);
//         lazy.resize(4 * n);
//         _build(1, 0, n - 1);
//     }
//     Node _combine(Node& a, Node& b) {
//         return {add(a.tot, b.tot), a.width + b.width, a.sumDepths + b.sumDepths};
//     }
//     void _pull(int nodeI) {
//         Node& left = tree[2 * nodeI];
//         Node& right = tree[2 * nodeI + 1];
//         tree[nodeI] = _combine(left, right);
//     }
//     void _build(int nodeI, int tl, int tr) {
//         if (tl == tr) {
//             lazy[nodeI] = {0, 0, false};
//             tree[nodeI] = {0, 1, depths[tl]};
//             return;
//         }
//         int tm = (tl + tr) / 2;
//         _build(2 * nodeI, tl, tm);
//         _build(2 * nodeI + 1, tm + 1, tr);
//         _pull(nodeI);
//     }
//     Tag _compose(Tag& a, Tag& b) {
//         Tag out;
//         if (a.active) {
//             out.active = true;
//             out.toRoot = add(out.toRoot, a.toRoot);
//             out.step = add(out.step, a.step);
//         }
//         if (b.active) {
//             out.active = true;
//             out.toRoot = add(out.toRoot, b.toRoot);
//             out.step = add(out.step, b.step);
//         }
//         return out;
//     }
//     // push our lazy tags down and compose them
//     void _pushDownAndClear(int nodeI) {
//         if (!lazy[nodeI].active) return;
//         _applyAndCompose(2*nodeI,lazy[nodeI]);
//         _applyAndCompose(2*nodeI + 1,lazy[nodeI]);
//         lazy[nodeI] = Tag{};
//     }
//     // applies the tag to the value here, and composes with the existing lazy
//     void _applyAndCompose(int nodeI, Tag t) {
//         Node& node = tree[nodeI];
//         int gainFromConstants = mul(t.toRoot, node.width);
//         int lossFromDepths = mul(t.step, node.sumDepths);
//         node.tot = add(node.tot, gainFromConstants);
//         node.tot = sub(node.tot, lossFromDepths);
//         lazy[nodeI] = _compose(lazy[nodeI], t);
//     }
//     Node _pointQuery(int nodeI, int tl, int tr, int i) {
//         if (tl == tr) {
//             return tree[nodeI];
//         }
//         _pushDownAndClear(nodeI);
//         int tm = (tl + tr) / 2;
//         if (i <= tm) {
//             return _pointQuery(2 * nodeI, tl, tm, i);
//         }
//         return _pointQuery(2 * nodeI + 1, tm + 1, tr, i);
//     }
//     Node pointQuery(int i) {
//         return _pointQuery(1, 0, n - 1, i);
//     }
//     void _rangeUpdate(int nodeI, int tl, int tr, int ql, int qr, int toRoot, int step) {
//         // out of bounds, just stop
//         if (qr < tl || ql > tr) return;
//         // fully contained, put a tag
//         if (ql <= tl && qr >= tr) {
//             _applyAndCompose(nodeI, {toRoot, step, true});
//             return;
//         }
//         _pushDownAndClear(nodeI);
//         int tm = (tl + tr) / 2;
//         _rangeUpdate(2 * nodeI, tl, tm, ql, qr, toRoot, step);
//         _rangeUpdate(2 * nodeI + 1, tm + 1, tr, ql, qr, toRoot, step);
//         _pull(nodeI);
//     }
//     void rangeUpdate(int l, int r, int toRoot, int step) {
//         _rangeUpdate(1, 0, n - 1, l, r, toRoot, step);
//     }
// };



// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n; cin >> n;
    // vector<int> parents(n + 1);
    // vector<vector<int>> children(n + 1);
    // vector<int> depths(n + 1);
    // for (int node = 2; node <= n; node++) {
    //     int parent; cin >> parent;
    //     parents[node] = parent;
    //     children[parent].push_back(node);
    // }
//     // for (int node = 1; node <= n; node++) {
//     //     cout << "========" << endl;
//     //     cout << "Node: " << node << endl;
//     //     for (auto child : children[node]) {
//     //         cout << "child: " << child << endl;
//     //     }
//     // }

//     vector<int> flat(n + 1, 0); // our list of values, initially everything is 0
//     vector<int> tin(n + 1);
//     vector<int> tout(n + 1);
//     vector<int> depthsByVisitOrder; // kind of confusing but basically depths[visit order] -> node depth
//     int timer = 0;
//     auto dfs = [&](auto&& self, int node, int currDepth) -> void {
//         tin[node] = timer++;
//         depths[node] = currDepth;
//         depthsByVisitOrder.push_back(currDepth);
//         for (auto child : children[node]) {
//             self(self, child, currDepth + 1);
//         }
//         tout[node] = timer;
//     };
//     dfs(dfs, 1, 0);

//     Seg seg(flat, depthsByVisitOrder);

//     int q; cin >> q;
//     while (q--) {
//         int qtype; cin >> qtype;
//         if (qtype == 1) {
//             int v, x, k; cin >> v >> x >> k;
//             int l = tin[v];
//             int r = tout[v] - 1;
//             ll toRoot = add(x, (mul(depths[v], k)));
//             seg.rangeUpdate(l, r, toRoot, k);
//         } else {
//             int v; cin >> v;
//             cout << seg.pointQuery(tin[v]).tot << endl;
//         }
//     }
// }