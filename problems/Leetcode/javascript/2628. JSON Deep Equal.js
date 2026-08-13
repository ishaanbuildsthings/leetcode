/**
 * @param {null|boolean|number|string|Array|Object} o1
 * @param {null|boolean|number|string|Array|Object} o2
 * @return {boolean}
 */
var areDeeplyEqual = function(o1, o2) {
    const areArrays = Array.isArray(o1) && Array.isArray(o2);
    const areObjects = typeof o1 === 'object' && o1 !== null && !Array.isArray(o1) && typeof o2 === 'object' && o2 !== null && !Array.isArray(o2);

    if (!areArrays && !areObjects) return o1 === o2;

    if (areArrays) {
        if (o1.length !== o2.length) return false;
        for (let i = 0; i < o1.length; i++) {
            obj1 = o1[i];
            obj2 = o2[i];
            if (!areDeeplyEqual(obj1, obj2)) return false;
        }
        return true;
    }

    const k1 = Object.keys(o1);
    const k2 = Object.keys(o2);
    if (k1.length !== k2.length) return false;
    for (const key of k1) {
        if (!(key in o2)) return false;
        if (!areDeeplyEqual(o1[key], o2[key])) return false;
    }
    return true;
};