// LEETGOAT TEMPLATE!!!
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace __gnu_pbds;

typedef tree<
    int,                              // 1. Key type — what you store
    null_type,                        // 2. Mapped type — null = set, a type = map, there's no value attaached to each key, we are just storing keys in this case
    less<int>,                        // 3. Comparator — how elements are sorted
    rb_tree_tag,                      // 4. Tree tag — which tree implementation
    tree_order_statistics_node_update // 5. Node policy — the plugin, enables find_by_order(i) and order_of_key(x)
> ordered_set;

class SmallestInfiniteSet {
    ordered_set removed;
public:
    
    int popSmallest() {
        // binary search for the largest number where we have all 1...N
        int l = 0;
        int r = removed.size() - 1;
        int resIdx = -1;
        while (l <= r) {
            int m = (l + r) / 2;
            if (*removed.find_by_order(m) == m + 1) {
                resIdx = m;
                l = m + 1;
            } else {
                r = m - 1;
            }
        }
        removed.insert(resIdx + 2);
        return resIdx + 2;
    }
    
    void addBack(int num) {
        removed.erase(num);
    }
};

/**
 * Your SmallestInfiniteSet object will be instantiated and called as such:
 * SmallestInfiniteSet* obj = new SmallestInfiniteSet();
 * int param_1 = obj->popSmallest();
 * obj->addBack(num);
 */