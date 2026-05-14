// https://leetcode.com/problems/ipo/description/
// Difficulty: Hard
// tags: greedy, heap

// ________ MAX HEAP ABOVE ON LEETCODE ________

// Problem
/*
Detailed:
Example:
Input: k = 2, w = 0, profits = [1,2,3], capital = [0,1,1]
Output: 4
Explanation: Since your initial capital is 0, you can only start the project indexed 0.
After finishing it you will obtain profit 1 and your capital becomes 1.
With capital 1, you can either start the project indexed 1 or the project indexed 2.
Since you can choose at most 2 projects, you need to finish the project indexed 2 to get the maximum capital.
Therefore, output the final maximized capital, which is 0 + 1 + 3 = 4.

Suppose LeetCode will start its IPO soon. In order to sell a good price of its shares to Venture Capital, LeetCode would like to work on some projects to increase its capital before the IPO. Since it has limited resources, it can only finish at most k distinct projects before the IPO. Help LeetCode design the best way to maximize its total capital after finishing at most k distinct projects.

You are given n projects where the ith project has a pure profit profits[i] and a minimum capital of capital[i] is needed to start it.

Initially, you have w capital. When you finish a project, you will obtain its pure profit and the profit will be added to your total capital.

Pick a list of at most k distinct projects from given projects to maximize your final capital, and return the final maximized capital.

The answer is guaranteed to fit in a 32-bit signed integer.
*/

// Solution, O(n log n) time, O(n) space
/*
At any point, we want to take on the project that gives us the most return, assuming we can take on that project. So we create a max heap containing projects we can afford. We take on a project, then add more projects we can afford by iterating through a sorted list of tuples [capitalNeeded, trueProfit]. We repeat this process k times.

It takes n log n time to sort the tuples by capital needed. I didn't heapify so it takes n log n worst case time to populate the initial heap. Then, k times, we pop from a heap of size n. n log n dominates everything. For space, we use O(n) space.
*/

var findMaximizedCapital = function (k, w, profits, capital) {
  /*
    we will maintain a max heap of true profits for only projects we can afford. when we take on a project, the amount of money we have grows, and we can afford new projects, so we add those projects to the heap (we add the value of the true profit they give)
    */

  const zipped = capital.map((startingCapitalNeeded, i) => [
    startingCapitalNeeded,
    profits[i],
  ]);

  // sort by starting capital needed, as we will only add projects to the heap once we can afford to take them on
  zipped.sort((a, b) => a[0] - b[0]);

  const maxHeap = new MaxHeap();

  let currentCapital = w;

  // populate the heap with the initial true profits for what we can afford, could be faster with a true heapify
  let p = 0; // tracks the first project we cannot afford
  // iterates as long as we can afford a project, or stops if we can afford every project
  while (p < profits.length && zipped[p][0] <= currentCapital) {
    const tuple = zipped[p];
    const [startingCapitalNeeded, profit] = tuple;
    maxHeap.insert(profit);
    p++;
  }

  // take on k projects
  for (let i = 0; i < k; i++) {
    // if we run out of projects we can afford, we just return how much we made
    if (maxHeap.size() === 0) {
      return currentCapital;
    }
    // console.log(`taking on the ${i + 1}th project`)
    const mostProfitableProject = maxHeap.remove();
    currentCapital += mostProfitableProject;
    // add new projects we can afford, or if we can afford every project, then stop
    while (p < profits.length && zipped[p][0] <= currentCapital) {
      const tuple = zipped[p];
      const [startingCapitalNeeded, profit] = tuple;
      maxHeap.insert(profit);
      p++;
    }
  }

  return currentCapital;
};
