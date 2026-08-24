/**
 * @param {number[]} nums
 * @return {number}
 */
var numberOfArithmeticSlices = function(nums) {
    let result = 0;
    
    let lengthOfArithmeticArray = 0;
    // start at the 3rd element so we can see the prior two
    for (let i = 2; i < nums.length; i++) {
        // if the last three terms are arithmetic, that is good
        if (nums[i] - nums[i - 1] === nums[i - 1] - nums[i - 2]) {
            if (lengthOfArithmeticArray === 0) {
                lengthOfArithmeticArray = 3;
            } else {
                lengthOfArithmeticArray++;
            }
            result += (lengthOfArithmeticArray - 2);
        } else {
           lengthOfArithmeticArray = 0; 
        }
    }
    
    return result;
};