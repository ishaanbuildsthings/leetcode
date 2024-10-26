// https://leetcode.com/problems/fizz-buzz/description/
// Difficulty: Easy

// Problem
/*
Given an integer n, return a string array answer (1-indexed) where:

answer[i] == "FizzBuzz" if i is divisible by 3 and 5.
answer[i] == "Fizz" if i is divisible by 3.
answer[i] == "Buzz" if i is divisible by 5.
answer[i] == i (as a string) if none of the above conditions are true.
*/

// Solution, O(n) time and O(1) space
/*
A classic. I wrote it in a string builder style so its modularized.
*/

var fizzBuzz = function (n) {
  const result = [];

  for (let i = 1; i <= n; i++) {
    let str = "";
    if (i % 3 === 0) {
      str += "Fizz";
    }
    if (i % 5 === 0) {
      str += "Buzz";
    }
    result.push(str === "" ? String(i) : str);
  }

  return result;
};
