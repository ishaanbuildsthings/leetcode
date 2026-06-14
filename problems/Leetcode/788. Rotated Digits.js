/**
 * @param {number} n
 * @return {number}
 */
var rotatedDigits = function(n) {
    let result = 0;
     for (let i = 1; i <= n; i++) {
         // console.log(`_________`);
         // console.log(`trying: ${i}`);
         const flippedNum = translateNum(i);
         if (flippedNum !== i && flippedNum !== null) {
             result++;
             // console.log(`result is: ${result}`);
         }
     }
     
     return result;
 };
 
 const BAD_NUMS = ['3', '4', '7'];
 
 function translateNum(num) {
     // console.log(`translate on: ${num} called`);
     const arr = String(num).split('');
     for (const badNum of BAD_NUMS) {
         if (arr.includes(badNum)) {
             return null; // if our number has a number that cannot rotate, it is invalid
         }
     }
     
     // console.log(`arr is: ${arr}`);
     
     flippedArr = arr.map(digit => {
         if (digit === '2') {
             return '5';
         } else if (digit === '5') {
             return '2';
         } else if (digit === '6') {
             return '9';
         } else if (digit === '9') {
             return '6';
         } else {
             return digit; // 0, 1, and 8 map to themselves
         }
     });
     
     // console.log(`flipped num is: ${Number(flippedArr.join(''))}`);
     
     return Number(flippedArr.join(''));
 }