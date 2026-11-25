"""Compiles every syntax line documented in hash-tables/hashSet.cpp and hashMap.cpp (so the docs can't drift from what
works), checks both against std::set / std::map on random operations for every key type the docs promise (int, ll,
unsigned, char, pair<int, int>, pair<ll, ll>, string), with sanitizers, and times them against unordered_set / map.

    python3 test_hash_tables.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "hash-tables")

SET_SYNTAX = r'''
void setSyntax() {
    vector<int> arr = {3, 1, 3};
    int r = 1, c = 2;
    hash_set<int> seen;  for (int x : arr) seen.insert(x);
    hash_set<pair<int, int>> visited;
    hash_set<string> words;
    words.insert("hi");
    seen.insert(5);
    bool added = seen.insert(5).second;
    visited.insert({r, c});
    bool has = seen.find(5) != seen.end();
    if (seen.find(5) != seen.end()) {}
    if (seen.find(5) == seen.end()) {}
    if (visited.find({r, c}) == visited.end()) { visited.insert({r, c}); }
    int n = seen.size();
    if (seen.empty()) {}
    for (int x : seen) { (void)x; }
    for (auto [rr, cc] : visited) { (void)rr; (void)cc; }
    for (const string& w : words) { (void)w; }
    vector<int> keys(seen.begin(), seen.end());
    seen.erase(5);
    bool removed = seen.erase(5);
    seen.clear();
    assert(!added && has && n == 3 && keys.size() == 3 && !removed && seen.empty());
}
'''
MAP_SYNTAX = r'''
void mapSyntax() {
    vector<int> arr = {3, 1, 3};
    int r = 1, c = 2, i = 0;
    hash_map<int, int> cnt;  for (int x : arr) cnt[x]++;
    hash_map<string, vector<int>> positions;
    hash_map<pair<int, int>, ll> best;
    hash_map<int, hash_map<int, int>> nested;  nested[1][2] = 3;
    cnt[7] = 3;
    cnt[7]++;
    positions["abc"].push_back(i);
    best[{r, c}] = 10;
    cnt.insert({7, 3});
    bool has = cnt.find(7) != cnt.end();
    if (cnt.find(7) != cnt.end()) {}
    if (cnt.find(7) == cnt.end()) {}
    int v = cnt[7];
    auto it = cnt.find(7);
    if (it != cnt.end()) { int v2 = it->second; (void)v2; }
    int v3 = it != cnt.end() ? it->second : -1;
    int n = cnt.size();
    if (cnt.empty()) {}
    for (auto& [key, value] : cnt) { (void)key; (void)value; }
    for (auto& [key, value] : cnt) { (void)key; value *= 2; }
    for (auto& [key, _] : cnt) { (void)key; }
    for (auto& [_, value] : cnt) { (void)value; }
    for (auto& [rc, value] : best) { auto [rr, cc] = rc; (void)rr; (void)cc; (void)value; }
    for (auto& kv : cnt) { (void)kv.first; (void)kv.second; }
    vector<int> keys;  for (auto& [key, _] : cnt) keys.push_back(key);
    cnt.erase(7);
    bool removed = cnt.erase(7);
    cnt.clear();
    assert(has && v == 4 && v3 == 4 && n == 3 && keys.size() == 3 && !removed && nested[1][2] == 3);
}
'''
CHECK = r'''
mt19937_64 rng(12345);
template <class K> K randKey(int range);
template <> int randKey<int>(int range) { return (int)(rng() % range) - range / 2; }
template <> ll randKey<ll>(int range) { return (ll)(rng() % range) * 1000000007LL - (ll)range * 500000000LL; }
template <> unsigned randKey<unsigned>(int range) { return (unsigned)(rng() % range) * 2654435761u; }
template <> char randKey<char>(int range) { return (char)(rng() % min(range, 120)); }
template <> pair<int, int> randKey<pair<int, int>>(int range) { return {(int)(rng() % range), (int)(rng() % 3)}; }
template <> pair<ll, ll> randKey<pair<ll, ll>>(int range) { return {(ll)(rng() % range) << 33, -(ll)(rng() % 3)}; }
template <> string randKey<string>(int range) {
    string s(rng() % (range < 50 ? 3 : 20), 'a');  // lengths across the 8-byte chunks, few letters so keys repeat
    for (auto& ch : s) ch = 'a' + rng() % (range < 50 ? 2 : 3);
    return s;
}

template <class K> void checkSet() {
    for (int rangeSize : {5, 50, 2000}) {
        hash_set<K> h; set<K> ref;
        for (int step = 0; step < 20000; step++) {
            K k = randKey<K>(rangeSize);
            int op = rng() % 4;
            if (op == 0) assert(h.insert(k).second == ref.insert(k).second);
            else if (op == 1) assert((bool)h.erase(k) == (bool)ref.erase(k));
            else assert((h.find(k) != h.end()) == (ref.count(k) > 0));
            assert(h.size() == ref.size());
        }
        set<K> got(h.begin(), h.end());
        assert(got == ref);
    }
}
template <class K> void checkMap() {
    for (int rangeSize : {5, 50, 2000}) {
        hash_map<K, ll> h; map<K, ll> ref;
        for (int step = 0; step < 20000; step++) {
            K k = randKey<K>(rangeSize);
            int op = rng() % 5;
            if (op == 0) { ll v = rng() % 100; h[k] = v; ref[k] = v; }
            else if (op == 1) { h[k]++; ref[k]++; }
            else if (op == 2) assert((bool)h.erase(k) == (bool)ref.erase(k));
            else {
                auto it = h.find(k); auto jt = ref.find(k);
                assert((it != h.end()) == (jt != ref.end()));
                if (it != h.end()) assert(it->second == jt->second);
            }
            assert(h.size() == ref.size());
        }
        map<K, ll> got;
        for (auto& [key, value] : h) got[key] = value;
        assert(got == ref);
    }
}
'''


def build(src, name, flags):
    path = f"/tmp/{name}.cpp"
    open(path, "w").write(src)
    r = subprocess.run(["g++", "-std=c++17", "-Wall", "-Wextra", *flags, "-o", f"/tmp/{name}", path], capture_output=True, text=True)
    if r.returncode or "warning" in r.stderr:
        sys.exit(f"FAIL {name}: compile\n{r.stderr[:2000]}")
    r = subprocess.run([f"/tmp/{name}"], capture_output=True, text=True, timeout=300)
    if r.returncode:
        sys.exit(f"FAIL {name}: exit {r.returncode}\n{r.stderr[:1500]}")
    return r.stdout


def main():
    hs = open(os.path.join(SRC, "hashSet.cpp")).read()
    hm = open(os.path.join(SRC, "hashMap.cpp")).read()
    types = ["int", "ll", "unsigned", "char", "pair<int, int>", "pair<ll, ll>", "string"]
    san = ["-fsanitize=address,undefined", "-O1"]
    body = "".join(f"    checkSet<{t}>();\n" for t in types)
    build(hs + SET_SYNTAX + CHECK.replace("template <class K> void checkMap", "template <class K> [[maybe_unused]] void checkMap").replace("hash_map<K, ll>", "map<K, ll>") +
          "int main() {\n    setSyntax();\n" + body + "}\n", "hashset_test", san)
    print("hashSet.cpp: every documented line compiles; matches std::set for " + ", ".join(types))
    body = "".join(f"    checkMap<{t}>();\n" for t in types)
    build(hm + MAP_SYNTAX + CHECK.replace("template <class K> void checkSet", "template <class K> [[maybe_unused]] void checkSet").replace("hash_set<K> h;", "set<K> h;") +
          "int main() {\n    mapSyntax();\n" + body + "}\n", "hashmap_test", san)
    print("hashMap.cpp: every documented line compiles; matches std::map for " + ", ".join(types))
    bench = hm + r'''
int main() {
    const int N = 4000000;
    mt19937_64 rng(1);
    vector<ll> keys(N);
    for (auto& k : keys) k = rng() % 1000000 * 1000003;
    auto timeIt = [&](auto& m, const char* name) {
        auto t0 = chrono::steady_clock::now();
        ll s = 0;
        for (ll k : keys) m[k]++;
        for (ll k : keys) { auto it = m.find(k); if (it != m.end()) s += it->second; }
        double ms = chrono::duration<double, milli>(chrono::steady_clock::now() - t0).count();
        printf("%-34s %7.0f ms  (checksum %lld)\n", name, ms, s);
    };
    unordered_map<ll, int> std1; timeIt(std1, "std::unordered_map<ll, int>");
    hash_map<ll, int> fast; timeIt(fast, "hash_map<ll, int>");
}
'''
    print(build(bench, "hash_bench", ["-O2"]).rstrip())


if __name__ == "__main__":
    main()
