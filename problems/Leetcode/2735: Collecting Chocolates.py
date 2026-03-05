# MIN sparse table
# O(n log n) build
# O(1) range MIN

class SparseMin:
    def __init__(self, arr):
        self.n = len(arr)
        self.LOG = self.n.bit_length()
        self.sparse = [[0] * self.n for _ in range(self.LOG)]
        for i in range(self.n):
            self.sparse[0][i] = arr[i]
        for power in range(1, self.LOG):
            halfWidth = 1 << (power - 1)
            for left in range(self.n):
                val = self.sparse[power - 1][left]
                rightEdge = left + halfWidth
                if rightEdge < self.n:
                    val = min(val, self.sparse[power - 1][rightEdge])
                self.sparse[power][left] = val

    def query(self, l, r):
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return min(
            self.sparse[maxPow][l],
            self.sparse[maxPow][l + width - powWidth]
        )


class Solution:
    def minCost(self, nums: List[int], x: int) -> int:
        n = len(nums)
        nums2 = nums + nums
        sparse = SparseMin(nums2)

        def cost(k):
            total = k * x
            for i in range(n):
                total += sparse.query(n + i - k, n + i)
            return total

        l, r = 0, n - 1
        resI = None
        while l <= r:
            m = (l + r) // 2
            if cost(m) < cost(m + 1):
                resI = m
                r = m - 1
            else:
                l = m + 1
        return cost(resI)

# // old JS code
# // // https://leetcode.com/problems/collecting-chocolates/description/
# // // Difficulty: Medium
# // // tags: monotonic deque

# // // Problem
# // /*
# // You are given a 0-indexed integer array nums of size n representing the cost of collecting different chocolates. The cost of collecting the chocolate at the index i is nums[i]. Each chocolate is of a different type, and initially, the chocolate at the index i is of ith type.

# // In one operation, you can do the following with an incurred cost of x:

# // Simultaneously change the chocolate of ith type to ((i + 1) mod n)th type for all chocolates.
# // Return the minimum cost to collect chocolates of all types, given that you can perform as many operations as you would like.

# // Input: nums = [20,1,15], x = 5
# // Output: 13
# // Explanation: Initially, the chocolate types are [0,1,2]. We will buy the 1st type of chocolate at a cost of 1.
# // Now, we will perform the operation at a cost of 5, and the types of chocolates will become [1,2,0]. We will buy the 2nd type of chocolate at a cost of 1.
# // Now, we will again perform the operation at a cost of 5, and the chocolate types will become [2,0,1]. We will buy the 0th type of chocolate at a cost of 1.
# // Thus, the total cost will become (1 + 5 + 1 + 5 + 1) = 13. We can prove that this is optimal.
# // */

# // // Solution 1, O(n^2) time (assuming a real deque) and O(1) space. My implementation used O(n) space for ease of coding, but it can easily be done without.
# // // * Solution 2 is a simpler version of Solution 1. Instead of dealing with the monodeque, just track the smallest price viable starting from 0 rotations. Then when we check 1 rotation, compare the prior smallest price to the 1 slide away price, and so on.
# // // * Solution 3 can be n log n time using binary search and given the unimodal distribution of the cost function, though I haven't fully looked into this.

# // /*
# // It is a brute force. First, we assess the cost if we are allowed to rotate 0 times. Then 1 time, and so on.

# // Say we need to test the cost if we rotate 2 times. For each number, we are allowed to use the smallest cost between itself, and up to 2 elements on its left. I used a doubled array to make the wraparound easier, but it isn't needed.

# // For instance: [4, 6, 7, 10]

# // At 7, we are allowed to use cost 4, because it is the smallest cost that is at most 2 slides away from it.

# // To know what the smallest number is in a sliding window, we maintain a monodeque the tracks the smallest. The monodeque is monotonically increasing, and any time we get a new number we pop from the right until it is still decreasing. When we shift, we pop from the right if we lose the smallest number.

# // So for each iteration, we handle the monodeque and determine the smallest value, allowing us to compute the total sum.
# // */

# // var minCost = function (nums, x) {
# //   const doubleArr = [...nums, ...nums];

# //   function getLowestSumUsingLeftWindowSize(windowSize) {
# //     let result = 0;

# //     const deque = []; // pretend shift is O(1). the queue is monotonically increasing. whenever we see an element that violates this, we pop from the right. whenever we slide the window, we pop from the left if we slid past the smallest element.

# //     // populate the initial deque of smallest elements
# //     for (let i = 0; i < windowSize; i++) {
# //       const num = doubleArr[i];
# //       while (deque.length > 0 && deque[deque.length - 1] > num) {
# //         deque.pop();
# //       }
# //       deque.push(num);
# //     }

# //     /*
# //         say our nums are [1, 3, 10, 2]
# //         we make a double array: [1, 3, 10, 2, 1, 3, 10, 2]
# //         we have a window size of 3         *

# //         so we populate the initial deque, [1, 3, 10], which represents possible minimums. for each element, we want to know the minimum it can get from the left, which is the first position in the deque.

# //         we start iterating, starting at 10, since we have full info at 10, ending at 3, the last number.

# //         start from: (window size - 1)th index
# //         we do nums.length iterations, as we need to consider each element once.

# //         in the actual code, we will start from window size th index, because we manually add in the first smallest number to start with.
# //         */

# //     result += deque[0]; // add the initial smallest value

# //     const endPoint = windowSize + nums.length - 1;

# //     for (let i = windowSize; i < endPoint; i++) {
# //       // slid past leftmost number, maybe update deque if that was smallest
# //       const prevSmallest = deque[0];
# //       const lostNum = doubleArr[i - windowSize];

# //       if (prevSmallest === lostNum) {
# //         deque.shift(); // pretend O(1)
# //       }

# //       // add new number and update deque
# //       const newNum = doubleArr[i];

# //       while (deque.length > 0 && deque[deque.length - 1] > newNum) {
# //         deque.pop();
# //       }
# //       deque.push(newNum);

# //       // update result based on the smallest number
# //       result += deque[0];
# //     }

# //     return result;
# //   }

# //   let result = Infinity;

# //   for (let slides = 0; slides < nums.length; slides++) {
# //     const slideCost = slides * x;
# //     const purchaseCost = getLowestSumUsingLeftWindowSize(slides + 1);
# //     const totalCost = slideCost + purchaseCost;

# //     result = Math.min(result, totalCost);
# //   }

# //   return result;
# // };
