// https://leetcode.com/problems/minimum-space-wasted-from-packaging/description/
// Difficulty: hard
// tags: binary search

// Problem
/*
Simplified:
Input: packages = [2,3,5], boxes = [[4,8],[2,8]]
Output: 6
Explanation: It is optimal to choose the first supplier, using two size-4 boxes and one size-8 box.
The total waste is (4-2) + (4-3) + (8-5) = 6.

Detailed:
You have n packages that you are trying to place in boxes, one package in each box. There are m suppliers that each produce boxes of different sizes (with infinite supply). A package can be placed in a box if the size of the package is less than or equal to the size of the box.

The package sizes are given as an integer array packages, where packages[i] is the size of the ith package. The suppliers are given as a 2D integer array boxes, where boxes[j] is an array of box sizes that the jth supplier produces.

You want to choose a single supplier and use boxes from them such that the total wasted space is minimized. For each package in a box, we define the space wasted to be size of the box - size of the package. The total wasted space is the sum of the space wasted in all the boxes.

For example, if you have to fit packages with sizes [2,3,5] and the supplier offers boxes of sizes [4,8], you can fit the packages of size-2 and size-3 into two boxes of size-4 and the package with size-5 into a box of size-8. This would result in a waste of (4-2) + (4-3) + (8-5) = 6.
Return the minimum total wasted space by choosing the box supplier optimally, or -1 if it is impossible to fit all the packages inside boxes. Since the answer may be large, return it modulo 109 + 7.
*/

// Solution, time: O(n log n + m*(k log k + k log n)), space: O(sort).

/*
Sort all the packages, which takes n log n time. This is good because then, given a certain box, we can easily tell how many packages fit in that box. Iterate through m suppliers, for each supplier, sort the number of boxes they have, which is k log k.
So far, n log n + m*(k log k). Then, for each box, k, do a binary search among the packages to determine the amount of packages that fit into that box. Based on the packages that fit, the packages we have already packed into a smaller box, the sum of all packages, and the sum of the box sizes we have used, we can determine how much space we have wasted.

End time should be n log n + m*(k log k + k log n). Space is O(sort) for the packages / boxes.

A minor efficiency improvement would be to, instead of doing a log search on all the packages for each box, change the boundaries we search in the packages, based on the previous result. So if we have 25 packages and see 10 fit in box 1, we only search the latter 15 packages for box 2.
*/

var minWastedSpace = function (packages, boxes) {
  // sort the packages, so for a given box, we can easily tell how many packages we will fit
  packages.sort((a, b) => a - b);
  // the sum of all packages, we will subtract this from the total space used, to get the space wasted
  const packageSum = packages.reduce((acc, val) => acc + val, 0);
  let minWaste = Infinity;

  for (const supplier of boxes) {
    supplier.sort((a, b) => a - b); // sort one supplier's set of boxes
    // if we cannot fit the biggest package, just move on
    if (supplier[supplier.length - 1] < packages[packages.length - 1]) {
      continue;
    }

    // when we test a supplier's set of boxes, we will go through each box one by one. we will determine how many packages fit into that box. we always use the smallest box possible. so if we can fit some packages into a box of size 3, we check how many we have already packed. then, when we see how many boxes can fit into a box of size 10, we won't double count the ones we already packed
    let packagesAlreadyPacked = 0;
    // totalSpace tracks the total amount of space all boxes of a supplier will use
    let totalSpace = 0;

    // iterate over each box from a supplier. figure out how many packages can fit into this box
    for (const box of supplier) {
      let l = 0;
      let r = packages.length - 1;
      // for every box, do a binary search, looking for the largest package that fits under that size
      while (l <= r) {
        const m = Math.floor((r + l) / 2); // m is the index in packages to try
        const package = packages[m];
        // if the package is too big for the box, we must try a smaller box
        if (package > box) {
          r = m - 1;
        }
        // if the package is too small or equal to the box, we can try fitting in more boxes
        else if (package <= box) {
          l = m + 1;
        }
      }
      /* here, r represents the last package that could fit into the box */
      const totalPackagesThatCanFitInBox = r + 1;
      const totalPackagesUsingThisSize =
        totalPackagesThatCanFitInBox - packagesAlreadyPacked;

      // we are using a certain amount of a new box, add that to the total space usage
      totalSpace += totalPackagesUsingThisSize * box;
      packagesAlreadyPacked += totalPackagesUsingThisSize;
    }

    // the space we wasted is the total amount of box space used, minus the sum of all packages
    const spaceWasted = totalSpace - packageSum;

    minWaste = Math.min(minWaste, spaceWasted);
  }

  if (minWaste === Infinity) {
    return -1;
  }

  return minWaste % (10 ** 9 + 7);
};
// n = # of packages
// n log n = sort packages

// m = # of box suppliers
// k = # of boxes per supplier

// sort all suppliers boxes = m * k log k. or maybe just m log k,  where k is some amortized number such that the sum of all k's is constrainted
