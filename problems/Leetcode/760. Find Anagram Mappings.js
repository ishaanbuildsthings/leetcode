/**
 * @param {number[]} nums1
 * @param {number[]} nums2
 * @return {number[]}
 */
var anagramMappings = function(nums1, nums2) {
    const mapping = {}; // maps numbers in nums2 to the index they occur at
    
    for (let i = 0; i < nums2.length; i++) {
        const num = nums2[i];
        mapping[num] = i;
    }
    
    const result = [];
    
    for (const num of nums1) {
        const position = mapping[num];
        result.push(position);
    }
    
    return result;
};