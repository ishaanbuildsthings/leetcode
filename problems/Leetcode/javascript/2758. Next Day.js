/** 
 * @return {string}
 */
Date.prototype.nextDay = function() {
    const nextDate = new Date(this);
    nextDate.setDate(nextDate.getDate() + 1);
    return nextDate.toISOString().slice(0, 10);
}

/**
 * const date = new Date("2014-06-20");
 * date.nextDay(); // "2014-06-21"
 */