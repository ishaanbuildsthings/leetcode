/**
 * @return {Object}
 */
var createInfiniteObject = function() {
    return new Proxy({}, {
        get(origObj, property) {
            return () => property;
        }
    });
};

/**
 * const obj = createInfiniteObject();
 * obj['abc123'](); // "abc123"
 */