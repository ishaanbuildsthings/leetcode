// https://leetcode.com/problems/partition-labels/description/
// Difficulty: Medium
// tags: greedy

// Problem

/*
Example:
Input: s = "ababcbacadefegdehijhklij"
Output: [9,7,8]
Explanation:
The partition is "ababcbaca", "defegde", "hijhklij".
This is a partition so that each letter appears in at most one part.
A partition like "ababcbacadefegde", "hijhklij" is incorrect, because it splits s into less parts.

Detailed:

You are given a string s. We want to partition the string into as many parts as possible so that each letter appears in at most one part.

Note that the partition is done so that after concatenating all the parts in order, the resultant string should be s.

Return a list of integers representing the size of these parts.
*/

// Solution, O(1) space for the letter mapping, O(n) time
/*
First, store a mapping of each letter to the furthest right index it occurs at. Then, iterate over the window. Update the furthest right we need to go to, based on what we already had, and the new letter. If we ever reach the furthest right, we can make a partition. I also tracked the beginning of a partition so we could calculate the length of the partition, as that is what the result needed to be.
*/

var partitionLabels = function (s) {
  const furthestRight = {}; // maps a letter to it's furthest right appearance by index

  for (let i = s.length - 1; i >= 0; i--) {
    const char = s[i];
    if (!(char in furthestRight)) {
      furthestRight[char] = i;
    }
  }

  // keep going, every time we see a letter, we have to go until at least the furthest right occurence of that letter, if we ever reach that, we can make a partition

  const partitions = [];
  let furthestToGoTo = 0;
  let beginning = -1; // helps us calculate the length of partitions, initially -1, so if we can make a parition at say index 2, our initial length is 2 - (-1) = 3.
  for (let i = 0; i < s.length; i++) {
    const char = s[i];
    const furthestRightIndexOfChar = furthestRight[char];
    furthestToGoTo = Math.max(furthestToGoTo, furthestRightIndexOfChar);
    if (furthestToGoTo === i) {
      partitions.push(i - beginning);
      beginning = i;
    }
  }

  return partitions;
};
