// https://leetcode.com/problems/smallest-sufficient-team/description/
// Difficulty: Hard
// Tags: Dynamic Programming 2d

// Problem
/*
In a project, you have a list of required skills req_skills, and a list of people. The ith person people[i] contains a list of skills that the person has.

Consider a sufficient team: a set of people such that for every required skill in req_skills, there is at least one person in the team who has that skill. We can represent these teams by the index of each person.

For example, team = [0, 1, 3] represents the people with skills people[0], people[1], and people[3].
Return any sufficient team of the smallest possible size, represented by the index of each person. You may return the answer in any order.

It is guaranteed an answer exists.
*/

// Solution, k*2^n * (n^2 + k) time and k*2^n space
/*
At any point, we can either take a person, or not. Leaving us with a subproblem of [people left][skills currently taken]. We represent the skills taken with a mask.

There are up to 16 (n) skills, and up to 60 (k) people. This means there are 2^n masks and a memo table of 2^n * k. For each memo state, we iterate through the number of skills a person has, which is n, and then do a bit shift of n, so n^2. We also do a serialization of up to k people. So k*2^n * (n^2 + k)
*/

var smallestSufficientTeam = function (req_skills, people) {
  /*
    if we take a person, we may add their skills, we look at [skills we receive, ...dp[i+1:]], given a certain mask of arrangements
    */
  // memo[i][mask] gives the answer to the problem where we have [i:] people left, and the mask amount of skills handled already
  const memo = new Array(people.length).fill().map(() => ({}));

  let FILLED_MASK = 0; // for instance if we have 3 skills, 0...0111 is a filled mask, meaning we have every skill
  for (let i = 0; i < req_skills.length; i++) {
    FILLED_MASK = FILLED_MASK | (1 << i);
  }

  const skillMapping = {}; // maps a skill to its position in the mask
  for (let i = 0; i < req_skills.length; i++) {
    const skill = req_skills[i];
    skillMapping[skill] = i;
  }

  function dp(i, mask) {
    // base case, all skilled are taken
    if (mask === FILLED_MASK) {
      return [];
    }

    // base case, we have no people left to consider, so it isn't possible
    if (i === people.length) {
      return null;
    }

    if (memo[i][mask] !== undefined) {
      return memo[i][mask];
    }

    let newMask = mask;
    // if we do take the ith person
    const ithPersonSkills = people[i];
    for (const skill of ithPersonSkills) {
      const skillNumber = skillMapping[skill];
      const bit = 1 << skillNumber;
      newMask = newMask | bit;
    }

    const otherPeopleIfTake = dp(i + 1, newMask);

    const options = [];

    if (otherPeopleIfTake !== null) {
      options.push([i, ...otherPeopleIfTake]);
    }

    const otherPeopleIfSkip = dp(i + 1, mask);

    if (otherPeopleIfSkip !== null) {
      options.push([...otherPeopleIfSkip]);
    }

    if (options.length === 0) {
      memo[i][mask] = null;
      return null;
    }

    if (options.length === 1) {
      memo[i][mask] = options[0];
      return options[0];
    }

    if (options[0].length <= options[1].length) {
      memo[i][mask] = options[0];
      return options[0];
    }

    memo[i][mask] = options[1];
    return options[1];
  }

  return dp(0, 0);
};
