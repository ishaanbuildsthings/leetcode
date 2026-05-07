#include <ext/pb_ds/assoc_container.hpp>
using namespace __gnu_pbds;

struct custom_hash {
    static uint64_t splitmix64(uint64_t x) {
        x += 0x9e3779b97f4a7c15;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
        x = (x ^ (x >> 27)) * 0x94d049bb133111eb;
        return x ^ (x >> 31);
    }
    size_t operator()(uint64_t x) const {
        static const uint64_t FIXED_RANDOM =
            chrono::steady_clock::now().time_since_epoch().count();
        return splitmix64(x + FIXED_RANDOM);
    }
};

template<class K, class V> using hash_map = gp_hash_table<K, V, custom_hash>;
template<class K>          using hash_set = gp_hash_table<K, null_type, custom_hash>;

// unordered map is now:
// hash_map<int, vector<int>> pos;

// unordered set is now:
// hash_set<int> seen;