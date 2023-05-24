// https://leetcode.com/problems/repeated-dna-sequences/description/
// Difficulty: Medium
// tags: rolling hash

// Problem
/*
The DNA sequence is composed of a series of nucleotides abbreviated as 'A', 'C', 'G', and 'T'.

For example, "ACGAATTCCG" is a DNA sequence.
When studying DNA, it is useful to identify repeated sequences within the DNA.

Given a string s that represents a DNA sequence, return all the 10-letter-long sequences (substrings) that occur more than once in a DNA molecule. You may return the answer in any order.
*/

var findRepeatedDnaSequences = function (s) {
  const seenSequences = new Set();
  const duplicatedSequences = new Set();
  let l = 0;
  let r = 9;
  while (r < s.length) {
    const substring = s.slice(l, r + 1);
    if (seenSequences.has(substring)) {
      duplicatedSequences.add(substring);
    }
    seenSequences.add(substring);
    r++;
    l++;
  }
  return Array.from(duplicatedSequences);
};
