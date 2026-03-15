/**
 * @param {string} s
 * @return {string}
 */
var makeSmallestPalindrome = function(s) {
    let l = 0;
    let r = s.length - 1;
    const arr = s.split('');
    
    while (l < r) {
        if (arr[l] === arr[r]) {
            
        } else {
            if (arr[l].charCodeAt(0) < arr[r].charCodeAt(0)) {
                arr[r] = arr[l];
            } else {
                arr[l] = arr[r];
            }
        }
        l++;
        r--;
    }
    return arr.join('');
};