#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, m; cin >> n >> m;
    vector<int> A(n); for (int i = 0; i < n; i++) {
        cin >> A[i];
    }
    vector<int> B(m); for (int i = 0; i < m; i++) {
        cin >> B[i];
    }

    int MX = 10000000;
    vector<int> spf(MX + 1); // spf[1] -> 0, spf[prime] = prime
    for (int div = 2; div <= MX; div++) {
        if (spf[div]) continue;
        spf[div] = div;
        for (long long mult = 1LL * div * div; mult <= MX; mult += div) {
            if (spf[mult] == 0) spf[mult] = div;
        }
    }

    auto primeFactorizeWithMultiples = [&](int v) -> vector<int> {
        vector<int> primeFactors;
        int curr = v;
        while (curr > 1) {
            int p = spf[curr];
            primeFactors.push_back(p);
            curr /= p;
        }
        return primeFactors;
    };

    unordered_set<int> allPrimes;
    unordered_map<int,int> acnt;
    unordered_map<int,int> bcnt;

    for (auto x : A) {
        auto facs = primeFactorizeWithMultiples(x);
        for (auto fac : facs) {
            allPrimes.insert(fac);
            acnt[fac]++;
        }
    }
    for (auto x : B) {
        auto facs = primeFactorizeWithMultiples(x);
        for (auto fac : facs) {
            allPrimes.insert(fac);
            bcnt[fac]++;
        }
    }
    // how many copies of each prime factor are in each array ^
    // if 5 are in A and 3 are in B we nee to remove 3 from both

    // now convert acnt and bcnt to be trackers for how many more need to be removed
    for (auto prime : allPrimes) {
        int small = min(acnt[prime], bcnt[prime]);
        acnt[prime] = small;
        bcnt[prime] = small;
    }

    vector<int> outA = A;
    vector<int> outB = B;
    for (int i = 0; i < outA.size(); i++) {
        int num = outA[i];
        int finalNum = num;
        while (num > 1) {
            int p = spf[num];
            int e = 0;
            while (num % p == 0) {
                num /= p;
                e++;
            }
            int canRemove = min(acnt[p], e);
            finalNum /= pow(p, canRemove);
            acnt[p] -= canRemove;
        }
        outA[i] = finalNum;
    }
    for (int i = 0; i < outB.size(); i++) {
        int num = outB[i];
        int finalNum = num;
        while (num > 1) {
            int p = spf[num];
            int e = 0;
            while (num % p == 0) {
                num /= p;
                e++;
            }
            int canRemove = min(bcnt[p], e);
            finalNum /= pow(p, canRemove);
            bcnt[p] -= canRemove;
        }
        outB[i] = finalNum;
    }

    cout << outA.size() << " " << outB.size() << endl;
    for (auto x : outA) {
        cout << x << " ";
    }
    cout << endl;
    for (auto x : outB) {
        cout << x << " ";
    }
    cout << endl;

    // gather all prime factors in A and their counts, and in B
    // for every overlap, we can deduct one from each

    // 2 5 10 20 -> 2 2 2 2 5 5 5
    // 100 1 3 -> 2 2 3 5 5
    // overlap -> 2 2 5 5
    // final numerator -> 2 2 5
    // final denominator -> 3

    // 100 5 2 -> 2 2 2 5 5 5
    // 50 10 -> 2 2 5 5 5
    // final numerator -> 2
    // final denominator -> 1
}