# Stress tests for the substring / multi-pattern string templates (../strings) against brute force: python3 test_substrings.py
import random, sys, os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "strings")
F={}
for n in ["countDistinctSubstrings","distinctSubstringsByLength","longestCommonSubstring","multiPatternCounts","multiPatternMatches","multiPatternLongestPrefixMatches","multiPatternLongestPrefixInText"]:
    e={}; exec(open(os.path.join(D,n+".py")).read(),e); F[n]=e[n]
def rs():
    n=random.choice([0,1,2,random.randint(0,10),random.randint(0,30)]); sg=random.choice([1,2,3,26])
    seq=[random.randrange(sg) for _ in range(n)]
    k=random.choice(["s","l","t"])
    return "".join(chr(97+x) for x in seq) if k=="s" else (seq if k=="l" else tuple(seq))
for it in range(5000):
    s=rs(); n=len(s)
    subs={tuple(s[i:j]) for i in range(n) for j in range(i+1,n+1)}
    assert F["countDistinctSubstrings"](s)==len(subs),s
    by=[0]*(n+1)
    for x in subs: by[len(x)]+=1
    assert F["distinctSubstringsByLength"](s)==by,s
    b=rs()
    best=(0,0,0)
    for j in range(len(b)):
        for i in range(n):
            L=0
            while i+L<n and j+L<len(b) and s[i+L]==b[j+L]: L+=1
            # brute tie: max length, then min start in b, then min start in a
            if L>best[0] or (L==best[0] and L>0 and (j,i)<(best[2],best[1])): best=(L,i,j)
    assert F["longestCommonSubstring"](s,b)==best,(s,b,best,F["longestCommonSubstring"](s,b))
    pats=[]
    for _ in range(random.randint(0,6)):
        if n and random.random()<0.6:
            a=random.randrange(n); pats.append(s[a:a+random.randint(0,4)])
        else: pats.append(rs()[:random.randint(0,4)])
    want=[[i for i in range(n+1) if i+len(p)<=n and tuple(s[i:i+len(p)])==tuple(p)] for p in pats]
    assert F["multiPatternMatches"](s,pats)==want,(s,pats)
    assert F["multiPatternCounts"](s,pats)==[len(w) for w in want],(s,pats)
    wantPrefix=[]
    for i in range(n):
        best=0
        for p in pats:
            L=0
            while L<len(p) and i+L<n and p[L]==s[i+L]: L+=1
            best=max(best,L)
        wantPrefix.append(best)
    assert F["multiPatternLongestPrefixMatches"](s,pats)==wantPrefix,(s,pats)
    allSubs={tuple(s[i:j]) for i in range(n+1) for j in range(i,n+1)}
    assert F["multiPatternLongestPrefixInText"](s,pats)==[max(L for L in range(len(p)+1) if tuple(p[:L]) in allSubs) for p in pats],(s,pats)
# mixed types
assert F["multiPatternCounts"]("abab",[["a","b"],("b",)])==[2,2]
print(F["countDistinctSubstrings"]("abab"),F["countDistinctSubstrings"]([-1,2,-1]),F["distinctSubstringsByLength"]("abab"),F["distinctSubstringsByLength"]([-1,2,-1]))
print(F["longestCommonSubstring"]("xabcdy","zzbcdq"),F["longestCommonSubstring"]([5,-1,2,7],[-1,2,9]))
print(F["multiPatternCounts"]("ababa",["aba","b","ab","zz"]),F["multiPatternCounts"]([-1,2,-1,2],[[-1,2],[2]]))
print(F["multiPatternMatches"]("ababa",["aba","b","ab","zz"]),F["multiPatternMatches"]([-1,2,-1,2],[[-1,2],[2]]))
print("ok")
