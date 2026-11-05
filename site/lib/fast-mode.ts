// What the Fast mode panel says, shared by the pickers.
export const FAST_DRAWBACKS = [
  "Harder to debug on LeetCode since sanitizers are skipped",
  "Needs GCC or Clang, and C++17",
];
export const FAST_NO_SANITIZE = [
  { text: "Does nothing on other platforms, so you can ignore it there." },
  {
    text: "We can put this on the main function:",
    code: `public:
    LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) { // put at the start here`,
  },
  {
    text: "Any inner lambda can use it too:",
    code: "auto fn = [&](auto&& self, int x) LEETCODE_NO_SANITIZE -> void { ... };",
  },
];

// The generics: you write part of the hot code yourself, so the panel shows where the macro goes in it.
export const GENERIC_FAST = {
  how: "Sanitizers are skipped in the tree and in the functions you fill in. The gain only shows up on LeetCode.",
  drawbacks: FAST_DRAWBACKS,
  noSanitize: [
    FAST_NO_SANITIZE[0],
    {
      text: "It's already on every function you fill in, so keep it there:",
      code: "LEETCODE_NO_SANITIZE Node combine(const Node& left, const Node& right) {",
    },
    {
      text: "It doesn't carry into what a function calls, so put it on any helper you add:",
      code: "LEETCODE_NO_SANITIZE long long addMod(long long a, long long b) {",
    },
    {
      text: "And on a Node or Tag constructor:",
      code: `struct Node {
    int cnt[26];
    LEETCODE_NO_SANITIZE Node() { ... }
};`,
    },
    ...FAST_NO_SANITIZE.slice(1),
  ],
};
