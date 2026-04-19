class APRangeAddSegTree {
    public:
        APRangeAddSegTree(int n) : n_(n) {
            size_ = 1;
            while (size_ < std::max(n, 1)) size_ *= 2;
            
            sum_.assign(2 * size_, 0);
            lazyConst_.assign(2 * size_, 0);
            lazyIdx_.assign(2 * size_, 0);
            nodeL_.assign(2 * size_, 0);
            nodeR_.assign(2 * size_, 0);
            
            initRanges(1, 0, size_ - 1);
        }
        
        // Adds the arithmetic progression startVal, startVal + step, startVal + 2*step, ...
        // to positions l, l+1, ..., r. At position i, adds startVal + step*(i-l),
        // rewritten as (startVal - step*l) + step*i. Stored as two additive lazy tags
        // per node. Both tags compose by simple addition, and since we never query
        // mid-stream, we skip pushToRoot/recomputeToRoot entirely. Time: O(log n).
        void rangeAddAP(int l, int r, long long startVal, long long step) {
            if (l > r) return;
            long long constPart = startVal - step * (long long)l;
            long long idxPart = step;
            int lIdx = l + size_;
            int rIdx = r + size_ + 1;
            while (lIdx < rIdx) {
                if (lIdx & 1) { applyNode(lIdx, constPart, idxPart); lIdx++; }
                if (rIdx & 1) { rIdx--; applyNode(rIdx, constPart, idxPart); }
                lIdx >>= 1;
                rIdx >>= 1;
            }
        }
        
        // Push all lazy tags down to leaves. Call once after all updates,
        // before reading leaf values directly via leafValue().
        void pushAllDown() {
            for (int node = 1; node < size_; node++) {
                if (lazyConst_[node] != 0 || lazyIdx_[node] != 0) {
                    applyNode(2 * node, lazyConst_[node], lazyIdx_[node]);
                    applyNode(2 * node + 1, lazyConst_[node], lazyIdx_[node]);
                    lazyConst_[node] = 0;
                    lazyIdx_[node] = 0;
                }
            }
        }
        
        long long leafValue(int i) {
            return sum_[i + size_];
        }
    
    private:
        int n_, size_;
        std::vector<long long> sum_, lazyConst_, lazyIdx_;
        std::vector<int> nodeL_, nodeR_;
        
        void initRanges(int node, int l, int r) {
            nodeL_[node] = l;
            nodeR_[node] = r;
            if (l == r) return;
            int mid = (l + r) / 2;
            initRanges(2 * node, l, mid);
            initRanges(2 * node + 1, mid + 1, r);
        }
        
        void applyNode(int node, long long constPart, long long idxPart) {
            long long l = nodeL_[node];
            long long r = nodeR_[node];
            long long length = r - l + 1;
            long long sumOfIndices = (l + r) * length / 2;
            sum_[node] += constPart * length + idxPart * sumOfIndices;
            lazyConst_[node] += constPart;
            lazyIdx_[node] += idxPart;
        }
    };
    
    
    class Solution {
    public:
        long long maxArea(int height, vector<int>& positions, string directions) {
            int n = positions.size();
            int T = 2 * height;
            APRangeAddSegTree tree(T);
            
            auto addClipped = [&](int l, int r, long long startVal, long long step) {
                if (r > T - 1) r = T - 1;
                if (l < 0) l = 0;
                tree.rangeAddAP(l, r, startVal, step);
            };
            
            for (int i = 0; i < n; i++) {
                int p = positions[i];
                char d = directions[i];
                
                if (d == 'U') {
                    int seg1End = height - p;
                    addClipped(0, seg1End, p, 1);
                    
                    int seg2Start = seg1End + 1;
                    int seg2End = seg2Start + height - 1;
                    addClipped(seg2Start, seg2End, height - 1, -1);
                    
                    int seg3Start = seg2End + 1;
                    int seg3End = T - 1;
                    addClipped(seg3Start, seg3End, 1, 1);
                } else {
                    int seg1End = p;
                    addClipped(0, seg1End, p, -1);
                    
                    int seg2Start = seg1End + 1;
                    int seg2End = seg2Start + height - 1;
                    addClipped(seg2Start, seg2End, 1, 1);
                    
                    int seg3Start = seg2End + 1;
                    int seg3End = T - 1;
                    addClipped(seg3Start, seg3End, height - 1, -1);
                }
            }
            
            tree.pushAllDown();
            
            long long best = 0;
            for (int t = 0; t < T; t++) {
                long long v = tree.leafValue(t);
                if (v > best) best = v;
            }
            return best;
        }
    };