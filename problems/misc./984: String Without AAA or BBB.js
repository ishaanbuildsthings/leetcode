// https://leetcode.com/problems/string-without-aaa-or-bbb/description/
// Difficulty: Medium

// Problem
/*
Simplified:
Input: a = 1, b = 2
Output: "abb"
Explanation: "abb", "bab" and "bba" are all correct answers.

Detailed:
Given two integers a and b, return any string s such that:

s has length a + b and contains exactly a 'a' letters, and exactly b 'b' letters,
The substring 'aaa' does not occur in s, and
The substring 'bbb' does not occur in s.
*/

// Solution: O(a+b) time and O(a+b) space
/*
We can be greedy, if we need to use up more a's than b's, it's always favorable to add an 'a', as long as it doesn't violate the triple rule. So we add an 'a', then decrement the amount of a's left we need. If we have more a's than b's, but we already used 2, we are forced to use a b. Do the same for the b's. We used an array so we don't duplicate a lot of strings, and join it at the end.
*/
var strWithout3a3b = function (a, b) {
  let aLeft = a;
  let bLeft = b;
  const arr = [];
  while (arr.length < a + b) {
    if (aLeft >= bLeft) {
      if (arr[arr.length - 1] === "a" && arr[arr.length - 2] === "a") {
        arr.push("b");
        bLeft--;
      } else {
        arr.push("a");
        aLeft--;
      }
    } else if (aLeft < bLeft) {
      if (arr[arr.length - 1] === "b" && arr[arr.length - 2] === "b") {
        arr.push("a");
        aLeft--;
      } else {
        arr.push("b");
        bLeft--;
      }
    }
  }
  return arr.join("");
};
