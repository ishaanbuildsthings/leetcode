/**
 * @param {string} s
 * @return {boolean}
 */
var checkRecord = function(s) {
   let absentCount = 0;
    
    for (let i = 0; i < s.length; i++) {
        if (s[i] === 'A') {
            absentCount++;
        }
        
        if (absentCount > 1) {
            return false;
        }
        
        if (s.slice(i, i + 3) === 'LLL') {
            return false;
        }
    }
    
    return true;
};