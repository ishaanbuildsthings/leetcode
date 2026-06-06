// https://leetcode.com/problems/reconstruct-original-digits-from-english/description/
// difficulty: Medium

// Problem
/*
Example:
Input: s = "fviefuro"
Output: "45"

Detailed:
Given a string s containing an out-of-order English representation of digits 0-9, return the digits in ascending order.
*/

// Solution, O(n) time, O(1) space
/*
We can form certain words right off the bat, for instance z is only in zero. We decrement the appropriate counts of each character. After that, new numbers have unique letters, and we repeat the process.
*/

var originalDigits = function (s) {
  /*
    // zero -> z
    one
    // two -> w
    // three -> h but only if there is no g
    // four -> u
    five -> v now that we are out of other stuff
    // six -> x
    // seven -> s but only if there is no x
    // eight -> g
    nine

    */

  const frqs = {}; // maps chars to their frequencies
  for (const char of "abcdefghijklmnopqrstuvwxyz") {
    frqs[char] = 0;
  }
  for (const char of s) {
    frqs[char]++;
  }

  const resultCounts = {};
  for (const char of "0123456789") {
    resultCounts[char] = 0;
  }

  function deleteCharsAddNumber(char, word, resultToIncrement) {
    while (frqs[char] > 0) {
      resultCounts[resultToIncrement]++;
      for (const char of word) {
        frqs[char]--;
      }
    }
  }

  // solve 0s
  deleteCharsAddNumber("z", "zero", "0");
  // solve 2s
  deleteCharsAddNumber("w", "two", "2");
  // solve 4s
  deleteCharsAddNumber("u", "four", "4");
  // solve 6s
  deleteCharsAddNumber("x", "six", "6");
  // solve 8s
  deleteCharsAddNumber("g", "eight", "8");
  // solve 7s, now that we are out of x
  deleteCharsAddNumber("s", "seven", "7");
  // solve 3s, now that we are out of g for eight
  deleteCharsAddNumber("h", "three", "3");
  // solve 5s, now that we are out of other stuff
  deleteCharsAddNumber("v", "five", "5");
  // solve 9s, now that we are out of other stuff
  deleteCharsAddNumber("i", "nine", "9");
  // solve 1s, now that we are out of other stuff
  deleteCharsAddNumber("o", "one", "1");

  const resultArr = [];
  for (const char of "0123456789") {
    for (let i = 0; i < resultCounts[char]; i++) {
      resultArr.push(char);
    }
  }

  return resultArr.join("");
};
