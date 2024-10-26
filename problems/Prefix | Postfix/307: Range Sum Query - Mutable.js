// https://leetcode.com/problems/range-sum-query-mutable/description/
// Difficulty: Medium
// tags: square root decomposition, segment tree, binary indexed tree

// Problem
/*
Simplified:
Input
["NumArray", "sumRange", "update", "sumRange"]
[[[1, 3, 5]], [0, 2], [1, 2], [0, 2]]
Output
[null, 9, null, 8]

Explanation
NumArray numArray = new NumArray([1, 3, 5]);
numArray.sumRange(0, 2); // return 1 + 3 + 5 = 9
numArray.update(1, 2);   // nums = [1, 2, 5]
numArray.sumRange(0, 2); // return 1 + 2 + 5 = 8

Detailed:
Given an integer array nums, handle multiple queries of the following types:

Update the value of an element in nums.
Calculate the sum of the elements of nums between indices left and right inclusive where left <= right.
Implement the NumArray class:

NumArray(int[] nums) Initializes the object with the integer array nums.
void update(int index, int val) Updates the value of nums[index] to be val.
int sumRange(int left, int right) Returns the sum of the elements of nums between indices left and right inclusive (i.e. nums[left] + nums[left + 1] + ... + nums[right]).
*/

/* WRITEUP

There are many ways to solve this problem.

1) brute force. we hold an array of size n. when we update, we change the number in O(1). when we sum, we sum up to n elements, O(n).

2) store an array of prefix sums instead. each prefix sum holds the sum of the elements before it, and itself. when we update an element, update all prefixes of that element, and to the right, O(n). when we sum, we just look at the difference of two prefix sums, O(1).

3) square root decomp. Split the array into ~root n blocks. So for 10 elements, we have 3 blocks of 3, and 1 ending block of 1. we also store root n mappings of a block to its sum. when we update an index, we update the block and the sum for that block in O(1). when we sum a range, we sum the left partial block (up to root n elements), root n filled blocks, and the right partial block (up to root n elements), so O(root n).

4) segment tree
*/

// Solution, square root decomp
/*
This can be a bit more concise. For instance when summing, check if the starting block is the same as the ending block, if so iterate over the provided index range. Otherwise iterate from the starting index to the end of that block, the middle blocks, then 0 to the ending index of the ending block.
*/

var NumArray = function (nums) {
  this.buckets = [];
  const bucketSize = Math.ceil(Math.sqrt(nums.length)); // 16->4, 22->5, etc
  this.bucketSize = bucketSize; // we can use this later in the update function
  const numberOfBuckets = Math.floor(nums.length / bucketSize);
  for (let i = 0; i < numberOfBuckets; i++) {
    this.buckets.push(new Array(bucketSize).fill(0));
  }
  const elementsAccountedFor = bucketSize * numberOfBuckets;
  const elementsMissing = nums.length - elementsAccountedFor;
  if (elementsMissing > 0) {
    const lastBucket = new Array(elementsMissing).fill(0);
    this.buckets.push(lastBucket);
  }

  let bucketPointer = 0;
  let insertionPointer = 0; // where we will insert into a bucket
  for (let i = 0; i < nums.length; i++) {
    this.buckets[bucketPointer][insertionPointer] = nums[i];
    insertionPointer++;
    if (insertionPointer === bucketSize) {
      bucketPointer++;
      insertionPointer = 0;
    }
  }

  // populate the mapping of buckets to their sums, done separately to make code cleaner
  this.sums = {}; // maps a bucket number to its sum
  for (let bucketNum = 0; bucketNum < this.buckets.length; bucketNum++) {
    const bucket = this.buckets[bucketNum];
    const bucketSum = bucket.reduce((acc, val) => acc + val, 0);
    this.sums[bucketNum] = bucketSum;
  }
};

NumArray.prototype.update = function (index, val) {
  const bucketsBeaten = Math.floor(index / this.bucketSize);
  const bucketIndex = bucketsBeaten; // the bucket we will modify
  const bucketIndicesBeaten = bucketsBeaten * this.bucketSize; // total indices beaten from all buckets beaten
  const extraIndicesBeaten = index - bucketIndicesBeaten; // insertion point within the bucket

  const oldNum = this.buckets[bucketIndex][extraIndicesBeaten];
  this.buckets[bucketIndex][extraIndicesBeaten] = val;
  const diff = val - oldNum;

  this.sums[bucketIndex] += diff;
};

NumArray.prototype.sumRange = function (left, right) {
  const startingBucketIndex = Math.floor(left / this.bucketSize);
  const startingBucketStartingPoint =
    left - startingBucketIndex * this.bucketSize;

  const endingBucketIndex = Math.floor(right / this.bucketSize);
  const endingBucketEndingPoint = right - endingBucketIndex * this.bucketSize;

  let sum = 0;

  // if we are summing within on bucket only, go from the starting index to the ending
  if (startingBucketIndex === endingBucketIndex) {
    for (
      let i = startingBucketStartingPoint;
      i <= endingBucketEndingPoint;
      i++
    ) {
      sum += this.buckets[startingBucketIndex][i];
    }
    return sum;
  }

  // add the first partial bucket
  for (
    let i = startingBucketStartingPoint;
    i < this.buckets[startingBucketIndex].length;
    i++
  ) {
    sum += this.buckets[startingBucketIndex][i];
  }

  // add the buckets in the middle
  for (let i = startingBucketIndex + 1; i < endingBucketIndex; i++) {
    const bucketSum = this.sums[i];
    sum += bucketSum;
  }

  // add the ending partial bucket
  for (let i = 0; i <= endingBucketEndingPoint; i++) {
    sum += this.buckets[endingBucketIndex][i];
  }

  return sum;
};

/**
 * Your NumArray object will be instantiated and called as such:
 * var obj = new NumArray(nums)
 * obj.update(index,val)
 * var param_2 = obj.sumRange(left,right)
 */
