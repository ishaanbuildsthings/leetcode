// https://leetcode.com/problems/zigzag-conversion/description/
// Difficulty: Medium

// Problem
/*
The string "PAYPALISHIRING" is written in a zigzag pattern on a given number of rows like this: (you may want to display this pattern in a fixed font for better legibility)

P   A   H   N
A P L S I I G
Y   I   R
And then read line by line: "PAHNAPLSIIGYIR"

Write the code that will take a string and make this conversion given a number of rows:

string convert(string s, int numRows);
*/

var convert = function (s, numRows) {
  // edge case, since when we reverse directions with the buckets we would go to bucket -1
  if (numRows === 1) {
    return s;
  }

  const buckets = new Array(numRows).fill().map(() => new Array());
  let currentBucket = 0;
  const MAX_BUCKET = numRows - 1; // represents the index of the final bucket
  let direction = "down"; // which way we are moving
  for (let i = 0; i < s.length; i++) {
    const char = s[i];
    buckets[currentBucket].push(s[i]);
    if (direction === "down") {
      // if we are at the bottom bucket, we need to move up
      if (currentBucket === MAX_BUCKET) {
        direction = "up";
        currentBucket -= 1;
      }
      // if we are not at the bottom bucket, we keep moving down
      else {
        currentBucket += 1;
      }
    } else {
      // if we are at the top bucket, we need to reverse and move down (increase current bucket)
      if (currentBucket === 0) {
        direction = "down";
        currentBucket += 1;
      }
      // otherwise keep moving up
      else {
        currentBucket -= 1;
      }
    }
  }

  const resultArr = [];
  for (const bucket of buckets) {
    for (const char of bucket) {
      resultArr.push(char);
    }
  }

  return resultArr.join("");
};
