// from collections import defaultdict
// n, target = map(int, input().split())
// A = list(map(int, input().split()))

// pfSumToPairs = defaultdict(set)
// suffSumToPairs = defaultdict(set)
// for i in range(n):
//     for j in range(i + 1, n):
//         tot = A[i] + A[j]
//         suffSumToPairs[tot].add((i, j))

// for i in range(n):
//     for j in range(i + 1, n):
//         tot = A[i] + A[j]
//         suffSumToPairs[tot].remove((i, j))
//     for j in range(i):
//         tot = A[i] + A[j]
//         pfSumToPairs[tot].add((i, j))
//     for j in range(i):
//         pairSum = A[i] + A[j]
//         req = target - pairSum
//         if suffSumToPairs[req]:
//             pfPairs = list(pfSumToPairs[pairSum])
//             suffPairs = list(suffSumToPairs[req])
//             ans = [pfPairs[0][0] + 1, pfPairs[0][1] + 1, suffPairs[0][0] + 1, suffPairs[0][1] + 1]
//             print(*ans)
//             exit()

// print('IMPOSSIBLE')


#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
using namespace std;
using namespace __gnu_pbds;
using ll = long long;

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
    size_t operator()(uint64_t x) const { return splitmix64(x + fixed_random()); }
    size_t operator()(int x) const { return splitmix64((uint64_t)x + fixed_random()); }
    size_t operator()(long long x) const { return splitmix64((uint64_t)x + fixed_random()); }
    template<class A, class B>
    size_t operator()(const pair<A,B>& p) const {
        return splitmix64((uint64_t)p.first * 0x9E3779B97F4A7C15ULL + (uint64_t)p.second + fixed_random());
    }
};

template<class K, class V> using hash_map = gp_hash_table<K, V, custom_hash>;
template<class K>          using hash_set = gp_hash_table<K, null_type, custom_hash>;

struct PairSet { hash_set<pair<int,int>> s; };

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n; ll target;
    cin >> n >> target;
    vector<ll> A(n);
    for (auto& v : A) cin >> v;

    hash_map<ll, PairSet> pfSumToPairs;
    hash_map<ll, PairSet> suffSumToPairs;

    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            suffSumToPairs[A[i] + A[j]].s.insert({i, j});

    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++)
            suffSumToPairs[A[i] + A[j]].s.erase({i, j});
        for (int j = 0; j < i; j++)
            pfSumToPairs[A[i] + A[j]].s.insert({i, j});
        for (int j = 0; j < i; j++) {
            ll req = target - (A[i] + A[j]);
            auto it = suffSumToPairs.find(req);
            if (it != suffSumToPairs.end() && !it->second.s.empty()) {
                auto pf = *pfSumToPairs[A[i] + A[j]].s.begin();
                auto sf = *it->second.s.begin();
                cout << pf.first + 1 << " " << pf.second + 1 << " "
                     << sf.first + 1 << " " << sf.second + 1 << "\n";
                return 0;
            }
        }
    }

    cout << "IMPOSSIBLE\n";
    return 0;
}