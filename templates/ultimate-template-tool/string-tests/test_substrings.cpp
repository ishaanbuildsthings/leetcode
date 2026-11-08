// Stress tests for the substring / multi-pattern string templates (../strings) against brute force:
// g++ -std=c++17 -O2 -fsanitize=address,undefined test_substrings.cpp -o t && ./t
#include "../strings/countDistinctSubstrings.cpp"
#include "../strings/distinctSubstringsByLength.cpp"
#include "../strings/longestCommonSubstring.cpp"
#include "../strings/multiPatternCounts.cpp"
#include "../strings/multiPatternMatches.cpp"
#include "../strings/multiPatternLongestPrefixMatches.cpp"
#include "../strings/multiPatternLongestPrefixInText.cpp"
mt19937 rng(7);
int rnd(int a,int b){return uniform_int_distribution<int>(a,b)(rng);}
#define CHECK(c) do{if(!(c)){cerr<<"FAIL "<<__LINE__<<" "#c<<endl;exit(1);}}while(0)
template<class T> T rs(int sg){int n=vector<int>{0,1,2,rnd(0,10),rnd(0,30)}[rnd(0,4)];T s;for(int i=0;i<n;i++)s.push_back('a'+rnd(0,sg-1));return s;}
template<class T> void run(){
 for(int it=0;it<5000;it++){
  int sg=vector<int>{1,2,3,26}[rnd(0,3)];
  T s=rs<T>(sg),b=rs<T>(sg);int n=s.size();
  set<T> subs;for(int i=0;i<n;i++)for(int j=i+1;j<=n;j++)subs.insert(T(s.begin()+i,s.begin()+j));
  CHECK(countDistinctSubstrings(s)==(long long)subs.size());
  vector<int> by(n+1,0);for(auto&x:subs)by[x.size()]++;CHECK(distinctSubstringsByLength(s)==by);
  tuple<int,int,int> best{0,0,0};
  for(int j=0;j<(int)b.size();j++)for(int i=0;i<n;i++){int L=0;while(i+L<n&&j+L<(int)b.size()&&s[i+L]==b[j+L])L++;
   auto&[bl,bi,bj]=best; if(L>bl||(L==bl&&L>0&&make_pair(j,i)<make_pair(bj,bi)))best={L,i,j};}
  CHECK(longestCommonSubstring(s,b)==best);
  vector<T> pats;int k=rnd(0,6);
  for(int q=0;q<k;q++){if(n&&rnd(0,9)<6){int a=rnd(0,n-1);int l=min(n-a,rnd(0,4));pats.push_back(T(s.begin()+a,s.begin()+a+l));}else{T p=rs<T>(sg);p.resize(min<int>(p.size(),rnd(0,4)));pats.push_back(p);}}
  vector<vector<int>> want;vector<int> wc;
  for(auto&p:pats){vector<int> w;for(int i=0;i+(int)p.size()<=n;i++)if(equal(p.begin(),p.end(),s.begin()+i))w.push_back(i);want.push_back(w);wc.push_back(w.size());}
  CHECK(multiPatternMatches(s,pats)==want);CHECK(multiPatternCounts(s,pats)==wc);
  vector<int> wp(n);for(int i=0;i<n;i++){int b=0;for(auto&p:pats){int L=0;while(L<(int)p.size()&&i+L<n&&p[L]==s[i+L])L++;b=max(b,L);}wp[i]=b;}
  CHECK(multiPatternLongestPrefixMatches(s,pats)==wp);
  vector<int> wt;for(auto&p:pats){int b=0;for(int L=0;L<=(int)p.size();L++){bool found=false;for(int i=0;i+L<=n&&!found;i++)if(equal(p.begin(),p.begin()+L,s.begin()+i))found=true;if(found)b=L;}wt.push_back(b);}
  CHECK(multiPatternLongestPrefixInText(s,pats)==wt);
 }}
int main(){run<string>();run<vector<long long>>();
 CHECK(multiPatternCounts(string("abab"),vector<vector<char>>{{'a','b'},{'b'}})==vector<int>({2,2}));
 CHECK(longestCommonSubstring(string("xabcdy"),vector<char>{'z','b','c','d'})==make_tuple(3,2,1));
 CHECK(countDistinctSubstrings(string("abab"))==7&&countDistinctSubstrings(vector<int>{-1,2,-1})==5);
 CHECK(distinctSubstringsByLength(vector<int>{-1,2,-1})==vector<int>({0,2,2,1}));
 CHECK(longestCommonSubstring(vector<int>{5,-1,2,7},vector<int>{-1,2,9})==make_tuple(2,1,0));
 CHECK(multiPatternMatches(vector<int>{-1,2,-1,2},vector<vector<int>>{{-1,2},{2}})==vector<vector<int>>({{0,2},{1,3}}));
 CHECK(multiPatternCounts(string("ababa"),vector<string>{"aba","b","ab","zz"})==vector<int>({2,2,2,0}));
 cout<<"cpp ok"<<endl;}
