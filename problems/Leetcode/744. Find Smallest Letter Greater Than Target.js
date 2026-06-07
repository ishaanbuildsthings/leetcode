function getNum(char) {
    return char.charCodeAt(0);
}

var nextGreatestLetter = function(letters, target) {
    const targetNum = getNum(target);
    let lowest = Infinity;
    let smallestLetter;

    for (const char of letters) {
        const code = getNum(char);
        if (code < lowest && code > targetNum) {
            smallestLetter = char;
            lowest = code;
        }
    }

    return smallestLetter === undefined ? letters[0] : smallestLetter;

};