/**
 * @param {string[]} emails
 * @return {number}
 */
var numUniqueEmails = function(emails) {
    const emailSet = new Set();
    for (const email of emails) {
        emailSet.add(getMappedEmail(email));
    }
    
    return Array.from(emailSet).length;
};

// could be more efficient with pointers, just using slice/split/indexof to make implementation a bit easier
function getMappedEmail(email) {
    const arr = email.split('@');
    let local = arr[0];
    const firstPlus = local.indexOf('+');
    // if we have a plus sign, splice it out
    if (firstPlus !== -1) {
        local = local.slice(0, firstPlus);
    }
    
    const localArr = local.split('');
    const localArrNoPeriods = localArr.filter(char => char !== '.');
    
    const parsedLocal = localArrNoPeriods.join('');
    const domain = arr[1];
    
    const constructedEmail = parsedLocal + '@' + domain;
    
    return constructedEmail;
}