// // option 1, rolling hash n+m time

// #include<bits/stdc++.h>
// using namespace std;

// const int BASE = 26;
// const int MOD = 998244353;
// const int MAX_N = 1000000 + 5;
// long long basePowMod[MAX_N]; // basePowMod[power] is (base ^ power) % MOD

// void initPows() {
//     basePowMod[0] = 1;
//     for (int power = 1; power < MAX_N; power++) {
//         basePowMod[power] = (basePowMod[power - 1] * BASE) % MOD;
//     }
// };

// struct Hasher {
//     long long windowHash = 0; // current hash value
//     int windowSize = 0;

//     void add(char c) {
//         windowHash *= BASE;
//         windowHash += c - 'a';
//         windowHash %= MOD;
//         windowSize++;
//     };
    
//     long long getHash() {
//         return windowHash;
//     }
    
//     int getSize() {
//         return windowSize;
//     }
    
//     void popLeft(char c) {
//         int leftPower = getSize() - 1;
//         long long leftContribution = ((c - 'a') * basePowMod[leftPower]) % MOD;
//         windowHash -= leftContribution;
//         if (windowHash < 0) windowHash += MOD;
//         windowSize--;
//     }
// };


// int main() {
//     initPows();

//     string haystack;
//     cin >> haystack;
//     string needle;
//     cin >> needle;
//     int n = (int)haystack.size();
//     int m = (int)needle.size();
//     if (m > n) {
//         cout << 0 << "\n";
//         return 0;
//     }

//     Hasher haystackHasher, needleHasher;
//     for (int i = 0; i < m; i++) {
//         haystackHasher.add(haystack[i]);
//         needleHasher.add(needle[i]);
//     }

//     long long needleHash = needleHasher.getHash();
//     int out = haystackHasher.getHash() == needleHash ? 1 : 0;
//     for (int r = m; r < n; r++) {
//         haystackHasher.add(haystack[r]);
//         haystackHasher.popLeft(haystack[r-m]);
//         if (haystackHasher.getHash() == needleHash) {
//             out++;
//         }
//     }
//     cout << out << "\n";
// }


// Solution 2, z function

/*
|0 1 2 3 4 5 6 7| 8  9 10 11 12 13 14 15 16| 17 18    [indices]
|a a b x a a b x| c |a a  b  x  a  a  b  x | a  y      z-box set 9-16 when we reached i=9
|0 1 0 0 4 1 0 0| 0  8 1  0  0  4?                    [z array]
         ^

now we try to solve at i=13, we are inside the z-box so we can re-use work
the corresponding k is k=4, which has a z score of 4

All we are saying is the z-box perfectly equals our prefix, and so we can use some of that work. We know the letter after the z-box
ending doesn't equal the letter after the prefix (index 17 doesn't equal index 8) but if we try to re-use work for index 13, it doesn't mean
index 17 cannot match index 4.

Also the reason we do z[i] = min(r - i + 1, z[k]) is literally all we have is the guarantee the prefix equals the z-box.
We don't know if any letters past match even if z[k] is really big because we don't know if our z-box right edge would keep matching the prefix.

Note if we started our for i loop at 0, we would initialize the z-box to 0:n-1 z[i] to n. Then for all future i we are inside the z-box and set z[i] to be 0 initially (set equal to z[k], which is the same as z[i], ends up being 0). Now nxt and pref are messed up and we loop fully inside n again.

*/

#include <bits/stdc++.h>
using namespace std;

// returns a z-function array for a string
vector<int> zFunction(string text) {
    vector<int> z(text.size());
    int l = 0;
    int r = 0;
    for (int i = 1; i < text.size(); i++) {
        // if we are inside the zbox, we could re-use some prior z value
        if (i <= r) {
            int k = i - l;
            z[i] = min(r - i + 1, z[k]);
            // if (z[i] == z[k] && z[i] < r - i + 1) continue; // This optional line shows if z[k] was the true minimum, z[i] cannot actually be greater and the code after becomes unnecessary
        }

        int nxt = z[i] + i;
        int pref = z[i];
        while (nxt < text.size() && text[nxt] == text[pref]) {
            z[i]++;
            nxt++;
            pref++;
        }

        if (nxt - 1 > r) {
            l = i;
            r = nxt - 1;
        }
    }
    return z;
};

// returns a list of indices in the text that fully match pattern
vector<int> patternMatch(string pattern, string text) {
    vector<int> res;
    string newString = pattern + "#" + text;
    auto z = zFunction(newString);
    for (int i = pattern.size() + 1; i < z.size(); i++) {
        if (z[i] == pattern.size()) {
            res.push_back(i - pattern.size() - 1);
        }
    }
    return res;
};

int main() {
    string text; cin >> text;
    string pattern; cin >> pattern;
    auto matches = patternMatch(pattern, text);
    cout << matches.size();
}