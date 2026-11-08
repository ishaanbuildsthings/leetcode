// Stress test for longestPalAroundEachCenter (../strings) against brute force:
// g++ -std=c++17 -O1 -fsanitize=address,undefined test_palindromes.cpp -o t && ./t
#include "../strings/longestPalAroundEachCenter.cpp"
int main() {
    mt19937 rng(4);
    for (int it = 0; it < 20000; it++) {
        int n = rng() % 15, sg = vector<int>{1, 2, 3, 26}[rng() % 4];
        vector<long long> s(n); for (auto& x : s) x = (long long)(rng() % sg) - 1;
        auto pal = [&](int a, int b) { for (; a < b; a++, b--) if (s[a] != s[b]) return false; return true; };
        auto [a, b] = longestPalAroundEachCenter(s);
        for (int i = 0; i < n; i++) {
            int k = 0; while (i - k >= 0 && i + k < n && pal(i - k, i + k)) k++;
            if (a[i] != make_pair(i - k + 1, i + k - 1)) { puts("odd FAIL"); return 1; }
            k = 0; while (i - k >= 0 && i + 1 + k < n && pal(i - k, i + 1 + k)) k++;
            if (b[i] != (k ? make_pair(i - k + 1, i + k) : make_pair(i + 1, i))) { puts("even FAIL"); return 1; }
        }
    }
    auto [a, b] = longestPalAroundEachCenter(string("abaab"));
    for (auto [l, r] : a) printf("(%d,%d) ", l, r);
    puts("");
    for (auto [l, r] : b) printf("(%d,%d) ", l, r);
    puts("\nlongestPalAroundEachCenter ok: 20000 random cases");
}
