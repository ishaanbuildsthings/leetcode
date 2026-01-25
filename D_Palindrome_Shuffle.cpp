#include <bits/stdc++.h>
using namespace std;

void solve() {
    string s; cin >> s;
    cout << "============" << endl << "s=" << s << endl;
}

int main() {
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}


ac | b(ac)d  dacb | ca

# we are at C
if c+1...mirror is not a palindrome, we give up since we are flipping before that

# what is the longest prefix that equals the suffix?
# it is 2, we should not encroach on the first 2
# if that prefix already equals the suffix dont touch it

we could flip anywhere from 3...i 

we should flip the most possible 