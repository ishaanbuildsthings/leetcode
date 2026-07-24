/**
 * @param {Function} callback
 * @param {Object} context
 * @return {void}
 */
Array.prototype.forEach = function(callback, context) {
    for (let i = 0; i < this.length; i++) {
        callback.call(context, this[i], i, this);
    }
}


/**
 *  const arr = [1,2,3];
 *  const callback = (val, i, arr) => arr[i] = val * 2;
 *  const context = {"context":true};
 *
 *  arr.forEach(callback, context)  
 *
 *  console.log(arr) // [2,4,6]
 */