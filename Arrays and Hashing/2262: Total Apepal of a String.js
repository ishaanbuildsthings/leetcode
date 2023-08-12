// https://leetcode.com/problems/total-appeal-of-a-string/description/
// Difficulty: hard

// Problem
/*
The appeal of a string is the number of distinct characters found in the string.

For example, the appeal of "abbca" is 3 because it has 3 distinct characters: 'a', 'b', and 'c'.
Given a string s, return the total appeal of all of its substrings.

A substring is a contiguous sequence of characters within a string.
*/

// Solution, O(n) time and O(n) space
/*
Essentially, we need to know for each character, how many substrings is it uniquely that character. First create a mapping for each char type and their positions. Then we can add the contributions. If I know 'a' is the only 'a' ranging from indices [3, 7] and that 'a' is at position 6, I can calculate how many subarrays that 'a' forms a contribution to. This is similar to the total strength of wizards question.
*/

var appealSum = function (s) {
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
      if (i === positionsForNum.length - 1) {
        const startsOnLeft = positionsForNum[i] + 1;
        const endsOnRight = s.length - positionsForNum[i];
        const contributions = startsOnLeft * endsOnRight;
        result += contributions;
      } else {
        const nextPosition = positionsForNum[i + 1];
        const roomOnRight = nextPosition - positionsForNum[i];
        const roomOnLeft = positionsForNum[i] + 1;
        const contributions = roomOnLeft * roomOnRight;
        result += contributions;
      }
    }
  }

  return result;
};
