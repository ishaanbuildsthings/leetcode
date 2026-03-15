/**
 * @param {number[]} arr
 * @return {string}
 */
var largestTimeFromDigits = function(arr) {
    const frqs = {}; // maps numbers to their frequencies
    
    for (const num of arr) {
        if (num in frqs) {
            frqs[num]++;
        } else {
            frqs[num] = 1;
        }
    }
    
    console.log(`frqs is: ${JSON.stringify(frqs)}`)
    
    const result = [];
    
    // handle first number
    // we cannot use a 2 unless we also have one number <= 5 and one number <= 4, don't double count the 2 itself
    if (frqs[2]) {
        console.log(`found a 2, testing`);
        let numsLTE4 = 0;
        for (let num = 0; num <= 4; num++) {
            if (frqs[num] && num !== 2) {
                numsLTE4 += frqs[num];
            } else if (frqs[num] && num === 2) {
                numsLTE4 += frqs[num] - 1;
            }
        }
        console.log(`total numbers LTE to 4, excluding the 2: ${numsLTE4}`);
        if (numsLTE4 >= 2) {
            result.push(2);
            frqs[2]--;
        } else if (numsLTE4 === 1 && frqs[5] >= 1) {
            result.push(2);
            frqs[2]--;
        }
        
    } 
    // if we use the 1, we must have one number less than or equal to 5
    if (frqs[1] && result.length === 0) {
        let numsLTE5 = 0;
        for (let num = 0; num <= 5; num++) {
            if (frqs[num] && num !== 1) {
                numsLTE5 += frqs[num];
            } else if (frqs[num] && num === 1) {
                numsLTE5 += frqs[num] - 1;
            }
        }
        if (numsLTE5 >= 1) {
            result.push(1);
            frqs[1]--;
        }
        
    } else if (frqs[0] && result.length === 0) {
        console.log(`'pushing 0'`)
        result.push(0);
        frqs[0]--;
    } 
    // no valid number for the starting number
    if (result.length === 0) {
        return '';
    }
    
    console.log(`result is: ${result}`);
    
    // handle second number
    
    // if the first number is a 2, the biggest second number we can use is 3
    if (result[0] === 2) {
        let secondNumFound = false;
        for (let secondNum = 3; secondNum >= 0; secondNum--) {
            if (frqs[secondNum]) {
                result.push(secondNum);
                frqs[secondNum]--;
                secondNumFound = true;
                break;
            }
        }
        if (!secondNumFound) {
            return '';
        }
    } 
    // if the first number is a 0 or 1, we want to pick the biggest number
    else {
        for (let secondNum = 9; secondNum >= 0; secondNum--) {
            if (frqs[secondNum]) {
                result.push(secondNum);
                frqs[secondNum]--;
                break;
            }
        }
    }
    
    console.log(`result is: ${result}`);
    
    // handle the middle of the timer
    result.push(':');
    
    // for the third number, pick the biggest <= 5
    let thirdNumFound = false;
    for (let thirdNum = 5; thirdNum >= 0; thirdNum--) {
        if (frqs[thirdNum]) {
            result.push(thirdNum);
            frqs[thirdNum]--;
            thirdNumFound = true;
            break;
        }
    }
    if (!thirdNumFound) {
        return '';
    }
    
    console.log(`result is: ${result}`);
    
    // for the last number, put whatever is left
    for (let fourthNum = 0; fourthNum <= 9; fourthNum++) {
        if (frqs[fourthNum]) {
            result.push(fourthNum);
            return result.join('');
        }
    }
    
    console.log(`result is: ${result}`);
    
    
};