// implementation with real deque, O(n) time and O(n) space

class Deque {
  constructor() {
    // when the head is bigger than the tail, they are crossed, and the deque is empty, otherwise the head and tail point to the head and tail elements
    this.headPosition = 0;
    this.tailPosition = -1;
    this.storage = {};
  }

  push(val) {
    this.tailPosition++;
    this.storage[this.tailPosition] = val;
  }

  pop() {
    // trying to dequeue from an empty queue
    if (this.tailPosition < this.headPosition) {
      return null;
    }

    const value = this.storage[this.tailPosition];
    delete this.storage[this.tailPosition];
    this.tailPosition--;
    return value;
  }

  shift() {
    // trying to dequeue from an empty queue
    if (this.tailPosition < this.headPosition) {
      return null;
    }

    const value = this.storage[this.headPosition];
    delete this.storage[this.headPosition];
    this.headPosition++;
    return value;
  }

  right() {
    // trying to peek from an empty queue
    if (this.tailPosition < this.headPosition) {
      return null;
    }
    return this.storage[this.tailPosition];
  }

  left() {
    // trying to peek from an empty queue
    if (this.tailPosition < this.headPosition) {
      return null;
    }
    return this.storage[this.headPosition];
  }

  size() {
    return this.tailPosition - this.headPosition + 1;
  }
}

var shortestSubarray = function (nums, k) {
  /*
    our array is
    [80 -40  30   30   30  100]
    our prefix sums are
    [80, 40, 70, 100, 130, 230]

    to compute the sum of a subarray, we can do a range sum query on the prefixes, so the sum of [1,3] would be the 3rd indexed prefix sum, 100, minus the 0th index prefix sum, 80, yielding 20

    we want to find when this is over k, and minimize the length of it

    we can consider every possible right point of a subarray (n) instead of every possible subarray, which would be n^2.

    maintain an increasing monoqueue of prefix sums, when we reach a new number check if we can cross the threshold:
    check first prefix
    queue: [80
    our best possible is the number prefix sum of the number we are at (sum=80) minus the smallest earlier prefix, 0, we don't cross the threshold and don't update our result

    check second prefix
    queue: [80, 40
    well, 80 is always a worse prefix, why would we chop off 80 when we could chop off more numbers (smaller array) while keeping a bigger number. if we're going to remove the entire prefix that is 80, we might as well remove the -40 along with it as we could get a smaller array. we can dequeue the 80, we would never remove just that.
    queue:[40
    our best possible is the prefix sum we are at, which is 40, minus the smallest earlier prefix sum, which is 0, making our best possible sum 40 (we chop off nothing basically), which isn't the threshold

    check third prefix, 70, for number 30
    [40, 70
    here, it's debatable, chopping off 40 is good to try to get a smaller array, but we could potentially chop off 70 and get an even smaller array. we must keep it. we take our current prefix sum, 70, and subtract the smallest earlier prefix, which is still 0 (chop nothing), we don't meet the threshold

    ...
    whenever we do cross the threshold, we pop from the left since increasing our array would never help

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

  const deque = new Deque(); // contains tuples of [index, prefix sum]
  let minLength = Infinity;

  for (let i = 0; i < nums.length; i++) {
    // maintain increasing monoqueue for sums, in numbers 10 20 -5, prefixes 10 30 25, why would we ever chop off 20 elements and lose 30 in the sum when we could chop off 3 and lose 25? we still need to maintain the possibility of chopping off just one number and losing 10 though, for example
    while (deque.size() > 0 && prefixSums[i] < deque.right()[1]) {
      deque.pop();
    }

    // while we can chop from the left bigger and bigger prefixes and still be over k, do it
    while (deque.size() > 0 && prefixSums[i] - deque.left()[1] >= k) {
      const length = i - deque.left()[0];
      minLength = Math.min(minLength, length);
      deque.shift();
    }

    // we can always chop off 0 elements too
    if (prefixSums[i] >= k) {
      const length = i + 1;
      minLength = Math.min(minLength, length);
    }

    deque.push([i, prefixSums[i]]);
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
