/**
 * @param {Function} fn
 * @param {number} delay
 * @param {number} period
 * @return {number} id
 */

let nextFreeId = 0;
const mp = new Map(); // maps function call id -> clear id
function customInterval(fn, delay, period){
    let iterations = 0;
    let currId = nextFreeId;
    nextFreeId++;
    const single = () => {
        fn();
        iterations++;
        // call this again after the required time
        const clearId = setTimeout(single, delay + period * iterations);
        mp.set(currId, clearId);
    };
    // kick off the call once which will then call itself
    const outer = setTimeout(single, delay + period * iterations);
    mp.set(currId, outer);

    return currId;
}

/**
 * @param {number} id
 * @return {void}
 */
function customClearInterval(id) {
    clearTimeout(mp.get(id));
}