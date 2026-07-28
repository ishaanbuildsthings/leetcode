/**
 * @param {string} address
 * @return {string}
 */
var defangIPaddr = function(address) {
    let result = '';
    for (const letter of address) {
        if (letter === '.') {
            result += '[.]';
        } else {
            result += letter;
        }
    }
    return result;
};