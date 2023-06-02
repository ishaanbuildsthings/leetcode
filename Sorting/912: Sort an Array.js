// https://leetcode.com/problems/sort-an-array/description/
// Difficulty: Medium
// tags: insertion sort

// Solution X-1, insertion sort, O(n^2) time and O(1) space

/*
Iterate over the array, whenever we find a smaller element, start swapping like in Solution X. Use `i` to track which elements to swap.
*/
function sortArray(arr) {
  for (let j = 1; j < arr.length; j++) {
    let i = j - 1;
    while (i >= 0 && arr[i + 1] < arr[i]) {
      const temp = arr[i + 1];
      arr[i + 1] = arr[i];
      arr[i] = temp;
      i--;
    }
  }
  return arr;
}

// Solution X, my original insertion sort, O(n^2) time and O(1) space

/*
Iterate starting from the left. Whenever we find a smaller element, say 3 6 9 4 and we reach 4, start performing swaps. First swap 9 and 4: 3 6 4 9. Then swap 6 and 4: 3 4 6 9. Then return back to after 9 and keep going.
*/

var sortArray = function (nums) {
  for (let j = 1; j < nums.length; j++) {
    const saveJ = j;

    let i = j - 1;

    if (nums[j] >= nums[i]) {
      continue;
    }

    while (j >= 1 && nums[j] < nums[i]) {
      const temp = nums[i];
      nums[i] = nums[j];
      nums[j] = temp;
      j--;
      i--;
    }

    j = saveJ;
  }
  return nums;
};
