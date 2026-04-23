using ull = unsigned long long;
struct FastSet {
    static constexpr unsigned B = 64; // bits per word
    int u; // universe size, so if we have [0, n] values then u=n+1
    int levels; // number of levels in the trie
    vector<vector<ull>> seg; // seg[h] = vector of 64-bit words at level h

    void build(int _u) {
        // destroys every word in our list, and then resets the list to size 0 again, basically a reset between tests, takes O(size of vector) to call all the destructors
        seg.clear();
        u = _u;
        int width = u; // how many values we are currently responsible for
        while (true) {
            int numWords = (width + B - 1) / B; // ceil(width / 64)
            seg.push_back(vector<ull>(numWords, 0));
            if (numWords == 1) break;
            width = numWords; // next level up will summarize `numWords` words, so that's its new width
        }
        levels = (int)seg.size();
    }

    // add i to the set, takes log_64(U) time
    void insert(int i) {
        if (i < 0 || i >= u) return; // bounds check
        for (int h = 0; h < levels; h++) {
            seg[h][i / B] |= (1ULL << (i % B));
            i /= B;
        }
    }

    // removes i from the set, log_64(U) time, some weird branchless version
    void erase(int i) {
        if (i < 0 || i >= u) return;
        ull carry = 0;
        for (int h = 0; h < levels; h++) {
            int idx = i / B;
            ull &v = seg[h][idx];
            v &= ~(1ULL << (i % B)); // clear the bit
            v |= (carry << (i % B)); // restore the bit if child was still nonempty
            carry = (v != 0); // did this word survive?
            i = idx;
        }
    }

    // O(1) check if i is in the set
    bool contains(int i) const {
        if (i < 0 || i >= u) return false;
        return (seg[0][i / B] >> (i % B)) & 1ULL;
    }

    // find next value >= i, O(log_64(U)), or -1 if it doesn't exist
    // first we check the base level word if any other bit on the right (or equal) is set, we can do this with machine ops
    // if not, we walk up, check some more, etc, then when we find the right place we walk back down
    int next(int i) const {
        if (i < 0) i = 0;
        if (i >= u) return -1;
        for (int h = 0; h < levels; h++) {
            int idx = i / B;
            if (idx >= (int)seg[h].size()) break;
            ull v = seg[h][idx] >> (i % B);
            if (v) {
                // Answer's in this word. Convert to an absolute position at level h.
                int pos = i + __builtin_ctzll(v);
                // Descend: at each level below, pos becomes the word index at that level.
                for (int g = h - 1; g >= 0; g--) {
                    pos = pos * B + __builtin_ctzll(seg[g][pos]);
                }
                return pos;
            }
            i = idx + 1;  // climb: at the next level, we want bits past the current word
        }
        return -1;
    }

    // O(log_64(U)) finds the first element <= i or -1 if it doesn't exist
    int prev(int i) const {
        if (i >= u) i = u - 1;
        if (i < 0) return -1;
        for (int h = 0; h < levels; h++) {
            int idx = i / B;
            ull v = seg[h][idx] & (~0ULL >> (63 - (i % B)));
            if (v) {
                int pos = idx * B + (63 - __builtin_clzll(v));
                for (int g = h - 1; g >= 0; g--) {
                    ull vv = seg[g][pos];
                    pos = pos * B + (63 - __builtin_clzll(vv));
                }
                return pos;
            }
            if (idx == 0) return -1;
            i = idx - 1;  // at level h+1, we want positions ≤ idx-1
        }
        return -1;
    }
};