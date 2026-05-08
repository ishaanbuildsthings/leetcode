
#include <bits/stdc++.h>
using namespace std;
 
struct SparseSegTreeOnValues {
  struct Node {
    int tl, tr, cnt = 0;
    Node *l, *r;
    Node(int tl, int tr): tl(tl), tr(tr), l(nullptr), r(nullptr) {}
  };
  Node root;
 
  SparseSegTreeOnValues(int low, int high) : root(low, high) {}
 
  int countQuery(int ql, int qr, Node* node) {
    if (ql <= node->tl && node->tr <= qr) return node->cnt;
    if (qr < node->tl || node->tr < ql) return 0;
 
    int res = 0;
    if (node->l) res += countQuery(ql, qr, node->l);
    if (node->r) res += countQuery(ql, qr, node->r);
    return res;
  }
 
  void updateVal(int val, int diff, Node* node) {
    if (val < node->tl || val > node->tr) return;
 
    if (node->tl == node->tr) {
      node->cnt += diff;
      return;
    }
 
    int mid = (node->tl + node->tr) >> 1;
    if (val <= mid) {
      if (!node->l) node->l = new Node(node->tl, mid);
      updateVal(val, diff, node->l);
    } else {
      if (!node->r) node->r = new Node(mid + 1, node->tr);
      updateVal(val, diff, node->r);
    }
 
    node->cnt = (node->l ? node->l->cnt : 0) + (node->r ? node->r->cnt : 0);
  }
};
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
 
  int n, q;
  cin >> n >> q;
 
  SparseSegTreeOnValues seg(0, 1'000'000'000);
  vector<int> salaries(n + 1);
 
  for (int i = 0; i < n; i++) {
    int v; cin >> v;
    seg.updateVal(v, 1, &seg.root);
    salaries[i + 1] = v;
  }
 
  while (q--) {
    string op; cin >> op;
    if (op == "!") {
      int k, x; cin >> k >> x;
      int oldSalary = salaries[k];
      salaries[k] = x;
      seg.updateVal(oldSalary, -1, &seg.root);
      seg.updateVal(x, +1, &seg.root);
    } else {
      int a, b; cin >> a >> b;
      cout << seg.countQuery(a, b, &seg.root) << "\n";
    }
  }
  return 0;
}