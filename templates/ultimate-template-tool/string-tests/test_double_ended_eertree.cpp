// Brute-force checks for DoubleEndedEertree.cpp with every op kept (random append / appendLeft):
// g++ -std=c++17 -O1 -fsanitize=address,undefined test_double_ended_eertree.cpp -o t && ./t
// (the markers are just comments, so the unstripped file compiles with everything)
#include "../strings/DoubleEndedEertree.cpp"
mt19937 rng(13);
int rnd(int a, int b) { return uniform_int_distribution<int>(a, b)(rng); }
#define CHECK(c) do { if (!(c)) { cerr << "FAIL line " << __LINE__ << ": " #c << endl; exit(1); } } while (0)

template <class E>
void run(function<E(int)> item) {
    for (int it = 0; it < 400; it++) {
        int sigma = vector<int>{1, 2, 3, 26}[rnd(0, 3)];
        deque<E> s;
        for (int k = rnd(0, 8); k--;) s.push_back(item(rnd(0, sigma - 1)));
        DoubleEndedEertree<E> t(vector<E>(s.begin(), s.end()));
        for (int step = rnd(0, 30); step >= 0; step--) {
            int n = s.size();
            auto pal = [&](int a, int b) { for (; a < b; a++, b--) if (!(s[a] == s[b])) return false; return true; };
            set<vector<E>> st;
            long long total = 0;
            for (int a = 0; a < n; a++) for (int b = a; b < n; b++) if (pal(a, b)) { st.insert(vector<E>(s.begin() + a, s.begin() + b + 1)); total++; }
            CHECK(t.numDistinctPals() == (int)st.size());
            CHECK(t.numPalsTotal() == total);
            int suf = 0, pre = 0;
            for (int l = 0; l < n; l++) if (pal(l, n - 1)) { suf = n - l; break; }
            for (int r = n - 1; r >= 0; r--) if (pal(0, r)) { pre = r + 1; break; }
            CHECK(t.longestPalEndingAtCurrentR() == suf);
            CHECK(t.longestPalStartingAtCurrentL() == pre);
            int longest = 0;
            for (int a = 0; a < n; a++) for (int b = a; b < n; b++) if (pal(a, b)) longest = max(longest, b - a + 1);
            CHECK(t.longestPal() == longest);
            int endR = 0, startL = 0;
            for (int a = 0; a < n; a++) endR += pal(a, n - 1);
            for (int b = 0; b < n; b++) startL += pal(0, b);
            CHECK(t.numPalsEndingAtCurrentR() == endR);
            CHECK(t.numPalsStartingAtCurrentL() == startL);
            E x = item(rnd(0, sigma - 1));
            if (rnd(0, 1)) { t.append(x); s.push_back(x); } else { t.appendLeft(x); s.push_front(x); }
        }
    }
}

int main() {
    run<char>([](int v) { return char('a' + v); });
    run<long long>([](int v) { return (long long)v - 1; });
    run<pair<int, int>>([](int v) { return make_pair(v, -v); });
    cout << "ok" << endl;
}
