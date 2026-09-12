// https://leetcode.com/problems/count-unique-characters-of-all-substrings-of-a-given-string/description/
// difficulty: hard

// Problem
/*
Let's define a function countUniqueChars(s) that returns the number of unique characters on s.

For example, calling countUniqueChars(s) if s = "LEETCODE" then "L", "T", "C", "O", "D" are the unique characters since they appear only once in s, therefore countUniqueChars(s) = 5.
Given a string s, return the sum of countUniqueChars(t) where t is a substring of s. The test cases are generated such that the answer fits in a 32-bit integer.

Notice that some substrings can be repeated so in this case you have to count the repeated ones too.
*/

// Solution, O(n) time and O(n) space
/*
Essentially, we need to know for each character, how many substrings is it uniquely that character. First create a mapping for each char type and their positions. Then we can add the contributions. If I know 'a' is the only 'a' ranging from indices [3, 7] and that 'a' is at position 6, I can calculate how many subarrays that 'a' forms a contribution to. This is similar to the total strength of wizards question.
*/

var uniqueLetterString = function (s) {
  const positions = {}; // maps a number to a list of positions that number occurs at

  for (let i = 0; i < s.length; i++) {
    if (!(s[i] in positions)) {
      positions[s[i]] = [i];
    } else {
      positions[s[i]].push(i);
    }
  }

  let result = 0;

  for (const key in positions) {
    const positionsForNum = positions[key];
    for (let i = 0; i < positionsForNum.length; i++) {
      const position = positionsForNum[i];
      const rightPosition = positionsForNum[i + 1] ?? s.length;
      const leftPosition = positionsForNum[i - 1] ?? -1;
      const roomOnRight = rightPosition - position;
      const roomOnLeft = position - leftPosition;
      const contribution = roomOnLeft * roomOnRight;
      result += contribution;
    }
  }

  return result;
};
