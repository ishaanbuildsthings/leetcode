#include <bits/stdc++.h>
using ull = unsigned long long;

const int MAXN = 200003;
const int B = 64;

int levels; // height of tree
ull seg0[MAXN / B + 1]; // words in layer 0 (bottom)
ull seg1[MAXN / B / B + 1]; // words in layer 1
ull seg2[1]; // words in layer 2
ull* segs[3]; // pointers to segments
int segSizes[3]; // # of words at each level

static int arr[MAXN];
static int cnt[MAXN];

static char inBuf[1 << 22];
static int inPos = 0, inLen = 0;

// some IO stuff I ripped from online
inline int readChar() {
    if (inPos == inLen) {
        inLen = fread(inBuf, 1, sizeof(inBuf), stdin);
        inPos = 0;
        if (inLen == 0) return -1;
    }
    return inBuf[inPos++];
}

inline int readInt() {
    int c = readChar(), x = 0;
    while (c < '0') c = readChar();
    while (c >= '0') { x = x * 10 + c - '0'; c = readChar(); }
    return x;
}

static char outBuf[MAXN * 8];
static int outPos = 0;

inline void writeInt(int x) {
    if (x == 0) {
        outBuf[outPos++] = '0';
    } else {
        char tmp[12];
        int len = 0;
        while (x > 0) {
            tmp[len++] = '0' + (x % 10);
            x /= 10;
        }
        while (len > 0) outBuf[outPos++] = tmp[--len];
    }
    outBuf[outPos++] = ' ';
}

void fsBuild(int u) {
    int width = u;
    int lvl = 0;
    int sizes[3]; // number of words at a level
    while (true) {
        int numWords = (width + B - 1) / B;
        sizes[lvl++] = numWords;
        if (numWords == 1) break;
        width = numWords;
    }
    levels = lvl;
    segs[0] = seg0; segs[1] = seg1; segs[2] = seg2;
    // commit to the global
    for (int h = 0; h < levels; h++) {
        segSizes[h] = sizes[h];
    }
}

void fsInsert(int i) {
    for (int h = 0; h < levels; h++) {
        // i>>6 is i/64
        // i/64 tells us which word holds the bit we care about
        segs[h][i >> 6] |= (1ULL << (i & 63)); // do this instead of i<<? since i is an int
        i >>= 6; // walk up the tree
    }
}

void fsErase(int i) {
    ull carry = 0;
    for (int h = 0; h < levels; h++) {
        int idx = i >> 6;
        ull& v = segs[h][idx];
        v &= ~(1ULL << (i & 63));
        v |= (carry << (i & 63));
        carry = (v != 0);
        i = idx;
    }
}

int fsNext(int i) {
    for (int h = 0; h < levels; h++) {
        int idx = i >> 6;
        if (idx >= segSizes[h]) break;
        ull v = segs[h][idx] >> (i & 63);
        if (v) {
            int pos = i + __builtin_ctzll(v);
            for (int g = h - 1; g >= 0; g--) {
                pos = (pos << 6) + __builtin_ctzll(segs[g][pos]);
            }
            return pos;
        }
        i = idx + 1;
    }
    return -1;
}

int main() {
    int n = readInt(), k = readInt();
    int U = n + 1;
    for (int i = 0; i < n; i++) arr[i] = readInt();
    
    fsBuild(U);
    int fullWords = U / B;
    for (int w = 0; w < fullWords; w++) seg0[w] = ~0ULL; // bulk set an entire word, since everything is set at first
    int rem = U - fullWords * B;
    if (rem) seg0[fullWords] = (1ULL << rem) - 1;
    // propagate to upper levels
    for (int h = 1; h < levels; h++) {
        int childWords = segSizes[h - 1];
        int parentWords = segSizes[h];
        for (int p = 0; p < parentWords; p++) {
            ull mask = 0;
            int start = p * B;
            int end = start + B;
            if (end > childWords) end = childWords;
            for (int c = start; c < end; c++) {
                if (segs[h - 1][c]) mask |= (1ULL << (c - start));
            }
            segs[h][p] = mask;
        }
    }
    // populate the initial window
    for (int i = 0; i < k; i++) {
        int v = arr[i];
        if (v < U) {
            if (cnt[v]++ == 0) fsErase(v);
        }
    }
    
    writeInt(fsNext(0));
    
    for (int r = k; r < n; r++) {
        int gained = arr[r];
        int lost = arr[r - k];
        if (gained < U) {
            if (cnt[gained]++ == 0) fsErase(gained);
        }
        if (lost < U) {
            if (--cnt[lost] == 0) fsInsert(lost);
        }
        writeInt(fsNext(0));
    }
    outBuf[outPos++] = '\n';
    fwrite(outBuf, 1, outPos, stdout);
    return 0;
}