/**
 * @param {Object|Array} obj
 * @return {Object|Array} immutable obj
 */
var makeImmutable = function(obj) {
    return new Proxy(obj, {
        // tricky, stuff like arr.push is basically a get call
        // key is the name whether obj.foo or obj.push
        get(origObject, key) {
            if (Array.isArray(origObject) && ['pop', 'push', 'shift', 'unshift', 'splice', 'sort', 'reverse'].includes(key)) {
                return () => {throw `Error Calling Method: ${key}`;}
            }
            // we have to prevent stuff like obj.arr.push so this is needed
            const val = origObject[key];
            if (val !== null && typeof val === 'object') {
                return makeImmutable(val);
            }
            return val;
        },
        set(origObject, key, value) {
            if (Array.isArray(origObject)) {
                throw `Error Modifying Index: ${key}`;
            } else {
                throw `Error Modifying: ${key}`;
            }
        }
    });
};

/**
 * const obj = makeImmutable({x: 5});
 * obj.x = 6; // throws "Error Modifying x"
 */