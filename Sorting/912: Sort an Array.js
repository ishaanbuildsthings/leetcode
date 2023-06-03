// https://leetcode.com/problems/sort-an-array/description/
// Difficulty: Medium
// tags: insertion sort

// Solution 1, merge sort, O(n log n) time and O(n) space
// Scroll down to see callstack / recursive steps

/*
Take an array, say [5, 2, 3, 1]
To sort it, split the array in half
[5, 2] and [3, 1]
Now, sort each half (recursive)

To sort [5, 2], we get [5] and [2]
[5] and [2] are both sorted, so we merge them, getting [2, 5]
Bubble this back up.

Now we have a sorted half, [2, 5]. Repeat for [3, 1], getting [1, 3]. Now merge these, getting [1, 2, 3, 5].

It takes n log n time, since there are log n levels, and for each level, we will have to merge a total of n elements.

The space is n, not log n! This is because we only ever concurrently have n space allocated. In the naive code below (lots of allocating), we do:

[4, 2, 1, 3] = initial array
[4, 2] [1, 3] = left and right arrays, this is n allocation
eventually:
[2, 4] and [1, 3] = the sorted arrays, another n allocation

merge them: [1, 2, 3, 4] = another n allocation

It's 3n allocation. We don't need to worry about further recursing down, because each time we go down we are allocating 3n * 0.5. And 1 + 0.5 + 0.25... = 2, so it is still O(n).

We could also improve this by not allocating so much memory (using pointers to the original array), or even merging it in place.
*/

var sortArray = function (nums) {
  // base case, a single element is already sorted
  if (nums.length === 1) {
    return nums;
  }

  // 5, 2, 3, 1

  // otherwise we have multiple elements, split them up
  const m = Math.floor(nums.length / 2);
  const leftArray = nums.slice(0, m); // 5, 2
  const rightArray = nums.slice(m); // 3, 1

  const leftArraySorted = sortArray(leftArray);
  const rightArraySorted = sortArray(rightArray);

  const mergedArray = merge(leftArraySorted, rightArraySorted);

  return mergedArray;
};

/*
 5, 2, 3, 1 tries to be sorted
 left array: [5, 2]   right array: [3, 1]
 3) left array sorted resolved to [2, 5]
 right array of [3, 1] tries to be sorted
 5) now [1, 3] is returned
 we merge [2, 5] and [1, 3], producing [1, 2, 3, 5], and return that

left array: [5, 2] tries to be sorted
left array: [5]   right array: [2]
1) left array sorted resolves to [5]
2) right array sorted resolves to [2]
merged array is called on [5] and [2], producing [2, 5]
we return [2, 5], terminating the context


left array: [5] tries to be sorted, it already is so it returns [5]

[3, 1] tries to be sorted, so we split it into left: [3] and right: [1]
4) now [3] and [1] are sorted, their merged array becomes [1, 3]
we return [1, 3] up, terminating the context

[3] is sorted, returns [3]

[1] is sorted, returns [1]


*/

// takes in two arrays, returns a sorted array
function merge(arr1, arr2) {
  const mergedArr = [];

  let p1 = 0;
  let p2 = 0;

  /*
     v          v
    [2, 6, 7]  [3, 9, 12]

    */

  // merge
  while (p1 < arr1.length && p2 < arr2.length) {
    if (arr1[p1] <= arr2[p2]) {
      mergedArr.push(arr1[p1]);
      p1++;
    } else {
      mergedArr.push(arr2[p2]);
      p2++;
    }

    // once one lists runs out, add the other
    if (p1 === arr1.length) {
      while (p2 < arr2.length) {
        mergedArr.push(arr2[p2]);
        p2++;
      }
    } else if (p2 === arr2.length) {
      while (p1 < arr1.length) {
        mergedArr.push(arr1[p1]);
        p1++;
      }
    }
  }

  return mergedArr;
}

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
