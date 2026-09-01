// https://leetcode.com/problems/largest-palindromic-number/description/
// Difficulty: Medium
// Tags: greedy, palindrome

// Problem
/*
Example:
Input: num = "444947137"
Output: "7449447"
Explanation:
Use the digits "4449477" from "444947137" to form the palindromic integer "7449447".
It can be shown that "7449447" is the largest palindromic integer that can be formed.

Detailed:
You are given a string num consisting of digits only.

Return the largest palindromic integer (in the form of a string) that can be formed using digits taken from num. It should not contain leading zeroes.

Notes:

You do not need to use all the digits of num, but you must use at least one digit.
The digits can be reordered.
*/

// Solution, O(n^2) time (can easily be O(n)), O(n) space
/*
First, get a count of how many times each number occurs. In a palindrome, every digit occurs twice, except for an optional center digit. So we can greedily select the largest center digit for numbers that have odd counts. Then greedily select pairs of digits around the center digit. We can only put 0s if we have other numbers to wrap around the 0s. Since we are adding elements to the beginning of the list, it is n^2 time. This could easily be fixed by using a queue, or by just using a stack and mirror it at the end to form the answer.
*/

var largestPalindromic = function (num) {
  // maps a char to the number of times it occurs
  const counts = {};

  for (const char of num) {
    if (!(char in counts)) {
      counts[char] = 1;
    } else {
      counts[char]++;
    }
  }

  const resultArr = [];

  // the first odd number goes in the middle

  for (let number = 9; number >= 0; number--) {
    const char = String(number);
    const countOfChar = counts[char];

    if (countOfChar % 2 === 1) {
      resultArr.push(char);
      counts[char]--;
      break;
    }
  }

  let numberOtherThanZero = false;
  for (let number = 1; number <= 9; number++) {
    const char = String(number);
    if (counts[char] >= 2) {
      numberOtherThanZero = true;
      break;
    }
  }

  for (let number = 0; number <= 9; number++) {
    const char = String(number);

    if (char === "0" && !numberOtherThanZero) {
      continue;
    }

    while (counts[char] > 1) {
      resultArr.unshift(char);
      resultArr.push(char);
      counts[char] -= 2;
    }
  }

  return resultArr.length === 0 ? "0" : resultArr.join("");
};
