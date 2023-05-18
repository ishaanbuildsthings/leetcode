// https://leetcode.com/problems/valid-parentheses/
// Difficulty: Easy
// tags: stack

// Problem
/*
Simplfied: Check if a string with parentheses is valid.

Detailed: Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:

Open brackets must be closed by the same type of brackets.
Open brackets must be closed in the correct order.
Every close bracket has a corresponding open bracket of the same type.
*/

// Solution
// O(n) time and O(n) space. Use a stack to keep track of the opening braces. If we get a closing brace, pop the opening brace off the stack. If the closing brace doesn't match the opening brace, return false. If we get to the end of the string, return true if the stack is empty, otherwise return false, since we would have a string like '((((('

const mapping = {
  ")": "(",
  "]": "[",
  "}": "{",
};

var isValid = function (s) {
  const stack = [];

  for (const char of s) {
    // if we get an opening brace, add it
    if (!(char in mapping)) {
      stack.push(char);
    }
    // if we get a closing brace, and it doesn't match, return false, otherwise pop the opening brace
    else {
      // pop it off if we can
      if (stack[stack.length - 1] === mapping[char]) {
        stack.pop();
      } else {
        return false;
      }
    }
  }
  return stack.length === 0;
};
