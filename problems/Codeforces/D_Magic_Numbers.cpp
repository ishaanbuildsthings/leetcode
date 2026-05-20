#include <bits/stdc++.h>
using namespace std;

long long m, d;
string aStr, bStr;
const int MOD = 1000000007;

vector<int> memo;
vector<array<int,10>> nxt; // pre-computed (rem*10+dig)%m

// generate key
inline int idx(int i, int nstarted, int isTight, int remainder, int isOdd) {
    long long x = i;
    x = x * 2 + nstarted;
    x = x * 2 + isTight;
    x = x * m + remainder;
    x = x * 2 + isOdd;
    return (int)x;
}

int dfs(int i, int nstarted, int isTight, int remainder, int isOdd,
        const string& strNum) {
    int id = idx(i,nstarted,isTight,remainder,isOdd);
    int v = memo[id];
    if (v != -2) return v;

    int n = (int)strNum.size();
    if (i == n) {
        memo[id] = (nstarted && remainder == 0) ? 1 : 0;
        return memo[id];
    }

    int upper = isTight ? (strNum[i]-'0') : 9;
    long long res = 0;

    for (int nextDigit = 0; nextDigit <= upper; ++nextDigit) {
        int newStarted = nstarted || nextDigit > 0;
        if (newStarted) {
            if (isOdd) {
                if (nextDigit == d) continue;
            } else {
                if (nextDigit != d) continue;
            }
        }

        int newTight = isTight && (nextDigit == upper);
        int newRemainder = nxt[remainder][nextDigit];
        int newOdd = newStarted ? !isOdd : 1;

        res += dfs(i+1,newStarted,newTight,newRemainder,newOdd,strNum);
        if (res >= MOD) res -= MOD;
    }
    memo[id] = (int)res;
    
    return memo[id];
}

int countStr(const string& strNum){
    int n = (int)strNum.size();
    long long tot = 1LL*(n+1)*2*2*m*2;
    memo.assign((size_t)tot,-2);
    return dfs(0,0,1,0,1,strNum);
}

string stringMinusOne(string s){
    int i = (int)s.size() - 1;
    while(i>=0 && s[i]=='0'){
        s[i]='9'; --i;
    }
    if(i>=0) --s[i];
    
    int pos=0; while(pos+1<(int)s.size() && s[pos]=='0') ++pos;
    
    return s.substr(pos);
}

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin>>m>>d;
    cin>>aStr>>bStr;

    nxt.resize(m);
    for(int r=0; r < m; ++r)
        for(int dig=0; dig < 10; ++dig)
            nxt[r][dig] = (r * 10 + dig) %m;

    int high=countStr(bStr);
    int low =countStr(stringMinusOne(aStr));
    cout<<((high-low) % MOD + MOD) % MOD<<'\n';
    return 0;
}