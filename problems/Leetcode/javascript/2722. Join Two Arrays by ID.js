/**
 * @param {Array} arr1
 * @param {Array} arr2
 * @return {Array}
 */
var join = function(arr1, arr2) {
    const mergedObj = {};
    for (const obj of arr1) {
        mergedObj[obj.id] = obj;
    }
    for (const obj of arr2) {
        if (!mergedObj[obj.id]) {
            mergedObj[obj.id] = obj;
        } else {
            const newObj = {
                ...mergedObj[obj.id],
                ...obj
            };
            mergedObj[obj.id] = newObj;
        }
    }
    return Object.values(mergedObj);
};