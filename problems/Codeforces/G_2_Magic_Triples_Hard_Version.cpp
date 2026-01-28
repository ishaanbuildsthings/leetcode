#include <bits/stdc++.h>
using namespace std;

long long nc3(long long n) {
    return n * (n - 1) * (n - 2) / 6;
}

const long long MAX_ELEMENT = 1000000000;
const int MAX_WITH_DIV = 1000000;

int spf[MAX_WITH_DIV + 1];

vector<int> factorize(int number) {
    vector<int> facs = {1};
    int curr = number;
    while (curr > 1) {
        int p = spf[curr];
        int length = facs.size();
        int currToPow = 1;
        while (curr % p == 0) {
            curr /= p;
            currToPow *= p;
            for (int i = 0; i < length; i++) {
                facs.push_back(facs[i] * currToPow);
            }
        }
    }
    return facs; 
}

void solve() {
    int n; cin >> n;
    unordered_map<long long,int> frq; frq.reserve(n + 5);
    vector<int> A(n);
    for (int i = 0; i < n; i++) {
        cin >> A[i];
        frq[A[i]]++;
    }
    long long out = 0;
    for (auto& kv : frq) {
        out += 6LL * nc3(kv.second);
    }
    unordered_map<long long,int> frqLeft; frqLeft.reserve(n + 5);
    sort(A.begin(), A.end());
    long long prevGain = 0;
    for (int i = 0; i < A.size(); i++) {
        int num = A[i];
        if (i > 0 && num == A[i - 1]) {
            out += prevGain;
            frqLeft[num]++;
            continue;
        }
        prevGain = 0;
        // we can iterate over divisors
        if (num <= MAX_WITH_DIV) {
            auto divs = factorize(num);
            for (auto div : divs) {
                if (div == 1) continue;
                int reqLeft = num / div;
                if (frqLeft.find(reqLeft) == frqLeft.end()) continue;
                long long reqRight = 1LL * num * div;
                if (frq.find(reqRight) == frq.end()) continue;
                if (reqRight > MAX_ELEMENT) continue;
                prevGain += frqLeft[reqLeft] * (frq[reqRight] - frqLeft[reqRight]);
            }
            out += prevGain;
        } else {
            int bigMult = MAX_ELEMENT / num + 5;
            for (int div = 2; div <= bigMult; div++) {
                if (num % div) continue;
                int reqLeft = num / div;
                if (frqLeft.find(reqLeft) == frqLeft.end()) continue;
                long long reqRight = 1LL * num * div;
                if (frq.find(reqRight) == frq.end()) continue;
                if (reqRight > MAX_ELEMENT) continue;
                long long leftChoices = frqLeft[reqLeft];
                long long rightChoices = frq[reqRight] - frqLeft[reqRight];
                prevGain += leftChoices * rightChoices;
            }
            out += prevGain;
        }
        frqLeft[num]++;
    }
    cout << out << '\n';
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    for (int div = 2; div <= MAX_WITH_DIV; div++) {
        if (spf[div]) continue;
        spf[div] = div;
        for (long long mult = 1LL * div * div; mult <= MAX_WITH_DIV; mult += div) {
            if (spf[mult] == 0) spf[mult] = div;
        }

    }
    int t; cin >> t;
    while (t--) {
        solve();
    }
}