// https://leetcode.com/problems/4sum/description/
// Difficulty: Medium
// Tags: Two Pointers

// Solution
// O(n^3) time and O(1) space. Sort the array. Iterate over the array and calculate threeSums. To calculate a threeSum, iterate over the array and calculate twoSums. To calculate a twoSum, use a 2-pointer method on the sorted array.
/*
if (i > 0 && nums[i] === nums[i - 1]) continue; // skip duplicates
^ this is needed to skip duplicates in a four loop. We can use the continue strategy inside a for loop, because continue will make the for loop iterate its counter to the next value. Since both fourSum and _threeSum use for loops, we use that optimization in both.

However, in twoSum, we also want to skip duplicate values, but we are using a while loop. We could in theory use a for loop, and say for (let i = ...; i < r; i++) and modify r and i while inside the for loop. If we did that, we could use `continue`. But since we used a while loop, we can do something like:
l++
while (nums[l] === nums[l - 1]) l++;

We don't need to worry about l becoming too big because the initial while(l<r) condition will break.
*/

// nested approach (easier to write than functional)
var fourSum = function (nums, target) {
  nums.sort((a, b) => a - b);
  const solutions = [];

  // four every fourSum number, do a 3sum
  for (let i = 0; i < nums.length; i++) {
    // for every threeSum number, do a 2sum
    if (i > 0 && nums[i] === nums[i - 1]) continue;
    const threeSumTarget = target - nums[i];
    for (let j = i + 1; j < nums.length; j++) {
      if (j > i + 1 && nums[j] === nums[j - 1]) continue; // never use the same j twice for a given i, if j is next to i then don't compare
      const twoSumTarget = threeSumTarget - nums[j];
      // do a twoSum
      let l = j + 1;
      let r = nums.length - 1;
      while (l < r) {
        if (nums[l] + nums[r] === twoSumTarget) {
          solutions.push([nums[i], nums[j], nums[l], nums[r]]);
          l++;
          while (nums[l] === nums[l - 1]) {
            l++;
          }
        } else if (nums[l] + nums[r] > twoSumTarget) {
          r--;
          while (nums[r] === nums[r + 1]) {
            r--;
          }
        } else if (nums[l] + nums[r] < twoSumTarget) {
          l++;
          while (nums[l] === nums[l - 1]) {
            l++;
          }
        }
      }
    }
  }
  return solutions;
};

// functional approach
var fourSum = function (nums, target) {
  nums.sort((a, b) => a - b);
  const fourSumResults = [];
  for (let i = 0; i < nums.length; i++) {
    if (i > 0 && nums[i] === nums[i - 1]) continue; // skip duplicates
    const threeSumTarget = target - nums[i];
    const resultsSpecificPointer = _threeSum(
      nums,
      i + 1,
      threeSumTarget,
      nums[i]
    ); // all results for a given fourSum pointer
    fourSumResults.push(...resultsSpecificPointer);
  }

  return fourSumResults;
};

// finds all threesums starting from a given pointer until the end
function _threeSum(nums, pointerToStartAt, target, fourSumNumber) {
  const threeSumResults = [];
  for (let i = pointerToStartAt; i < nums.length; i++) {
    if (i > pointerToStartAt && nums[i] === nums[i - 1]) continue; // skip duplicates
    const twoSumTarget = target - nums[i];
    const resultsSpecificPointer = _twoSum(
      nums,
      i + 1,
      twoSumTarget,
      nums[i],
      fourSumNumber
    ); // all results for a given threeSum pointer
    threeSumResults.push(...resultsSpecificPointer);
  }

  return threeSumResults;
}

function _twoSum(
  nums,
  pointerToStartAt,
  target,
  threeSumNumber,
  fourSumNumber
) {
  let l = pointerToStartAt;
  let r = nums.length - 1;
  const results = [];
  while (l < r) {
    if (nums[l] + nums[r] === target) {
      results.push([fourSumNumber, threeSumNumber, nums[l], nums[r]]);
      l++;
      r--;
      while (nums[l] === nums[l - 1]) {
        l++;
      }
      while (nums[r] === nums[r + 1]) {
        r--;
      }
    } else if (nums[l] + nums[r] > target) {
      r--;
    } else if (nums[l] + nums[r] < target) {
      l++;
    }
  }
  return results;
}
/*
4sum pointer, i
 V
[0, 0, 1, 1, 2, 2, 3, 3, 4]   target= 4

for every 4sum pointer, find a 3sum starting at i+1 that equals (target - the pointer value)
so here, find a 3sum that equals 4-0, starting from i=1


3sum pointer, i
    V
[0, 0, 1, 1, 2, 2, 3, 3, 4]   threeSumTarget= 4

for every 3sum pointer, find a 2sum, starting at i+1, that equals the threeSumTarget - pointer value

2sum pointer, i
       V
[0, 0, 1, 1, 2, 2, 3, 3, 4]   twoSumTarget= 2

for every 2sum pointer, find all 2sums that equal the twoSum target


*/
