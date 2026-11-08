// Brute-force checks for one stripped Eertree.cpp (included as eertree_under_test.cpp); test_eertree_cpp.py compiles
// this once per op subset, with -DHAS_<op> for each op kept.
#include "eertree_under_test.cpp"
mt19937 rng(11);
int rnd(int a, int b) { return uniform_int_distribution<int>(a, b)(rng); }
#define CHECK(c) do { if (!(c)) { cerr << "FAIL line " << __LINE__ << ": " #c << endl; exit(1); } } while (0)

template <class E>
void check(Eertree<E>& t, const vector<E>& s) {
    int n = s.size();
    auto pal = [&](int a, int b) { for (; a < b; a++, b--) if (!(s[a] == s[b])) return false; return true; };
    (void)pal;
#if defined(HAS_leftmostLForPalEndingAtR) || defined(HAS_leftmostLForPalEndingAtEachR)
    {
        vector<int> w(n); for (int r = 0; r < n; r++) { int l = 0; while (!pal(l, r)) l++; w[r] = l; }
#ifdef HAS_leftmostLForPalEndingAtR
        for (int r = 0; r < n; r++) CHECK(t.leftmostLForPalEndingAtR(r) == w[r]);
#endif
#ifdef HAS_leftmostLForPalEndingAtEachR
        CHECK(t.leftmostLForPalEndingAtEachR() == w);
#endif
    }
#endif
#if defined(HAS_rightmostRForPalStartingAtL) || defined(HAS_rightmostRForPalStartingAtEachL)
    {
        vector<int> w(n); for (int l = 0; l < n; l++) { int r = n - 1; while (!pal(l, r)) r--; w[l] = r; }
#ifdef HAS_rightmostRForPalStartingAtL
        for (int l = 0; l < n; l++) CHECK(t.rightmostRForPalStartingAtL(l) == w[l]);
#endif
#ifdef HAS_rightmostRForPalStartingAtEachL
        CHECK(t.rightmostRForPalStartingAtEachL() == w);
#endif
    }
#endif
    auto distinct = [&](int m) { set<vector<E>> st; for (int a = 0; a < m; a++) for (int b = a; b < m; b++) if (pal(a, b)) st.insert(vector<E>(s.begin() + a, s.begin() + b + 1)); return (int)st.size(); };
    (void)distinct;
#ifdef HAS_numDistinctPals
    CHECK(t.numDistinctPals() == distinct(n));
#endif
#if defined(HAS_numDistinctPalsInPrefixEndingAtR) || defined(HAS_numDistinctPalsInPrefixEndingAtEachR)
    {
        vector<int> w(n); for (int r = 0; r < n; r++) w[r] = distinct(r + 1);
#ifdef HAS_numDistinctPalsInPrefixEndingAtR
        for (int r = 0; r < n; r++) CHECK(t.numDistinctPalsInPrefixEndingAtR(r) == w[r]);
#endif
#ifdef HAS_numDistinctPalsInPrefixEndingAtEachR
        CHECK(t.numDistinctPalsInPrefixEndingAtEachR() == w);
#endif
    }
#endif
#if defined(HAS_numPalsEndingAtR) || defined(HAS_numPalsEndingAtEachR)
    {
        vector<int> w(n, 0); for (int r = 0; r < n; r++) for (int l = 0; l <= r; l++) w[r] += pal(l, r);
#ifdef HAS_numPalsEndingAtR
        for (int r = 0; r < n; r++) CHECK(t.numPalsEndingAtR(r) == w[r]);
#endif
#ifdef HAS_numPalsEndingAtEachR
        CHECK(t.numPalsEndingAtEachR() == w);
#endif
    }
#endif
#ifdef HAS_numPalsTotal
    { long long w = 0; for (int a = 0; a < n; a++) for (int b = a; b < n; b++) w += pal(a, b); CHECK(t.numPalsTotal() == w); }
#endif
#ifdef HAS_distinctPalsWithCounts
    {
        map<vector<E>, tuple<int, int, long long>> w;
        for (int a = 0; a < n; a++) for (int b = a; b < n; b++) if (pal(a, b)) {
            vector<E> key(s.begin() + a, s.begin() + b + 1);
            if (!w.count(key)) w[key] = {a, b, 0};
            get<2>(w[key])++;
        }
        vector<tuple<int, int, long long>> want, got = t.distinctPalsWithCounts();
        for (auto& [k, v] : w) want.push_back(v);
        sort(want.begin(), want.end()); sort(got.begin(), got.end());
        CHECK(got == want);
    }
#endif
#ifdef HAS_longestPalEndingAtCurrentR
    { int w = 0; for (int l = 0; l < n; l++) if (pal(l, n - 1)) { w = n - l; break; } CHECK(t.longestPalEndingAtCurrentR() == w); }
#endif
#ifdef HAS_longestPalStartingAtCurrentL
    { int w = 0; for (int r = n - 1; r >= 0; r--) if (pal(0, r)) { w = r + 1; break; } CHECK(t.longestPalStartingAtCurrentL() == w); }
#endif
#ifdef HAS_longestPal
    { int w = 0; for (int a = 0; a < n; a++) for (int b = a; b < n; b++) if (pal(a, b)) w = max(w, b - a + 1); CHECK(t.longestPal() == w); }
#endif
#ifdef HAS_numPalsEndingAtCurrentR
    { int w = 0; for (int l = 0; l < n; l++) w += pal(l, n - 1); CHECK(t.numPalsEndingAtCurrentR() == w); }
#endif
#ifdef HAS_numPalsStartingAtCurrentL
    { int w = 0; for (int r = 0; r < n; r++) w += pal(0, r); CHECK(t.numPalsStartingAtCurrentL() == w); }
#endif
#ifdef HAS_minPalPartition
    { vector<int> dp(n + 1, 1 << 29); dp[0] = 0; for (int b = 1; b <= n; b++) for (int a = 0; a < b; a++) if (pal(a, b - 1)) dp[b] = min(dp[b], dp[a] + 1); CHECK(t.minPalPartition() == dp[n]); }
#endif
}

template <class E>
void run(function<E(int)> item) {
    for (int it = 0; it < 300; it++) {
        int sigma = vector<int>{1, 2, 3, 26}[rnd(0, 3)];
        vector<E> s;
        for (int k = rnd(0, 10); k--;) s.push_back(item(rnd(0, sigma - 1)));
        Eertree<E> t(s);
        check(t, s);
        for (int step = rnd(0, 25); step--;) {
#ifdef HAS_pop
            if (!s.empty() && rnd(0, 99) < 45) { CHECK(t.pop() == s.back()); s.pop_back(); check(t, s); continue; }
#endif
#ifdef HAS_append
            E x = item(rnd(0, sigma - 1)); t.append(x); s.push_back(x); check(t, s);
#else
            break;
#endif
        }
    }
}

int main() {
    run<char>([](int v) { return char('a' + v); });
    run<long long>([](int v) { return (long long)v - 1; });
    run<pair<int, int>>([](int v) { return make_pair(v, -v); });
    Eertree<char> fromString(string("abaab"));
    (void)fromString;
    cout << "ok" << endl;
}
