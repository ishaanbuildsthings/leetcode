#include<bits/stdc++.h>
using namespace std;

int MOD = 1000000000 + 7;
static const int MAX_N = 1000000 + 5;
static const int ALPHA = 26;
bool isEnd[MAX_N]; // isEnd[node] tells us if this is the end of a word
int nxt[MAX_N][ALPHA]; // nxt[node][alpha] -> index of the next node, or -1 if it doesn't exist
int nextNode = 1; // pointer to next node we can insert, root is implicitly 0

void add(string word) {
    int node = 0;
    for (char c : word) {
        int cIdx = c - 'a';
        if (nxt[node][cIdx] == -1) {
            nxt[node][cIdx] = nextNode++;
        }
        node = nxt[node][cIdx];
    }
    isEnd[node] = true;
}

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);

    memset(isEnd, false, sizeof(isEnd));
    memset(nxt, -1, sizeof(nxt));
    

    string target;
    cin >> target;
    int k;
    cin >> k;
    for (int i = 0; i < k; i++) {
        string w;
        cin >> w;
        add(w);
    }

    int n = (int)target.size();

    vector<long long> dp(n + 1);
    dp[n] = 1;
    // dp[i] tells us how many ways we can build target[i:]
    for (int i = n - 1; i >= 0; i--) {
        int currNode = 0;
        int resHere = 0;
        for (int j = i; j < n; j++) {
            char c = target[j];
            int cIdx = c - 'a';
            if (nxt[currNode][cIdx] == -1) {
                break;
            }
            currNode = nxt[currNode][cIdx];
            if (isEnd[currNode]) {
                resHere += dp[j + 1];
                resHere %= MOD;
            }
        }
        dp[i] = resHere;
    }

    cout << dp[0];
}
