// https://leetcode.com/problems/first-bad-version/description/
// Difficulty: Easy
// tags: binary search

// Solution
// O(log n) time and O(1) space. Use binary search, and look for the last good version. If the version is good, we need to look to the right, inclusive. If the version is bad, we need to look strictly to the left. Once we narrow it down to just `l`, check if that version is bad, which would mean no good versions. Otherwise `l` is good, so return `l+1`. We could have also scanned for the earliest bad version, so if the version is bad, we look left inclusive, if it is good we look strictly right. But here,

var solution = function (isBadVersion) {
  return function (n) {
    let l = 1;
    let r = n;
    let m = Math.ceil((r + l) / 2);
    while (l < r) {
      m = Math.ceil((r + l) / 2);
      // if this version is bad, we need to search all version to the left
      if (isBadVersion(m)) {
        r = m - 1;
      } else {
        l = m;
      }
    }

    // here, the only possible good version is l
    // but, l could be bad, if there are no good version, so we test that
    if (isBadVersion(l)) return l;

    // otherwise, l is good, so the first bad version is l + 1
    return l + 1;
  };
};

// [1,2,3,4,5]
//      ^   ^
