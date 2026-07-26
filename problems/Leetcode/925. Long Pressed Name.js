/**
 * @param {string} name
 * @param {string} typed
 * @return {boolean}
 */
var isLongPressedName = function(name, typed) {
    let p1 = 0; // iterates over the name
    let p2 = 0; // iterates over what is typed
    while (p1 < name.length) {
        console.log(`p1 is: ${p1} p2 is: ${p2}`)
        // while analyzing new characters, if they are different we cannot have made the name
        if (name[p1] !== typed[p2]) {
            console.log(`letter mismatch, false!`)
            return false;
        }
        
        let charCount1 = 0; // will track how many characters in a row we have for a given char in `name`
        // increment p1 while the next letter is the same
        while (name[p1] === name[p1 + 1]) {
            p1++;
            charCount1++;
        }
        
        let charCount2 = 0; // tracks the # of digits in a row in typed
        while (typed[p2] === typed[p2 + 1]) {
            p2++;
            charCount2++;
        }
        
        // if we had more letters in a row in name, then it is not possible
        if (charCount1 > charCount2) {
            console.log(`too many chars in a row in typed`)
            return false;
        }
        
        // look at the next characters
        p1++;
        p2++;
        
    }
    
    // if we still have extra letters in the end in typed, it is invalid
    if (p2 < typed.length) {
        return false;
    }
    return true;
};