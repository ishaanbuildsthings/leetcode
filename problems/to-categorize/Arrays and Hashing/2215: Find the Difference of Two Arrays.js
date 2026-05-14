// https://leetcode.com/problems/find-the-difference-of-two-arrays/description/
// Difficulty: Easy
// tags: binary search

// Solution 1
// O(n+m) time and O(n+m) space. Create sets out of both arrays and use those to determine which elements are unique to each array.

const findDifference = function (nums1, nums2) {
  const set1 = new Set(nums1);
  const set2 = new Set(nums2);
  const nums1Exclusive = [];
  const nums2Exclusive = [];
  for (const num of nums1) {
    if (!set2.has(num)) {
      nums1Exclusive.push(num);
      set2.add(num); // to prevent the value from being added again
    }
  }
  for (const num of nums2) {
    if (!set1.has(num)) {
      nums2Exclusive.push(num);
      set1.add(num); // to prevent the value from being added again
    }
  }
  return [nums1Exclusive, nums2Exclusive];
};

// Solution 2
// O(n log m + m log n) time and O(1) space, or more space if we consider .sort to use space, but it depends on the implementation. Sort both arrays and use binary search to find the unique elements.
const findDifference2 = function (nums1, nums2) {
  nums1.sort((a, b) => a - b);
  nums2.sort((a, b) => a - b);

  const nums1Exclusive = [];
  const nums2Exclusive = [];

  // do a binary lookup in nums2 for every number in nums1
  for (let i = 0; i < nums1.length; i++) {
    if (i > 0 && nums1[i] === nums1[i - 1]) {
      continue;
    }
    let l = 0;
    let r = nums2.length - 1;
    let m = Math.floor((l + r) / 2);
    while (l < r) {
      m = Math.floor((l + r) / 2);
      if (nums2[m] > nums1[i]) {
        r = m - 1;
      } else if (nums2[m] < nums1[i]) {
        l = m + 1;
      } else if (nums2[m] === nums1[i]) {
        l = m;
        break;
      }
    }
    if (nums2[l] !== nums1[i]) {
      nums1Exclusive.push(nums1[i]);
    }
  }

  // do a binary lookup in nums1 for every number in nums2
  for (let i = 0; i < nums2.length; i++) {
    if (i > 0 && nums2[i] === nums2[i - 1]) {
      continue;
    }
    let l = 0;
    let r = nums1.length - 1;
    let m = Math.floor((l + r) / 2);
    while (l < r) {
      m = Math.floor((l + r) / 2);
      if (nums1[m] > nums2[i]) {
        r = m - 1;
      } else if (nums1[m] < nums2[i]) {
        l = m + 1;
      } else if (nums1[m] === nums2[i]) {
        l = m;
        break;
      }
    }
    if (nums1[l] !== nums2[i]) {
      nums2Exclusive.push(nums2[i]);
    }
  }

  return [nums1Exclusive, nums2Exclusive];
};
