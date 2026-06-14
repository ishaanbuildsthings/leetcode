// ADAINDEX - Ada and Indexing
// #trie-1

// Ada the Ladybug has many things to do and almost no time. She wants to to save time while searching for something so she have decided to make a search engine.

// She has many words in her TODO list. It costs her precious time to find out, whether a word is in it so she seeks your help. You will get list and some queries. You will be asked, to find out how many words in TODO list have a word as prefix.

// Input
// The first line contains N, Q: the number words in TODO list and number of queries.

// N lines follow, with words (of TODO list) consisting of lowercase letters. The sum of their lengths won't be greater than 106

// Q lines follow, with words (queries) consisting of lowercase letters. The sum of their lengths won't be greater than 106

// Output
// For each query print the number of words in TODO list which have actual word as prefix.

// Example Input
// 12 6
// bulldog
// dog
// dogged
// doggedly
// doggerel
// dogma
// dogmatic
// dogmatism
// dogs
// catastroph
// catastroph
// doctor
// cat
// dog
// dogg
// do
// doctrinography
// dogge


#include <bits/stdc++.h>
using namespace std;

// ⚠️ Not constant factor optimized, using vector instead of array
// ⚠️ Missing methods probably
// ✅

struct Trie {
  struct Node {
    int nxt[26]; // nxt[letterIndex] -> index of next node in Trie's shared pool, -1 means no child
    int pass = 0;
    int end = 0;
    Node() { fill(begin(nxt), std::end(nxt), -1); }
  };

  vector<Node> pool;

  Trie (size_t maxConcurrentNodes) {
    pool.reserve(maxConcurrentNodes); // no resizing required
    pool.emplace_back(); // assign root
  }

  int newNode() {
    pool.emplace_back();
    return (int)pool.size() - 1;
  }

  // adds (or deletes, delta=-1) a word in O(word) time
  void insert(const string &word, int delta=1) {
    int currI = 0;
    pool[currI].pass += delta;

    for (char c : word) {
      int charI = c - 'a';
      if (pool[currI].nxt[charI] == -1) {
        pool[currI].nxt[charI] = newNode();
      }
      currI = pool[currI].nxt[charI];
      pool[currI].pass += delta;
    }
    pool[currI].end += delta;
  }

  // deletes a word in O(word) time
  void remove(const string &word) {
    insert(word, -1);
  }

  // gets how many words have a prefix in O(pref) time
  int prefCount(const string &pref) {
    int currI = 0;
    for (char c : pref) {
      int cI = c - 'a';
      if (pool[currI].nxt[cI] == -1) {
        return 0;
      }
      currI = pool[currI].nxt[cI];
    }
    return pool[currI].pass;
  }

  // gets how many times `word` appears in the structure
  int count(const string &word) {
    int currI = 0;
    for (char c : word) {
      int cI = c - 'a';
      if (pool[currI].nxt[cI] == -1) {
        return 0;
      }
      currI = pool[currI].nxt[cI];
    }
    return pool[currI].end;
  }

};

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, q;
  cin >> n >> q;
  Trie t = Trie(1'000'005);
  for (int i = 0; i < n; i++) {
    string word;
    cin >> word;
    t.insert(word);
  }
  for (int i = 0; i < q; i++) {
    string pref;
    cin >> pref;
    int withPref = t.prefCount(pref);
    cout << withPref << endl;
  }
  return 0;
}


