/**
 * @param {string[]} wordsDict
 * @param {string} word1
 * @param {string} word2
 * @return {number}
 */
var shortestDistance = function(wordsDict, word1, word2) {
    let rightmostWord1 = -Infinity;
    let rightmostWord2 = -Infinity;
    
    let result = Infinity;
    
    for (let i = 0; i < wordsDict.length; i++) {
        const word = wordsDict[i];
        if (word === word1) {
            const distance = i - rightmostWord2;
            result = Math.min(result, distance);
            rightmostWord1 = i;
        } else if (word === word2) {
            const distance = i - rightmostWord1;
            result = Math.min(result, distance);
            rightmostWord2 = i;
        }
    }
    
    return result;
};