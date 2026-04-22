vector<int> arr;
vector<int> pf;
 
struct TrieNode {
  int count; // how many are in subtree
  TrieNode* child[2];
 
  TrieNode() {
    count = 0;
    child[0] = child[1] = nullptr;
  }
};
 
class BitTrie {
  private:
    TrieNode* root;
    int maxBit;
  public:
    BitTrie(int maxBit_) {
      root = new TrieNode();
      maxBit = maxBit_;
    }
 
    void insert(int num) {
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
 
    void remove (int num) {
      TrieNode* curr = root;
      root->count--;
      for (int i=maxBit;i>=0;i--) {
        int bit = num >> i & 1;
        curr = curr->child[bit];
        curr->count--;
      }
    }
 
    int maxXor (int num) {
      TrieNode* curr = root;
      int res = 0;
      for (int i=maxBit;i>=0;i--) {
        int bit = num >> i & 1;
        int want = bit^1;
        if (curr->child[want] && curr->child[want]->count) {
          curr = curr->child[want];
          res += 1 << i;
        } else {
          curr = curr->child[bit];
        }
      }
      return res;
    }
};
 
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> n;
    arr.resize(n);
    for (int i=0;i<n;i++) cin >> arr[i];
    int curr = 0;
    for (int v : arr) {
      curr ^= v;
      pf.push_back(curr);
    }
    BitTrie t = BitTrie(30);
    for (int v : pf) {
      t.insert(v);
    }
    t.insert(0); // empty prefix
    int res = 0;
    for (int v : pf) {
      // cout << "v: " << v << endl;
      res = max(res, t.maxXor(v));
      // cout << "res now: " << res << endl;
    }
    res = max(res, t.maxXor(0));
    cout << res;
    return 0;
}