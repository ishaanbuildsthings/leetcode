import type { FillIn } from "@/components/TemplatePicker";

// The hash tables (templates/ultimate-template-tool/hash-tables/), C++ only, on the Misc tab. The drawer's Usage block
// shows the everyday syntax; the files hold every variant, checked by hash-tables-tests/test_hash_tables.py.
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/hash-tables/";

const SET_USAGE = `hash_set<int> s;                    // also hash_set<ll>, hash_set<pair<int, int>>, hash_set<string>

s.insert(5);                        // add 5
s.erase(5);                         // remove 5

if (s.find(5) != s.end()) { }       // 5 IS in s       (there's no s.count(5) or s.contains(5))
if (s.find(5) == s.end()) { }       // 5 is NOT in s

int n = s.size();                   // how many elements
bool none = s.empty();
s.clear();                          // remove everything

for (int x : s) { }                 // every element, in no particular order
for (auto [r, c] : cells) { }       // a hash_set<pair<int, int>> unpacks like this`;

const MAP_USAGE = `hash_map<string, int> m;            // keys: any integer type, pair of integers, or string; values: anything

m["apple"] = 3;                     // set a value (adds the key if it's new)
m["apple"]++;                       // a missing key starts at 0 (or empty for strings / vectors)

if (m.find("apple") != m.end()) { } // "apple" IS a key      (there's no m.count or m.contains)
if (m.find("apple") == m.end()) { } // "apple" is NOT a key  (don't check with m["apple"]: that ADDS it)

auto it = m.find("apple");          // read a value without adding the key:
if (it != m.end()) {                // "apple" IS a key: it points at its entry
    string key = it->first;         //   "apple"
    int value = it->second;         //   its value
} else {                            // "apple" is NOT a key (it == m.end()): nothing to read, and nothing was added
}

m.erase("apple");                   // remove a key
int n = m.size();                   // how many keys

for (auto& [key, value] : m) { }    // keys and values, in no particular order
for (auto& [key, _] : m) { }        // just keys
for (auto& [_, value] : m) { }      // just values`;

export const HASH_TABLES: FillIn[] = [
  {
    label: "Hash set (C++) O(1)",
    title: "hash_set<K>: about 3x faster than an unhackable std::unordered_set. Keys: any integer type, a pair of integers, or string",
    folder: "_hash-tables",
    file: "hashSet",
    langs: ["cpp"],
    ops: [
      ["insert: add an element", "1"],
      ["erase: remove an element", "1"],
      ["check whether an element is in the set", "1"],
      ["size", "1"],
      ["loop over every element", "N"],
    ],
    usage: { cpp: SET_USAGE },
    githubUrl: GITHUB,
  },
  {
    label: "Hash map (C++) O(1)",
    title: "hash_map<K, V>: about 3x faster than an unhackable std::unordered_map. Keys: any integer type, a pair of integers, or string; values: anything",
    folder: "_hash-tables",
    file: "hashMap",
    langs: ["cpp"],
    ops: [
      ["set or update a value", "1"],
      ["check whether a key is in the map", "1"],
      ["read a value without adding the key", "1"],
      ["erase: remove a key", "1"],
      ["size", "1"],
      ["loop over keys and values", "N"],
    ],
    usage: { cpp: MAP_USAGE },
    githubUrl: GITHUB,
  },
];
