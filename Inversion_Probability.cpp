#include <bits/stdc++.h>
#include <boost/multiprecision/cpp_int.hpp>

using namespace std;
using boost::multiprecision::cpp_int;

static cpp_int gcd_cppint(cpp_int a, cpp_int b) {
    if (a < 0) a = -a;
    if (b < 0) b = -b;
    while (b != 0) {
        cpp_int r = a % b;
        a = b;
        b = r;
    }
    return a;
}

struct Frac {
    cpp_int num = 0;
    cpp_int den = 1;

    void norm() {
        if (den < 0) { den = -den; num = -num; }
        cpp_int g = gcd_cppint(num, den);
        num /= g;
        den /= g;
    }

    void add(const cpp_int& n2, const cpp_int& d2) {
        // num/den + n2/d2
        cpp_int g = gcd_cppint(den, d2);
        cpp_int lden = (den / g) * d2;
        cpp_int a = lden / den;
        cpp_int b = lden / d2;
        num = num * a + n2 * b;
        den = lden;
        norm();
    }

    void div_int(long long k) {
        den *= k;
        norm();
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];

    Frac inversions; // starts at 0/1

    for (int i = 0; i < n; i++) {
        // expectedInversionsAtIndex as exact rational:
        // expectedInversionsAtIndex = (1 / A[i]) * sum_{size} bucket[size] / size
        vector<long long> bucket(101, 0);

        for (int v = 1; v <= A[i]; v++) {
            for (int L = i - 1; L >= 0; L--) {
                // the number on the left must be v+1...r_L to be bigger
                int size = A[L];
                int bigger = size - v;
                if (bigger <= 0) continue;
                bucket[size] += bigger;
            }
        }

        Frac expectedInversionsAtIndex; // 0/1
        for (int size = 1; size <= 100; size++) {
            if (bucket[size] == 0) continue;
            expectedInversionsAtIndex.add(cpp_int(bucket[size]), cpp_int(size));
        }
        expectedInversionsAtIndex.div_int(A[i]); // take the average based on all possible numbers this could have been

        inversions.add(expectedInversionsAtIndex.num, expectedInversionsAtIndex.den);
    }

    // round half to even at 6 decimals, exactly
    cpp_int scale = 1000000;
    cpp_int scaled_num = inversions.num * scale;

    cpp_int q = scaled_num / inversions.den;
    cpp_int rem = scaled_num % inversions.den;

    cpp_int twice = rem * 2;
    if (twice > inversions.den) {
        q += 1;
    } else if (twice == inversions.den) {
        if ((q & 1) != 0) q += 1; // ties to even
    }

    cpp_int whole = q / scale;
    cpp_int frac = q % scale;

    string whole_s = whole.convert_to<string>();
    string frac_s = frac.convert_to<string>();
    while ((int)frac_s.size() < 6) frac_s = "0" + frac_s;

    cout << whole_s << "." << frac_s << "\n";
    return 0;
}



// from decimal import Decimal, getcontext, ROUND_HALF_EVEN

// getcontext().prec = 50

// n = int(input())
// A = list(map(int, input().split()))

// inv = [Decimal(0)] * 101
// for s in range(1, 101):
//     inv[s] = Decimal(1) / Decimal(s)

// inversions = Decimal(0)
// for i in range(n):
//     expectedInversionsAtIndex = Decimal(0)
//     invAi = inv[A[i]]
//     for v in range(1, A[i] + 1):
//         for L in range(i - 1, -1, -1):
//             # the number on the left must be v+1...r_L to be bigger
//             size = A[L]
//             bigger = size - v
//             if bigger <= 0:
//                 continue
//             expectedInversionsAtIndex += Decimal(bigger) * inv[size]
//     expectedInversionsAtIndex *= invAi # take the average based on all possible numbers this could have been
//     inversions += expectedInversionsAtIndex

// print(inversions.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN))
