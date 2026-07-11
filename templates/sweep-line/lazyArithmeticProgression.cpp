// Offline range arithmetic-progression add. No queries during updates.
//
// Second-difference array: diff_[i] is the change in the step at position i.
// Two prefix sums at the end recover the values.
//
// mod defaults to 0, which means no modular arithmetic at all.
// Pass a mod to reduce everything into [0, mod); start and step may then
// still be negative, they get normalized on the way in.
//
// Public operations:
//   APDiff(int n) or APDiff(int n, long long mod)   O(n)
//   rangeAddAP(l, r, start, step)                   O(1)
//   build()                                         O(n)  -- returns the final vector of n values
class APDiff {
    public:
        explicit APDiff(int n, long long mod = 0) : n_(n), MOD_(mod), diff_(n + 2, 0) {}
    
        void rangeAddAP(int l, int r, long long start, long long step) {
            if (l > r) return;
            if (MOD_) {
                long long s = norm(start);
                long long d = norm(step);
                long long end = (s + d * (long long)(r - l)) % MOD_;
                diff_[l] = (diff_[l] + s) % MOD_;
                diff_[l + 1] = ((diff_[l + 1] + d - s) % MOD_ + MOD_) % MOD_;
                diff_[r + 1] = ((diff_[r + 1] - end - d) % MOD_ + MOD_) % MOD_;
                diff_[r + 2] = (diff_[r + 2] + end) % MOD_;
            } else {
                long long end = start + step * (long long)(r - l);
                diff_[l] += start;
                diff_[l + 1] += step - start;
                diff_[r + 1] -= end + step;
                diff_[r + 2] += end;
            }
        }
    
        std::vector<long long> build() const {
            std::vector<long long> res(n_);
            long long step = 0, total = 0;
            if (MOD_) {
                for (int i = 0; i < n_; i++) {
                    step += diff_[i]; if (step >= MOD_) step -= MOD_;
                    total += step;    if (total >= MOD_) total -= MOD_;
                    res[i] = total;
                }
            } else {
                for (int i = 0; i < n_; i++) {
                    step += diff_[i];
                    total += step;
                    res[i] = total;
                }
            }
            return res;
        }
    
    private:
        int n_;
        long long MOD_;
        std::vector<long long> diff_;
        inline long long norm(long long x) const { x %= MOD_; if (x < 0) x += MOD_; return x; }
    };