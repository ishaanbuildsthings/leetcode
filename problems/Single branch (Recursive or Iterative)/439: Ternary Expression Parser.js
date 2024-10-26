// https://leetcode.com/problems/ternary-expression-parser/description/
// Difficulty: Medium
// Tags: recursion

// Problem
/*
Example:
Input: expression = "F?1:T?4:5"
Output: "4"
Explanation: The conditional expressions group right-to-left. Using parenthesis, it is read/evaluated as:
"(F ? 1 : (T ? 4 : 5))" --> "(F ? 1 : 4)" --> "4"
or "(F ? 1 : (T ? 4 : 5))" --> "(T ? 4 : 5)" --> "4"

Detailed:
Given a string expression representing arbitrarily nested ternary expressions, evaluate the expression, and return the result of it.

You can always assume that the given expression is valid and only contains digits, '?', ':', 'T', and 'F' where 'T' is true and 'F' is false. All the numbers in the expression are one-digit numbers (i.e., in the range [0, 9]).

The conditional expressions group right-to-left (as usual in most languages), and the result of the expression will always evaluate to either a digit, 'T' or 'F'.
*/

// Solution, O(n^2) time, O(n) space
/*
For a given expression, we need to find the extra ':' which determines the split point. This takes n time, and there are n expressions to resolve.
*/

var parseTernary = function (expression) {
  // returns the solution for the substring [l:r]
  function parse(l, r) {
    // we simplified to a single digit
    if (l === r) {
      return expression[r];
    }

    // generally, expressions look like: T ? _____ : ______
    // where each underline can be another nested ternary, therefore, the split happens when we encounter the extra ':'

    let questionCount = 0;
    let colonCount = 0;
    // start after the '?', find the ':' for the main expression, which occurs when we find more ':' than '?'
    let i;
    for (i = l + 2; i <= r; i++) {
      if (expression[i] === "?") {
        questionCount++;
      } else if (expression[i] === ":") {
        colonCount++;
      }
      if (colonCount > questionCount) {
        break;
      }
    }
    /* here, 'i' is the index of the colon */

    if (expression[l] === "T") {
      return parse(l + 2, i - 1);
    } else if (expression[l] === "F") {
      return parse(i + 1, r);
    }
  }

  return parse(0, expression.length - 1);
};
