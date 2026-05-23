#include <bits/stdc++.h>
using namespace std;

int n;
const int MAXN = 1e5;
// string words[MAXN];

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> n;
    string longSubseq = "";
    for (int i=0;i<n;i++) {
      string w;
      cin >> w;
      w = "<3" + w;
      longSubseq += w;
    }
    longSubseq += "<3";
    // cout << longSubseq;

    string text;
    cin >> text;

    // cout << text;
    // cout << "long subseq: " << longSubseq << endl;

    // check if longSubseq is a subsequence of text

    int i = 0;
    int j = 0;
    while (i < (int)text.size()) {
      if (longSubseq[j] == text[i]) {
        i += 1;
        j += 1;
        if (j == (int)longSubseq.size()) {
          cout << "yes";
          return 0;
        }
        continue;
      }
      i += 1;
    }

    cout << "no";
    return 0;

    // // print
    // cout << "print:" << endl;
    // for (int i = 0; i < n; i++) {
    //   cout << words[i] << "\n";
    // }
}