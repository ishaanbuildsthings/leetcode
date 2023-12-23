// https://leetcode.com/problems/sleep/description/
// Difficulty: Easy

// Solution
// It's just promisifying a native async function

async function sleep(ms) {
  return new Promise((res) => setTimeout(res, ms));
}
