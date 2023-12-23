// https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/description/
// Difficulty: Medium
// tags: stack

// Problem
/*
Simplified:
Input: s = "lee(t(c)o)de)"
Output: "lee(t(c)o)de"
Explanation: "lee(t(co)de)" , "lee(t(c)ode)" would also be accepted.

Detailed:
Given a string s of '(' , ')' and lowercase English characters.

Your task is to remove the minimum number of parentheses ( '(' or ')', in any positions ) so that the resulting parentheses string is valid and return any valid string.

Formally, a parentheses string is valid if and only if:

It is the empty string, contains only lowercase characters, or
It can be written as AB (A concatenated with B), where A and B are valid strings, or
It can be written as (A), where A is a valid string.
*/

// Solution, O(n) time and O(n) space. Maintain a stack with the parentheses. Pop when we get a pair. Also track the indices so we know which ones we need to remove at the end.

var minRemoveToMakeValid = function (s) {
  const stack = []; // holds tuples of [parenthesis, index]. when a pair is formed, pop from the stack. at the end, we know which parentheses to remove.

  const indicesToSkip = new Set();

  for (let i = 0; i < s.length; i++) {
    const char = s[i];
    if (char !== "(" && char !== ")") {
      continue;
    }

    if (char === "(") {
      stack.push([char, i]);
      indicesToSkip.add(i);
    } else if (char === ")") {
      if (stack.length > 0 && stack[stack.length - 1][0] === "(") {
        const otherIndex = stack[stack.length - 1][1];
        indicesToSkip.delete(otherIndex);
        stack.pop();
      } else {
        stack.push([char, i]);
        indicesToSkip.add(i);
      }
    }
  }

  const result = [];
  for (let i = 0; i < s.length; i++) {
    const char = s[i];
    if (char !== "(" && char !== ")") {
      result.push(char);
    } else {
      if (indicesToSkip.has(i)) {
        continue;
      }
      result.push(char);
    }
  }

  return result.join("");
};
