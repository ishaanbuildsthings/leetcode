// TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
//
// USAGE
//   vector<pair<int,int>> pts;                 // every (x, y) you will ever chmax
//   for (int i = 0; i < n; i++) pts.push_back({i, nums[i]});
//   OfflineSparseBIT2DMax nxtUp(0, n - 1, lo, hi, pts);
//   OfflineSparseBIT2DMax nxtDown(0, n - 1, lo, hi, pts, false, true);
//
// Offline sparse 2D BIT over a max monoid. Same contract as the online
// variant -- corner-anchored queries only, monotone (chmax) updates only,
// orientation fixed at construction via descX / descY -- but ALL update
// coordinates must be supplied to the constructor. chmax at an
// unregistered (x, y) is undefined behaviour.
//
// That requirement is what buys the memory: each row node stores only
// the y-coords present in it, sorted, with a dense inner Fenwick over
// that compressed list. A point costs log(uX) slots, not
// log(uX) * log(uY).
//
//   ctor:      O(P log(uX) log P) time, O(P log(uX)) memory
//   chmax:     O(log(uX) * log(uY))
//   queryMax:  O(log(uX) * log(uY))
class OfflineSparseBIT2DMax {
    public:
        static constexpr long long NEG = LLONG_MIN;
    
        OfflineSparseBIT2DMax(int loX_, int hiX_, int loY_, int hiY_,
                              const vector<pair<int,int>>& points,
                              bool descX_ = false, bool descY_ = false)
            : loX(loX_), hiX(hiX_), loY(loY_), hiY(hiY_),
              descX(descX_), descY(descY_),
              uX(hiX_ - loX_ + 1), uY(hiY_ - loY_ + 1) {
    
            vector<int> cnt(uX + 2, 0);
            for (const auto& p : points) {
                int x = descX ? hiX - p.first + 1 : p.first - loX + 1;
                for (int i = x; i <= uX; i += i & -i) cnt[i]++;
            }
            start.assign(uX + 2, 0);
            for (int i = 1; i <= uX; i++) start[i + 1] = start[i] + cnt[i];
    
            vector<int> raw(start[uX + 1]);
            vector<int> cur(start.begin(), start.end());
            for (const auto& p : points) {
                int x = descX ? hiX - p.first + 1 : p.first - loX + 1;
                int y = descY ? hiY - p.second + 1 : p.second - loY + 1;
                for (int i = x; i <= uX; i += i & -i) raw[cur[i]++] = y;
            }
    
            // sort + dedup each node, compacting into a tight array
            ys.reserve(raw.size());
            vector<int> ns(uX + 2, 0);
            for (int i = 1; i <= uX; i++) {
                ns[i] = (int)ys.size();
                int a = start[i], b = start[i + 1];
                sort(raw.begin() + a, raw.begin() + b);
                int last = -1;
                for (int p = a; p < b; p++)
                    if (raw[p] != last) { ys.push_back(raw[p]); last = raw[p]; }
            }
            ns[uX + 1] = (int)ys.size();
            start.swap(ns);
            dat.assign(ys.size(), NEG);
        }
    
        // O(log(uX) * log(uY)) -- never lowers a cell
        void chmax(int x, int y, long long v) {
            x = descX ? hiX - x + 1 : x - loX + 1;
            y = descY ? hiY - y + 1 : y - loY + 1;
            for (int i = x; i <= uX; i += i & -i) {
                int a = start[i], b = start[i + 1], sz = b - a;
                int j = int(lower_bound(ys.begin() + a, ys.begin() + b, y)
                            - ys.begin() - a) + 1;      // 1-indexed within node
                for (; j <= sz; j += j & -j)
                    if (dat[a + j - 1] < v) dat[a + j - 1] = v;
            }
        }
    
        // O(log(uX) * log(uY)) -- NEG if empty or untouched
        long long queryMax(int x, int y) const {
            x = descX ? hiX - x + 1 : x - loX + 1;
            y = descY ? hiY - y + 1 : y - loY + 1;
            if (x <= 0 || y <= 0) return NEG;
            if (x > uX) x = uX;
            if (y > uY) y = uY;
            long long best = NEG;
            for (int i = x; i > 0; i -= i & -i) {
                int a = start[i], b = start[i + 1];
                int j = int(upper_bound(ys.begin() + a, ys.begin() + b, y)
                            - ys.begin() - a);          // count of cols <= y
                for (; j > 0; j -= j & -j) {
                    long long c = dat[a + j - 1];
                    if (c > best) best = c;
                }
            }
            return best;
        }
    
    private:
        int loX, hiX, loY, hiY;
        bool descX, descY;
        int uX, uY;
        vector<int> start, ys;
        vector<long long> dat;
    };