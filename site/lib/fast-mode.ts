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
