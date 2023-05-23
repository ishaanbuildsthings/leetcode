// brute force with memoized sums and minimums, O(n^2) time and O(1) space

var totalStrength = function (strength) {
  let totalStrength = 0;

  // i represents the left boundary of the subarray, j represents the right
  for (let i = 0; i < strength.length; i++) {
    let dpSum = 0;
    let minimum = Number.POSITIVE_INFINITY;
    for (let j = i; j < strength.length; j++) {
      dpSum += strength[j]; // represents total strength of all wizards in the subarray
      minimum = Math.min(minimum, strength[j]);
      totalStrength += minimum * dpSum;
    }
  }

  return totalStrength % (Math.pow(10, 9) + 7);
};
