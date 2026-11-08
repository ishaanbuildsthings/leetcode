#include "deque_eertree_under_test.cpp"  // a stripped DequeEertree.cpp, written by test_deque_eertree_cpp.py

mt19937_64 rng(12345);
long long rnd(long long a, long long b) { return uniform_int_distribution<long long>(a, b)(rng); }

template <class E>
bool isPal(const deque<E>& s, int i, int j) {
    while (i < j)
        if (!(s[i++] == s[j--])) return false;
    return true;
}

template <class E>
void check(DequeEertree<E>& et, const deque<E>& s) {
    int n = s.size();
    set<vector<E>> distinct;
    long long total = 0;
    int longR = 0, longL = 0, longest = 0, endR = 0, startL = 0;
    for (int i = 0; i < n; i++)
        for (int j = i; j < n; j++)
            if (isPal(s, i, j)) {
                distinct.insert(vector<E>(s.begin() + i, s.begin() + j + 1));
                total++;
                longest = max(longest, j - i + 1);
                endR += j == n - 1;
                startL += i == 0;
                if (j == n - 1) longR = max(longR, j - i + 1);
                if (i == 0) longL = max(longL, j - i + 1);
            }
    if (et.numDistinctPals() != (int)distinct.size() || et.numPalsTotal() != total ||
        et.longestPalEndingAtCurrentR() != longR || et.longestPalStartingAtCurrentL() != longL ||
        et.longestPal() != longest || et.size() != n ||
        et.numPalsEndingAtCurrentR() != endR || et.numPalsStartingAtCurrentL() != startL) {
        printf("MISMATCH n=%d got %d %lld %d %d exp %d %lld %d %d\n", n, et.numDistinctPals(), et.numPalsTotal(),
               et.longestPalEndingAtCurrentR(), et.longestPalStartingAtCurrentL(), (int)distinct.size(), total, longR, longL);
        exit(1);
    }
}

template <class E, class Gen>
void runCase(Gen gen) {
    int n0 = rnd(0, 8);
    vector<E> init;
    for (int i = 0; i < n0; i++) init.push_back(gen());
    DequeEertree<E> et(init);
    deque<E> s(init.begin(), init.end());
    check(et, s);
    int ops = rnd(1, 60);
    int pushBias = rnd(3, 7);
    auto popOne = [&]() {
        if (rnd(0, 1)) {
            E got = et.pop();
            if (!(got == s.back())) { puts("bad pop"); exit(1); }
            s.pop_back();
        } else {
            E got = et.popLeft();
            if (!(got == s.front())) { puts("bad popLeft"); exit(1); }
            s.pop_front();
        }
    };
    for (int op = 0; op < ops; op++) {
        if (rnd(0, 9) < pushBias || s.empty()) {
            E x = gen();
            if (rnd(0, 1)) et.append(x), s.push_back(x);
            else et.appendLeft(x), s.push_front(x);
        } else {
            popOne();
        }
        if (s.size() > 25)
            while (!s.empty()) popOne(), check(et, s);
        check(et, s);
    }
    while (!s.empty()) popOne();
    check(et, s);
    bool threw = false;
    try { et.pop(); } catch (const out_of_range&) { threw = true; }
    if (!threw) { puts("no throw"); exit(1); }
    threw = false;
    try { et.popLeft(); } catch (const out_of_range&) { threw = true; }
    if (!threw) { puts("no throw"); exit(1); }
    // refill after empty
    for (int i = 0; i < 10; i++) {
        E x = gen();
        if (rnd(0, 1)) et.append(x), s.push_back(x);
        else et.appendLeft(x), s.push_front(x);
        check(et, s);
    }
}

int main() {
    int cases = 0;
    for (int k : {1, 2, 3, 26}) {
        for (int t = 0; t < 1500; t++, cases++) runCase<char>([&]() { return char('a' + rnd(0, k - 1)); });
        for (int t = 0; t < 1500; t++, cases++) runCase<long long>([&]() { return rnd(0, k - 1) - k / 2; });
        for (int t = 0; t < 1500; t++, cases++)
            runCase<pair<int, int>>([&]() { return make_pair(int(rnd(0, k - 1) % 2), -int(rnd(0, k - 1) / 2)); });
    }
    // constructors
    DequeEertree<char> a("abaab");
    DequeEertree<char> b(string("abaab"));
    DequeEertree<long long> c(vector<long long>{-1, 2, -1});
    DequeEertree<string> d(vector<string>{"x", "yy", "x"});
    DequeEertree<pair<int, int>> e;
    if (a.numDistinctPals() != 5 || b.numPalsTotal() != a.numPalsTotal() || c.numDistinctPals() != 3 ||
        d.longestPalEndingAtCurrentR() != 3 || e.numPalsTotal() != 0) { puts("ctor fail"); return 1; }
    printf("cpp stress ok: %d cases\n", cases);
}
