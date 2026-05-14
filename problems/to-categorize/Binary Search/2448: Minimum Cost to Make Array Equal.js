// https://leetcode.com/problems/minimum-cost-to-make-array-equal/description/
// Difficulty: hard
// Tags: binary search

// Problem
/*
Simplfiied:
Input: nums = [1,3,5,2], cost = [2,3,1,14]
Output: 8
Explanation: We can make all the elements equal to 2 in the following way:
- Increase the 0th element one time. The cost is 2.
- Decrease the 1st element one time. The cost is 3.
- Decrease the 2nd element three times. The cost is 1 + 1 + 1 = 3.
The total cost is 2 + 3 + 3 = 8.
It can be shown that we cannot make the array equal with a smaller cost.

Detailed:
You are given two 0-indexed arrays nums and cost consisting each of n positive integers.

You can do the following operation any number of times:

Increase or decrease any element of the array nums by 1.
The cost of doing one operation on the ith element is cost[i].

Return the minimum total cost such that all the elements of the array nums become equal.
*/

// Solution, O(n log n) time, O(n) space for the sorted/filtered array.

/*
First, sort all the numbers, so we may have: [1, 2, 3, 5].

The answer must be converging all elements to one of these numbers. Intuitively, if we had two numbers, [1, 5], the minimum cost would just be setting everything to one of them, it couldn't be inbetween.

We create a cost function that, when given a number we set everything to, determines the total cost in O(n) time by simple iteration.

Then, do a binary search of the sorted numbers, checking two at a time. So we start by looking at the cost if we set everything to 2, and the cost if we set everything to 3. If the cost of setting everything to 3 was cheaper, we know we have to look from the range starting at 3, and going to the right.

Consider that we have some function, which represents the cost of setting things to some number. For instance if our number is 1, and each movement has a cost of 10, our function is y = |x - 1| * 10. So if we want to set the number to 1, it costs nothing, but setting it to 2 or 0 would cost 10, etc.

Now if we have a series of numbers, [1, 3, 5], and say each costs 10 to move, we could have multiple functions. The total cost for setting the entire array to 1 would be: |x - 1|*10 + |x - 3|*10 + |x - 5|*10.

Since this is a linear combination of convex functions, it has some minimum. So when we search among adjacent numbers, we move in the descending direction. Since we know for sure one cost produces the minimum, we use while (l < r), as the last value where l ends up equaling r, will be the minimum. If the cost of the left side is more than the right, we should look to the right, and set l=midLeft + 1. If the cost of the right side is more, we should look left, and set r=midLeft.

Since we do n binary searches of log n, the time is n log n.

We used storage to filter out duplicate elements to prevent any potential bugs that might arise if the numbers are adjacent. If we didn't use storage by sorting nums directly, and skipping over adjacent elements, we would still have needed O(n) storage to sort the cost function relative to how nums was being sorted as well, by zipping them together.
*/

var minCost = function (nums, cost) {
  const numsFiltered = Array.from(new Set(nums));
  const numsSortedAndFiltered = numsFiltered.sort((a, b) => a - b);

  // given a number we have to set all values to, gives a total cost
  function getTotalCost(setToThisNum) {
    let totalCost = 0;
    for (let i = 0; i < nums.length; i++) {
      const diff = Math.abs(setToThisNum - nums[i]);
      const singleCost = cost[i];
      const costToFullyChange = diff * singleCost;
      totalCost += costToFullyChange;
    }
    return totalCost;
  }

  /*
    now that the nums are sorted, do a binary search, starting on the two middle numbers. determine the costs for two options, and therefore which way to move given the unimodal distribution of the linear combination of the convex functions
    */

  let l = 0;
  let r = numsSortedAndFiltered.length - 1;
  while (l < r) {
    // represent the two middle indicies, for which we will determine costs if we try setting everything to those numbers
    const midLeft = Math.floor((r + l) / 2);
    const midRight = midLeft + 1;

    const costLeft = getTotalCost(numsSortedAndFiltered[midLeft]);
    const costRight = getTotalCost(numsSortedAndFiltered[midRight]);

    if (costLeft > costRight) {
      l = midLeft + 1;
    } else {
      r = midLeft;
    }
  }

  return getTotalCost(numsSortedAndFiltered[r]);
};
