/*
 * Fast lazy segment tree: range add, range assign, range sum.
 *
 * Construction:
 *   LazySeg<int> seg(n);              // n elements, all zero
 *   LazySeg<int> seg(A);              // from vector<int> A
 *   LazySeg<ll>  seg(A);              // from vector<ll>  A
 *
 * Methods (all ranges are 0-based, [l, r] inclusive):
 *   seg.rangeAdd(l, r, val);          // add val to every element in [l, r]
 *   seg.rangeAssign(l, r, val);       // set every element in [l, r] to val
 *   ll s = seg.rangeSum(l, r);        // sum of elements in [l, r]
 *
 * Example:
 *   vector<int> A = {2, 3, 1, 1, 5, 3};
 *   LazySeg<int> seg(A);
 *   seg.rangeAdd(1, 3, 2);            // A becomes {2, 5, 3, 3, 5, 3}
 *   seg.rangeSum(2, 4);               // returns 11
 *   seg.rangeAssign(1, 3, 5);         // A becomes {2, 5, 5, 5, 5, 3}
 *   seg.rangeSum(2, 4);               // returns 15
 */

 template <typename T>
 struct LazySeg {
     int n, size;
     vector<ll> sum;
     vector<ll> add;
     vector<ll> assign;
     vector<bool> hasAssign;
     vector<int> width;
 
     LazySeg(int n_) : n(n_) {
         size = 1;
         while (size < max(n, 1)) size <<= 1;
         sum.assign(2 * size, 0);
         add.assign(2 * size, 0);
         assign.assign(2 * size, 0);
         hasAssign.assign(2 * size, false);
         width.assign(2 * size, 0);
         for (int i = 0; i < n; i++) width[size + i] = 1;
         for (int i = size - 1; i >= 1; i--) width[i] = width[2*i] + width[2*i+1];
     }
 
     LazySeg(const vector<T>& A) : LazySeg((int)A.size()) {
         for (int i = 0; i < n; i++) sum[size + i] = A[i];
         for (int i = size - 1; i >= 1; i--) sum[i] = sum[2*i] + sum[2*i+1];
     }
 
     inline void applyAssign(int node, ll val) {
         sum[node] = (ll)width[node] * val;
         assign[node] = val;
         hasAssign[node] = true;
         add[node] = 0;
     }
 
     inline void applyAdd(int node, ll val) {
         sum[node] += (ll)width[node] * val;
         if (hasAssign[node]) assign[node] += val;
         else add[node] += val;
     }
 
     inline void push(int node) {
         if (hasAssign[node]) {
             applyAssign(2*node, assign[node]);
             applyAssign(2*node+1, assign[node]);
             hasAssign[node] = false;
             assign[node] = 0;
         }
         if (add[node] != 0) {
             applyAdd(2*node, add[node]);
             applyAdd(2*node+1, add[node]);
             add[node] = 0;
         }
     }
 
     void rangeAssign(int l, int r, ll val) { _rassign(1, 0, size - 1, l, r, val); }
     void rangeAdd(int l, int r, ll val)    { _radd(1, 0, size - 1, l, r, val); }
     ll   rangeSum(int l, int r)            { return _rsum(1, 0, size - 1, l, r); }
 
 private:
     void _rassign(int node, int tl, int tr, int l, int r, ll val) {
         if (r < tl || l > tr) return;
         if (l <= tl && tr <= r) { applyAssign(node, val); return; }
         push(node);
         int tm = (tl + tr) >> 1;
         _rassign(2*node, tl, tm, l, r, val);
         _rassign(2*node+1, tm+1, tr, l, r, val);
         sum[node] = sum[2*node] + sum[2*node+1];
     }
 
     void _radd(int node, int tl, int tr, int l, int r, ll val) {
         if (r < tl || l > tr) return;
         if (l <= tl && tr <= r) { applyAdd(node, val); return; }
         push(node);
         int tm = (tl + tr) >> 1;
         _radd(2*node, tl, tm, l, r, val);
         _radd(2*node+1, tm+1, tr, l, r, val);
         sum[node] = sum[2*node] + sum[2*node+1];
     }
 
     ll _rsum(int node, int tl, int tr, int l, int r) {
         if (r < tl || l > tr) return 0;
         if (l <= tl && tr <= r) return sum[node];
         push(node);
         int tm = (tl + tr) >> 1;
         return _rsum(2*node, tl, tm, l, r) + _rsum(2*node+1, tm+1, tr, l, r);
     }
 };