// https://leetcode.com/problems/making-file-names-unique/description/
// Difficulty: Medium

// Problem
/*
Given an array of strings names of size n. You will create n folders in your file system such that, at the ith minute, you will create a folder with the name names[i].

Since two files cannot have the same name, if you enter a folder name that was previously used, the system will have a suffix addition to its name in the form of (k), where, k is the smallest positive integer such that the obtained name remains unique.

Return an array of strings of length n where ans[i] is the actual name the system will assign to the ith folder when you create it.
*/

// Solution, O(n^2) time, O(n) space
/*
Store seen names. Each time we try to add a file, increment up to n previously added names. This could probably be sped up with some hashmap that maps to the highest number used so far for a prefix.
*/

var getFolderNames = function (names) {
  const seen = new Set();

  const result = [];

  for (let i = 0; i < names.length; i++) {
    if (!seen.has(names[i])) {
      seen.add(names[i]);
      result.push(names[i]);
      continue;
    }

    // if it does have the name, we iterate until a unique number is found
    let suffixNum = 1;
    while (true) {
      if (seen.has(`${names[i]}(${suffixNum})`)) {
        suffixNum++;
        continue;
      }
      seen.add(`${names[i]}(${suffixNum})`);
      result.push(`${names[i]}(${suffixNum})`);
      break;
    }
  }

  return result;
};
