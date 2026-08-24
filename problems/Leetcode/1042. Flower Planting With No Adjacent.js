/**
 * @param {number} n
 * @param {number[][]} paths
 * @return {number[]}
 */
var gardenNoAdj = function(n, paths) {
    const result = [];
    
    // make a bidirectional mapping to know all the paths
    const mapping = {}; // for instance if we have [1, 2], 1 : [2] and 2 : [1] will be inserted
    for (const path of paths) {
        const left = path[0];
        const right = path[1];
        if (left in mapping) {
            mapping[left].push(right);
        } else {
            mapping[left] = [right];
        }
        
        if (right in mapping) {
            mapping[right].push(left);
        } else {
            mapping[right] = [left];
        }
    }
    
    // console.log(`mapping is: ${JSON.stringify(mapping)}`);
            
    // iterate over each garden one at a time
    for (let i = 1; i <= n; i++) {
        // if that garden had no paths, just put a 1
        if (!(i in mapping)) {
            result[i - 1] = 1;
            continue;
        }
        // console.log(`garden: ${i}`);
        const neighbors = mapping[i];
        // console.log(`garden ${i}'s neighbors: ${neighbors}`);

                
        let firstMissing;
        
        // we have most 4 flower types, greedily select the earliest one we can use
        for (let type = 1; type <= 4; type++) {
            // console.log(`type: ${type}`)
            let typeFound = false;
            for (const neighbor of neighbors) {
                // console.log(`neighbor: ${neighbor}`);
                const neighborFlower = result[neighbor - 1];
                // console.log(`neighborflower: ${neighborFlower}`);
                if (neighborFlower === type) {
                    typeFound = true;
                }
            }
            if (!typeFound) {
                firstMissing = type;
                break;
            }
        }
        
        // console.log(`first missing: ${firstMissing}`);
        
        const resultIndex = i - 1; // zero-indexed
        result[resultIndex] = firstMissing; 
        
        // console.log(`result: ${result}`);
    }
    
    return result;
};