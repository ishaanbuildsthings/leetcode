// const START_CODE = 'A'.charCodeAt(0);

// var convertToTitle = function(columnNumber) {
//     // find # of powers that fit
//     let numberOfLetters = 0;
//     let current = 1;
//     while (current <= columnNumber) {
//         current *= 26;
//         numberOfLetters++;
//     }

//     console.log(`numberOfLetters: ${numberOfLetters}`);

//     // populate result arr
//     const resultArr = [];

//     current = columnNumber;

//     for (let power = numberOfLetters - 1; power >= 0; power--) {
//         const timesThisPowerFitsIn = Math.floor(current / (26**(power)));
//         console.log(`times: ${timesThisPowerFitsIn}`);
//         resultArr.push(timesThisPowerFitsIn);
//         current -= (timesThisPowerFitsIn * 26);
//     }

//     return resultArr;
// };
/**
 * @param {number} columnNumber
 * @return {string}
 */
var convertToTitle = function(columnNumber) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    let result = "";
    
    while (columnNumber) {
        columnNumber--;  // Adjust for 0-based index
        result = chars[columnNumber % 26] + result;
        columnNumber = Math.floor(columnNumber / 26);
    }

    return result;
};