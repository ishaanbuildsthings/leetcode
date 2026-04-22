#include <bits/stdc++.h>
using namespace std;

// ⚠️ Not constant factor optimized
// ⚠️ Missing methods
// ✅ Used to solve https://cses.fi/problemset/task/1655/

// All O(maxBits)
// Insert number
// Remove number
// Query k-th largest XOR of `num` against a number in the trie
// Query k-th smallest XOR of `num` against a number in the trie


// We can also do common seg tree operations, such as # of elements <= R but they're O(maxBits) which is worse than other structures

struct TrieNode {
  int count; // how many are in subtree
  TrieNode* child[2];

  TrieNode() {
    count = 0; // stores the count of numbers in this subtree
    child[0] = child[1] = nullptr;
  }
};

class BitTrie {
  private:
    using ll = long long;
    TrieNode* root;
    int maxBit;
  public:
    BitTrie(int maxBit_) {
      root = new TrieNode();
      maxBit = maxBit_;
    }

    // O(maxBits) time to insert
    void insert(ll num) {
      TrieNode* curr = root;
      root->count++;
      for (int i=maxBit;i>=0;i--) {
        int bit = num >> i & 1;
        if (!curr->child[bit]) {
          curr->child[bit] = new TrieNode();
        }
        curr = curr->child[bit];
        curr->count++;
      }
    }

    // O(maxBits) time to remove a number
    void remove(ll num) {
      TrieNode* curr = root;
      root->count--;
      for (int i=maxBit;i>=0;i--) {
        int bit = num >> i & 1;
        curr = curr->child[bit];
        curr->count--;
      }
    }

    // O(maxBits) gets the max XOR of a num against all numbers in the trie
    ll maxXor(ll num) {
      return kthXor(num, 1);
    }

    // ⚠️ Not tested
    // O(maxBits) gets the kth largst XOR of num against one of the elements in thetrie
    ll kthXor(ll num, int k) {
      if (k <= 0 || k > root->count) return -1;
      TrieNode* cur = root;
      ll result = 0;
      for (int b = maxBit; b >= 0; --b) {
        if (!cur) break;
        int bit = (num >> b) & 1;
        int want = bit ^ 1;
        int cntWant = cur->child[want] ? cur->child[want]->count : 0;
        if (k <= cntWant) {
          result |= (1LL << b);
          cur = cur->child[want];
        } else {
          k -= cntWant;
          cur = cur->child[bit];
        }
      }
      return result;
    }

  // ⚠️ Not tested
  // O(maxBits) gets the minimum XOR of num against some number in the trie
  ll minXor(ll num) {
    return kthSmallestXor(num, 1);
  }

  // ⚠️ Not tested
  // O(maxBits) gets the kth smallest XOR of num against some number in thetrie
  ll kthSmallestXor(ll num, int k) {
    if (k <= 0 || k > root->count) return -1;
    TrieNode* cur = root;
    ll res = 0;
    for (int b = maxBit; b >= 0; --b) {
      int bit = (num >> b) & 1;
      int cntMatch = cur->child[bit] ? cur->child[bit]->count : 0;
      if (k <= cntMatch) {
        cur = cur->child[bit];
      } else {
        k -= cntMatch;
        res |= (1LL << b);
        cur = cur->child[bit ^ 1];
      }
    }
    return res;
  }
};

int n;
vector<long long> arr;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> n;
    for (int i=0;i<n;i++) {
      long long tmp;
      cin >> tmp;
      arr.push_back(tmp);
    }
  BitTrie trie = BitTrie(50);

  // our bit trie will hold every pref XOR, we iterate on the suff XOR and compare it
  vector<long long> pfXor;
  long long curr = 0;
  for (int i = 0; i < n; i++) {
    curr ^= arr[i];
    pfXor.push_back(curr);
    trie.insert(curr);
  }
  trie.insert(0);

  long long suffXor = 0;
  long long res = 0;
  for (int i = arr.size() - 1;i>=0;i--) {
    // compare our suff XOR to all in pref
    long long best = trie.maxXor(suffXor);
    res = max(res, best);
    suffXor ^= arr[i];
    trie.remove(pfXor[i]);

  }

  cout << res;

}