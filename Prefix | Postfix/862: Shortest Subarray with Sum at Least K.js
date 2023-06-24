// https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/description/
// Difficulty: Hard
// tags: monotonic deque, prefix sums

// Solution O(n) time and O(n) space. Uses a monotonic deque, see comments for details. Essentially tracks prefix sums, and whenever we find a smaller prefix sum later, we pop from the deque. Whenever we find something that meets the threshold, we dequeue. We do not need to store tuples, just the indices, since we can look up the values based on the indices.

var shortestSubarray = function (nums, k) {
  /*
    our array is
    [80 -40  30   30   30  100]
    our prefix sums are
    [80, 40, 70, 100, 130, 230]

    to compute the sum of a subarray, we can do a range sum query on the prefixes, so the sum of [1,3] would be the 3rd indexed prefix sum, 100, minus the 0th index prefix sum, 80, yielding 20.

    we want to find when this is over k, and minimize the length of it

    we can consider every possible right point of a subarray (n) instead of every possible subarray, which would be n^2.

    maintain an increasing monoqueue of prefix sums. This intuitively makes sense, as normally when we iterate like in kadane's, we track the running sum. In this case, we have to track the running sum at each point, and add it to a deque, so when we finally reach the k threshold, we see how long of a prefix we can dequeue. when we add prefix sums to the deque, we should pop from the right as long as the right is bigger than our prefix sum, since if we get a smaller prefix sum, we could chop off more elements and lose less total numbers.

    check first prefix
    queue: [80
    our highest sum is the prefix sum of the number we are at (sum=80) minus the smallest earlier prefix, 0, we don't cross the threshold and don't update our result

    check second prefix
    queue: [80, 40
    well, 80 is always a worse prefix, why would we chop off 80 when we could chop off more numbers (smaller array) while keeping a bigger number. if we're going to remove the entire prefix that is 80, we might as well remove the -40 along with it as we could get a smaller array. we can dequeue the 80, we would never remove just that from the beginning.
    queue:[40
    our best possible is the prefix sum we are at, which is 40, minus the smallest earlier prefix sum, which is 0, making our best possible sum 40 (we chop off nothing basically), which isn't the threshold

    check third prefix, 70, for number 30
    [40, 70
    here, it's debatable, chopping off 40 is good to try to get a smaller array, but we could potentially chop off 70 and get an even smaller array. we must keep it. we take our current prefix sum, 70, and subtract the smallest earlier prefix, which is still 0 (chop nothing), we don't meet the threshold

    ...
    whenever we do cross the threshold, we dequeue from the left since increasing our array would never help

    in practice we have to keep the index the prefix sum occured at as well
    */
  const prefixSums = [];
  let dpSum = 0;
  for (let i = 0; i < nums.length; i++) {
    dpSum += nums[i];
    prefixSums.push(dpSum);
  }

  /*
    2, -1, 2

    queue: [index, prefixSum]
    [ [0,2]

    [ [0,2][1,1]
    dequeue from left
    [ [1,1]

    [ [1,1] [2,3]
    optimalSum is 3-0 = 3, which is of the threshold


    */

  const queue = []; // contains tuples of [index, prefix sum]
  let minLength = Infinity;

  for (let i = 0; i < nums.length; i++) {
    // maintain increasing monoqueue for sums, in numbers 10 20 -5, prefixes 10 30 25, why would we ever chop off 2 elements and lose 30 in the sum when we could chop off 3 and lose 25? we still need to maintain the possibility of chopping off just one number and losing 10 though, for example.
    while (queue.length > 0 && prefixSums[i] < queue[queue.length - 1][1]) {
      queue.pop();
    }

    // while we can chop from the left bigger and bigger prefixes and still be over k, do it
    while (queue.length > 0 && prefixSums[i] - queue[0][1] >= k) {
      const length = i - queue[0][0];
      minLength = Math.min(minLength, length);
      queue.shift(); // pretend O(1)
    }

    // we can always chop off 0 elements too
    if (prefixSums[i] >= k) {
      const length = i + 1;
      minLength = Math.min(minLength, length);
    }

    queue.push([i, prefixSums[i]]);
  }
  // [ [0,17] [1,102] [2,195]

  if (minLength === Infinity) {
    return -1;
  }
  return minLength;

  /*
    queue:
    [ [0, 17]  optimalsum = 17-0 not over threshold
    [ [0, 17] [1, 102] optimalsum = 102-0 not over threshold
    [ [0, 17] [1, 102] [2, 195] optimalsum = 195-0 over threshold, we can pop from the left, there is no point every chopping only the first element again because our array would always be bigger, update result=2
    [ [1, 102] [2, 195] optimalsum = 195-0
    */
};

/*
    80 -40 30 30 30 100, k=170
    we add up everything, get 230
    we decrement from the left, immediately dropping to 150, below 170, in reality we could decrement again to increase our sum, but we don't know that.
    if we stop here since we can't increment to the right anymore, we would fail, so maybe we could keep decrementing from l until l=r?

    no, consider:
    10 10 10 50 50 50 k=120
    our sums are:
    10 20 30 80 130, then we meet the threshold, so we decrement all the way down to our single 50, add the right number to get 100, and terminate. we missed 50 50 50. here, we would have needed to decrement only until dpSum falls below the threshold, but we cannot because of the prior example.

*/
