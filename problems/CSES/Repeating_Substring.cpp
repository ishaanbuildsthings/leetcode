#include <bits/stdc++.h>
using namespace std;
using ll = long long;

#include <ext/pb_ds/assoc_container.hpp>
using namespace __gnu_pbds;

struct custom_hash {
    static uint64_t splitmix64(uint64_t x) {
        x += 0x9e3779b97f4a7c15;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
        x = (x ^ (x >> 27)) * 0x94d049bb133111eb;
        return x ^ (x >> 31);
    }
    static uint64_t fixed_random() {
        static const uint64_t r = chrono::steady_clock::now().time_since_epoch().count();
        return r;
    }
    size_t operator()(uint64_t x) const {
        return splitmix64(x + fixed_random());
    }
    size_t operator()(int x) const {
        return splitmix64((uint64_t)x + fixed_random());
    }
    size_t operator()(long long x) const {
        return splitmix64((uint64_t)x + fixed_random());
    }
    template<class A, class B>
    size_t operator()(const pair<A,B>& p) const {
        return splitmix64((uint64_t)p.first * 0x9E3779B97F4A7C15ULL + (uint64_t)p.second + fixed_random());
    }
    size_t operator()(const string& s) const {
        uint64_t h = fixed_random();
        for (char c : s) h = splitmix64(h ^ (uint64_t)c);
        return h;
    }
};

template<class K, class V> using hash_map = gp_hash_table<K, V, custom_hash>;
template<class K>          using hash_set = gp_hash_table<K, null_type, custom_hash>;

// example usages
// hash_set<int> seen;
// hash_set<pair<ll,ll>> seenHashes;
// hash_map<string, int> counts;
// hash_map<pair<int,int>, vector<int>> adj;
//
// methods (gp_hash_table API, differs from std::unordered_*):
//   container.insert(key)            // set: insert key
//   container.insert({key, value})   // map: insert pair
//   container[key] = value           // map: insert or assign
//   container.find(key)              // returns iterator; check != end() (no count())
//   container.erase(key)             // remove by key
//   container.size()                 // number of entries
//   container.empty()                // bool
//   for (auto& x : container)        // iterate (set: x is key; map: x is pair<K,V>)
//
// gotchas:
//   - no .count(key) method, use find(key) != end()
//   - no .reserve() or .bucket_count(), pb_ds manages capacity internally
//   - iteration order is unspecified (it's a hash table)
//   - cannot store gp_hash_table inside another gp_hash_table directly without extra wrapping

const ll BASE = 911;
const ll BASE2 = 31;
const ll MOD2 = 1000000007;
const ll MOD = 999999527;
const ll MAX_N = 100000;
ll basePow[MAX_N + 1];
ll basePow2[MAX_N + 1];

struct Hasher {
    ll h1 = 0;
    ll h2 = 0;
    ll size = 0;

    pair<ll,ll> getHash() { return {h1, h2}; }
    void addRight(char c) {
        ll coeff = c - 'a' + 1;
        h1 *= BASE;
        h1 += coeff;
        h1 %= MOD;
        h2 *= BASE2;
        h2 += coeff;
        h2 %= MOD2;
        size++;
    }
    void popLeft(char c) {
        ll leftPow = size - 1;
        ll coeff = c - 'a' + 1;
        ll lost1 = (coeff * basePow[leftPow]) % MOD;
        h1 -= lost1;
        if (h1 < 0) h1 += MOD;
        ll lost2 = (coeff * basePow2[leftPow]) % MOD2;
        h2 -= lost2;
        if (h2 < 0) h2 += MOD2;
        size--;
    }
};

void init() {
    basePow[0] = 1;
    basePow2[0] = 1;
    for (int p = 1; p <= MAX_N; p++) {
        ll npow = (basePow[p - 1] * BASE) % MOD;
        basePow[p] = npow;
        ll npow2 = (basePow2[p - 1] * BASE2) % MOD2;
        basePow2[p] = npow2;
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    init();
    int resL = -1;
    int resR = -1;
    string s; cin >> s;
    int n = s.size();

    int l = 1;
    int r = n;
    while (l <= r) {
        int m = (l + r) / 2;
        // cerr << "length: " << m << endl;
        Hasher h;
        hash_set<pair<ll,ll>> seenHashes;
        for (int right = 0; right < m; right++) {
            h.addRight(s[right]);
        }
        int found = 0;
        seenHashes.insert(h.getHash());
        for (int right = m; right < n; right++) {
            h.addRight(s[right]);
            h.popLeft(s[right - m]);
            if (seenHashes.find(h.getHash()) != seenHashes.end()) {
                resL = right - m + 1;
                resR = right;
                found = 1;
            }
            seenHashes.insert(h.getHash());
        }
        if (found) {
            l = m + 1;
        } else {
            r = m - 1;
        }

    }
    if (resL == -1) {
        cout << -1 << endl;
    } else {
        for (int i = resL; i <= resR; i++) cout << s[i];
    }
}