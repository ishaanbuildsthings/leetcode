#include <bits/stdc++.h>
using namespace std;
const long long MOD = 998244353;

#include <bits/stdc++.h>
using namespace std;

struct CombModPrime {
    long long MOD;
    int maxN;
    vector<long long> fact, invFact;

    CombModPrime(int maxN, long long mod) : MOD(mod), maxN(maxN) {
        fact.assign(maxN + 1, 1);
        invFact.assign(maxN + 1, 1);

        for (int i = 1; i <= maxN; i++) fact[i] = fact[i - 1] * i % MOD;
        invFact[maxN] = modPow(fact[maxN], MOD - 2);
        for (int i = maxN; i >= 1; i--) invFact[i - 1] = invFact[i] * i % MOD;
    }

    long long modPow(long long a, long long e) const {
        long long r = 1 % MOD;
        a %= MOD;
        while (e > 0) {
            if (e & 1) r = (__int128)r * a % MOD;
            a = (__int128)a * a % MOD;
            e >>= 1;
        }
        return r;
    }

    long long C(int n, int k) const {
        if (k < 0 || k > n) return 0;
        return fact[n] * invFact[k] % MOD * invFact[n - k] % MOD;
    }
};


int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, k; cin >> n >> k;
    vector<pair<int,int>> ranges(n);
    for (int i = 0; i < n; i++) {
        int l, r; cin >> l >> r;
        ranges[i] = {l, r};
    }
    sort(ranges.begin(), ranges.end());

    vector<int> lefts;
    lefts.reserve(n);
    for (auto [l, r] : ranges) lefts.push_back(l);

    sort(lefts.begin(), lefts.end());
    lefts.erase(unique(lefts.begin(), lefts.end()), lefts.end());

    multiset<int> rights;

    CombModPrime modder(n + 10, MOD);

    // new idea
    // scan lamps by starting point
    // for a given point we have some amount of lamps before us that still have endings >= our current i
    // we can use some of those lamps to intersect at our i, but we cannot use all of them because it would duplicate combinations
    // we iterate, we use 1 lamp starting at this point, 2, etc, it amortizes
    unordered_map<int,vector<int>> leftFrq; // maps left -> rights
    for (auto r : ranges) {
        leftFrq[r.first].push_back(r.second);
    }

    long long out = 0;

    for (int i = 0; i < lefts.size(); i++) {
        int left = lefts[i];
        int leftFrqHere = leftFrq[left].size();
        // cout << "unique left is: " << left << endl;
        rights.erase(rights.begin(), rights.lower_bound(left)); // remove all rights that ended already
        // cout << "rights still overlapping: " << rights.size() << endl;
        for (int takeHere = 1; takeHere <= min(k, leftFrqHere); takeHere++) {
            // ways to take takeHere from this group
            long long ways = modder.C(leftFrqHere, takeHere);
            int reqToTake = k - takeHere;
            long long waysBefore = modder.C(rights.size(), reqToTake);
            long long ways2 = ways * waysBefore;
            ways2 %= MOD;
            out += ways2;
            out %= MOD;
        }
        for (auto rightEdge : leftFrq[left]) {
            rights.insert(rightEdge);
        }

    }
    cout << out;
    
}

// 5 7 6
// if we take only 7 we are take take and +7
// if we take 5 and 6 and lose 7 we are take take and +4