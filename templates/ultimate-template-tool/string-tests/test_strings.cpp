// Stress tests for the single-function string templates (../strings) against brute force:
// g++ -std=c++17 -O2 -fsanitize=address,undefined test_strings.cpp -o t && ./t
#include "../strings/minRotation.cpp"
#include "../strings/maxRotation.cpp"
#include "../strings/minRotationIndices.cpp"
#include "../strings/maxRotationIndices.cpp"
#include "../strings/zFunction.cpp"
#include "../strings/longestPrefixMatches.cpp"
#include "../strings/findMatches.cpp"
#include "../strings/prefixFunction.cpp"
#include "../strings/findMatchesKmp.cpp"
#include "../strings/shortestPeriod.cpp"

mt19937 rng(12345);
int rnd(int lo, int hi) { return uniform_int_distribution<int>(lo, hi)(rng); }
#define CHECK(c) do { if (!(c)) { cerr << "FAIL line " << __LINE__ << ": " #c << endl; exit(1); } } while (0)

template <class T>
void checkAll(const T& s, const T& t) {
    int n = s.size(), m = t.size();
    vector<T> rots;
    for (int i = 0; i < n; i++) {
        T r(s.begin() + i, s.end());
        r.insert(r.end(), s.begin(), s.begin() + i);
        rots.push_back(r);
    }
    if (n) {
        T lo = *min_element(rots.begin(), rots.end()), hi = *max_element(rots.begin(), rots.end());
        CHECK(minRotation(s) == lo);
        CHECK(maxRotation(s) == hi);
        vector<int> a, b;
        for (int i = 0; i < n; i++) { if (rots[i] == lo) a.push_back(i); if (rots[i] == hi) b.push_back(i); }
        CHECK(minRotationIndices(s) == a);
        CHECK(maxRotationIndices(s) == b);
    } else {
        CHECK(minRotation(s).empty() && maxRotationIndices(s).empty());
    }
    auto lcp = [](const T& x, int xi, const T& y, int yi) {
        int k = 0;
        while (xi + k < (int)x.size() && yi + k < (int)y.size() && x[xi + k] == y[yi + k]) k++;
        return k;
    };
    vector<int> z(n), pi(n);
    for (int i = 0; i < n; i++) z[i] = lcp(s, 0, s, i);
    CHECK(zFunction(s) == z);
    for (int i = 0; i < n; i++)
        for (int k = i; k >= 0; k--)
            if (equal(s.begin(), s.begin() + k, s.begin() + i - k + 1)) { pi[i] = k; break; }
    CHECK(prefixFunction(s) == pi);
    int period = n;
    for (int p = 1; p <= n; p++) {
        if (n % p) continue;
        bool ok = true;
        for (int i = p; i < n && ok; i++) ok = s[i] == s[i - p];
        if (ok) { period = p; break; }
    }
    CHECK(shortestPeriod(s) == period);
    vector<int> lens(n), matches;
    for (int i = 0; i < n; i++) lens[i] = lcp(t, 0, s, i);
    for (int i = 0; i + m <= n; i++) if (equal(t.begin(), t.end(), s.begin() + i)) matches.push_back(i);
    CHECK(longestPrefixMatches(s, t) == lens);
    CHECK(findMatches(s, t) == matches);
    CHECK(findMatchesKmp(s, t) == matches);
}

template <class T>
T randSeq(int sigma) {
    int n = vector<int>{0, 1, 2, 3, rnd(0, 12), rnd(0, 40)}[rnd(0, 5)];
    T s;
    if (rnd(0, 9) < 3 && n) {
        int b = rnd(1, 4);
        T base;
        for (int i = 0; i < b; i++) base.push_back('a' + rnd(0, sigma - 1));
        for (int i = 0; i < n; i++) s.push_back(base[i % b]);
    } else {
        for (int i = 0; i < n; i++) s.push_back('a' + rnd(0, sigma - 1));
    }
    return s;
}

int main() {
    for (int it = 0; it < 20000; it++) {
        int sigma = vector<int>{1, 2, 3, 26}[rnd(0, 3)];
        string s = randSeq<string>(sigma), t = randSeq<string>(sigma);
        if (!s.empty() && rnd(0, 1)) { int a = rnd(0, s.size() - 1); t = s.substr(a, rnd(0, s.size() - a)); }
        checkAll(s, t);
        vector<long long> vs(s.begin(), s.end()), vt(t.begin(), t.end());
        checkAll(vs, vt);
    }
    // mixed container types for the matchers
    CHECK(findMatches(string("ababa"), vector<char>{'a', 'b', 'a'}) == vector<int>({0, 2}));
    cout << "all string templates ok: 40000 random cases" << endl;
}
