// https://leetcode.com/problems/maximum-number-of-removable-characters/description/
// Difficulty: Medium
// tags: binary search, subsequence

// Problem
/*
Simplfied:
We have a big string, s: 'abcacb'
a small one, p: 'ab'
and a list of indices, removable: [3,1,0]

We want to form the subsequence, p, from s, while removing as many letters as possible from s. If we remove k letters, we must remove them from left to right. So if k=2, we must remove letters at indices 3 and 1. Find the maximum k.
*/

// Solution, O(nk log n) time and O(k) space. k is the length of removable. We need k storage for storing the set, and k time inside each loop to iterate over removable and see which characters to remove.
/*
Do a binary search, so start by removing the first half from removable. Check if we can make a subsequence still by skipping over the characters we chose from removable. Here, we used l<=r. The goal was that normally in a binary search, we narrow it down to one last possible value, but then need to verify that value again after the loop ends, which is significantly extra code here because the verification process is long. So instead, we do l<=r to run it one extra time. Consider the last two elements [1, 2] and m is pointing at the ifrst. If it passes, we increment to [2], and if that passes, l goes past r and the loop stops, so r was right. But if it fails, r drops down and is right again.
*/

var maximumRemovals = function (s, p, removable) {
  let l = 0;
  let r = removable.length - 1;
  let m = Math.floor((r + l) / 2);
  while (l <= r) {
    m = Math.floor((r + l) / 2);
    const indicesToSkip = new Set();
    for (let i = 0; i <= m; i++) {
      indicesToSkip.add(removable[i]);
    }
    let pPointer = 0;
    for (let i = 0; i < s.length; i++) {
      if (indicesToSkip.has(i)) {
        continue;
      }
      if (p[pPointer] === s[i]) {
        pPointer++;
      }
    }
    // we could create it, try removing more
    if (pPointer === p.length) {
      l = m + 1;
    }
    // we could not create it, need to remove less
    else {
      r = m - 1;
    }
  }
  /* now r points to the last possible index of removable that could be the answer */
  return r + 1; // since we are returning a number not an index
};
