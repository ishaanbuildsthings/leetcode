// https://leetcode.com/problems/substring-with-largest-variance/description/
// Difficulty: Hard
// tags: sliding window variable, kadane's (can be both)

// Problem
/*
The variance of a string is defined as the largest difference between the number of occurrences of any 2 characters present in the string. Note the two characters may or may not be the same.

Given a string s consisting of lowercase English letters only, return the largest variance possible among all substrings of s.

A substring is a contiguous sequence of characters within a string.
*/

// Solution, O(length) time, O(1) space
/*
To find the variance, we can consider 26*26 possible letter pairs. So we solve each pair individually in n time, with a sliding window. We slide, and as long as we have the minor character at least once, we update the result. When the minor exceeds the major, we decrement, until only 1 minor is left. There were some annoying cases in this one, kind of a more difficult kadane's.
*/

var largestVariance = function (s) {
  let result = 0;

  for (const minor of "abcdefghijklmnopqrstuvwxyz") {
    for (const major of "abcdefghijklmnopqrstuvwxyz") {
      let minorCount = 0;
      let majorCount = 0;
      let l = 0;
      let r = 0;
      // if we hit a minor surplus, for instance in aba, we have to start decrementing, unless it is our only minor. so something like a is okay, since we need one a. this lets us see the substring abbbb. but if we have abbbaaa, we should decrement down to the last a
      while (r < s.length) {
        // skip irrelevant letters
        if (s[r] !== minor && s[r] !== major) {
          r++;
          continue;
        }

        if (s[r] === minor) {
          minorCount++;
        } else if (s[r] === major) {
          majorCount++;
        }

        // if we get to a new letter, it is either a minor or a major one

        /*
                if it is a minor character, a few things can happen:

                1) we have something like bbbbba, that's fine, we take the minor character due to the positive prefix
                2) we have something like abbbba, since we started on a, we could remove it. so we decrement from the left until we delete the first a, if there is one. we never delete a major.

                but we only do this while we have more than one minor letter, for instance in ba, or even just a, we can't delete the leftmost minor letter, since we need at least one
                */
        while (minorCount > 1 && s[l] !== major) {
          const lostChar = s[l];
          if (lostChar === minor) minorCount--;
          l++;
        }

        /*
            what if the new minor character makes our prefic useless? bbaaa, then we just reset to that new minor letter
            */
        if (minorCount > majorCount && minorCount > 1) {
          l = r;
          minorCount = 1;
          majorCount = 0;
        }

        // update result, as long as we have a minor character
        if (minorCount >= 1) {
          result = Math.max(result, majorCount - minorCount);
        }

        r++;
      }
    }
  }

  return result;
};
