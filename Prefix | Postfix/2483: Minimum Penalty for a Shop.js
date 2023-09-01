// https://leetcode.com/problems/minimum-penalty-for-a-shop/description/
// Difficulty: Medium
// Tags: prefix / postfix

// Problem
/*
You are given the customer visit log of a shop represented by a 0-indexed string customers consisting only of characters 'N' and 'Y':

if the ith character is 'Y', it means that customers come at the ith hour
whereas 'N' indicates that no customers come at the ith hour.
If the shop closes at the jth hour (0 <= j <= n), the penalty is calculated as follows:

For every hour when the shop is open and no customers come, the penalty increases by 1.
For every hour when the shop is closed and customers come, the penalty increases by 1.
Return the earliest hour at which the shop must be closed to incur a minimum penalty.

Note that if a shop closes at the jth hour, it means the shop is closed at the hour j.
*/

// Solution, O(n) time, O(1) space without prefix array
/*
Just iterate through, and at each index we can compute the penalty in O(1) using some pointers and preprocessed data. For some reason when I solved this I computed an O(n) sized prefix array but it isn't needed.
*/

/**
 * @param {string} customers
 * @return {number}
 */
var bestClosingTime = function (customers) {
  let totalVisitors = 0;
  for (const char of customers) {
    if (char === "Y") {
      totalVisitors++;
    }
  }

  let prefixCount = 0;
  const prefixVisitors = []; // holds a count of how many Y's are before the ith index
  for (let i = 0; i < customers.length + 1; i++) {
    prefixVisitors.push(prefixCount);
    if (customers[i] === "Y") {
      prefixCount++;
    }
  }

  let minPenalty = Infinity;
  let result;

  for (let i = 0; i < prefixVisitors.length; i++) {
    const prefix = prefixVisitors[i];
    const totalSeen = i + 1;
    const penaltyFromBefore = totalSeen - prefix;
    const visitorsUnseen = totalVisitors - prefix;
    const penaltyFromAfter = visitorsUnseen;
    const penaltyIfCloseNow = penaltyFromBefore + penaltyFromAfter;
    if (minPenalty > penaltyIfCloseNow) {
      result = i;
      minPenalty = penaltyIfCloseNow;
    }
  }

  return result;
};
