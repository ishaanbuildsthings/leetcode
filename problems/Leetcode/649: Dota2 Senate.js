// https://leetcode.com/problems/dota2-senate/description/
// Difficulty: Medium
// tags: array (more like strings), queue, recursion

// Problem
/*
Example:

Input: senate = "RDD"
Output: "Dire"
Explanation:
The first senator comes from Radiant and he can just ban the next senator's right in round 1.
And the second senator can't exercise any rights anymore since his right has been banned.
And the third senator comes from Dire and he can ban the first senator's right in round 1.
And in round 2, the third senator can just announce the victory since he is the only guy in the senate who can vote.

Detailed:
In the world of Dota2, there are two parties: the Radiant and the Dire.

The Dota2 senate consists of senators coming from two parties. Now the Senate wants to decide on a change in the Dota2 game. The voting for this change is a round-based procedure. In each round, each senator can exercise one of the two rights:

Ban one senator's right: A senator can make another senator lose all his rights in this and all the following rounds.
Announce the victory: If this senator found the senators who still have rights to vote are all from the same party, he can announce the victory and decide on the change in the game.
Given a string senate representing each senator's party belonging. The character 'R' and 'D' represent the Radiant party and the Dire party. Then if there are n senators, the size of the given string will be n.

The round-based procedure starts from the first senator to the last senator in the given order. This procedure will last until the end of voting. All the senators who have lost their rights will be skipped during the procedure.

Suppose every senator is smart enough and will play the best strategy for his own party. Predict which party will finally announce the victory and change the Dota2 game. The output should be "Radiant" or "Dire".
*/

// Solution 1, O(n) time and O(n) space, simulation
// * Solution 2 below is a better simulation solution, no need to hold extra queues, just carry over extra bans to the next iteration (see solution 1 description for details).
// * Solution 3 is a slow literal string simulation that I wrote when I started.
/*
This approach simulates a greedy strategy, where each senator wants to ban the closest next senator.

Say we have RDDR. We iterate, and see R. R will want to ban the next D. We don't yet know where the next D is, instead of linearly scanning each time, we maintain an "extra bans on D" count. We get to the D, they are banned, so they get added to the banned set, so we skip that index. At the second D, we now get an extra ban on R, subsequently the last R is banned. Now, when we iterate again, the first R will ban that D again, winning. We track winning by checking the total banned amount and comparing it to the total amount of each type we started with.

Initially, I realized that we might not be able to ban something to the right, if there is nothing there. For instance in DDRRRR. The R's have nothing to ban. I ended up creating unbanned queues, and adding senators into that, so at the end of the loop, any extra bans would be used to ban the earliest unbanned members. So the first two D's would be added to this queue, and at the end of the first loop, each extra ban would ban one of those. However, I think we can just do another loop, carrying over the extra bans we have, which will be in solution 2.

The time complexity is O(n) because the iterations are amortized. If each person can ban one other person, maybe the first time we run a loop of N, and each person bans one person, so we have 50 people remaining. The same thing will happen again, leaving 25, etc. It's just 100+50+25+12.5... which is the infinite series that forms 2n.
*/

var predictPartyVictory = function (senate) {
  // get a count of how many of each there are, so we know when we have banned them all
  let totalR = 0;
  let totalD = 0;

  for (const senator of senate) {
    if (senator === "R") {
      totalR++;
    } else {
      totalD++;
    }
  }

  // stores indices of unbanned senators we have seen, so if we have extra bans we will retroactively use them, for instance DRR, R has an extra ban at the end, so we would dequeue from unbannedD to ban them
  const unbannedR = []; // pretend deque
  const unbannedD = [];

  // say we have RRRD, at the first R, we don't know where the next D is, so we carry a running tally so we can greedily ban the D when we see it
  let extraBansOnR = 0;
  let extraBansOnD = 0;

  // stores indices of banned senators, so we can skip over them in future rounds
  let bannedR = new Set();
  let bannedD = new Set();

  while (true) {
    for (let i = 0; i < senate.length; i++) {
      // if at any point the total bans for some party is equal to the number of their participants, they lose
      if (bannedR.size === totalR) {
        return "Dire";
      } else if (bannedD.size === totalD) {
        return "Radiant";
      }

      // if this senator was already banned, skip them
      if (bannedR.has(i) || bannedD.has(i)) {
        continue;
      }

      if (senate[i] === "R") {
        // if we reach an R senator, but there were carryover bans, ban them
        if (extraBansOnR > 0) {
          bannedR.add(i);
          extraBansOnR--;
          continue;
        }

        // if there were no carryover bans, now we can ban a D later
        extraBansOnD++;
        unbannedR.push(i);
      } else if (senate[i] === "D") {
        // if we reach a D senator, but there were carryover bans, ban them
        if (extraBansOnD > 0) {
          bannedD.add(i);
          extraBansOnD--;
          continue;
        }

        // if there were no carryover bans, now we can ban an R
        extraBansOnR++;
        unbannedD.push(i);
      }
    }

    // check again since the for loop just ended, maybe the last iteration triggered a win
    if (bannedR.size === totalR) {
      return "Dire";
    } else if (bannedD.size === totalD) {
      return "Radiant";
    }

    /* here, after a full for loop run, we might have some extra carryover bans for one party */
    while (extraBansOnR > 0) {
      const bannableIndex = unbannedR.shift();
      bannedR.add(bannableIndex);
      if (bannedR.size === totalR) {
        return "Dire";
      }
      extraBansOnR--;
    }

    while (extraBansOnD > 0) {
      const bannableIndex = unbannedD.shift();
      bannedD.add(bannableIndex);
      if (bannedD.size === totalD) {
        return "Radiant";
      }
      extraBansOnD--;
    }
  }
};

// Solution 2, better simulation without extra queues for unbanned participants

var predictPartyVictory = function (senate) {
  // get a count of how many of each there are, so we know when we have banned them all
  let totalR = 0;
  let totalD = 0;

  for (const senator of senate) {
    if (senator === "R") {
      totalR++;
    } else {
      totalD++;
    }
  }

  // say we have RRRD, at the first R, we don't know where the next D is, so we carry a running tally so we can greedily ban the D when we see it. we carry these over to the next iteration too, like in DDRRR, the ending R has nothing to ban.
  let extraBansOnR = 0;
  let extraBansOnD = 0;

  // stores indices of banned senators, so we can skip over them in future rounds
  let bannedR = new Set();
  let bannedD = new Set();

  while (true) {
    for (let i = 0; i < senate.length; i++) {
      // if at any point the total bans for some party is equal to the number of their participants, they lose
      if (bannedR.size === totalR) {
        return "Dire";
      } else if (bannedD.size === totalD) {
        return "Radiant";
      }

      // if this senator was already banned, skip them
      if (bannedR.has(i) || bannedD.has(i)) {
        continue;
      }

      if (senate[i] === "R") {
        // if we reach an R senator, but there were carryover bans, ban them
        if (extraBansOnR > 0) {
          bannedR.add(i);
          extraBansOnR--;
          continue;
        }

        // if there were no carryover bans, now we can ban a D later
        extraBansOnD++;
      } else if (senate[i] === "D") {
        // if we reach a D senator, but there were carryover bans, ban them
        if (extraBansOnD > 0) {
          bannedD.add(i);
          extraBansOnD--;
          continue;
        }

        // if there were no carryover bans, now we can ban an R
        extraBansOnR++;
      }
    }

    // check again since the for loop just ended, maybe the last iteration triggered a win
    if (bannedR.size === totalR) {
      return "Dire";
    } else if (bannedD.size === totalD) {
      return "Radiant";
    }
  }
};

// Solution 3, string simulation with recursion, Literally iterate through, for each person, find who we can ban, ban them, remove them from the string, then recurse the problem. I wrote this when I just started.

var predictPartyVictory = function (senate) {
  const occurences = { R: 0, D: 0 };

  for (const char of senate) {
    occurences[char]++;
  }

  function recurse(string, turnIndex) {
    if (turnIndex >= string.length) {
      turnIndex = 0;
    }
    // base case, if we have only one type left, return that type
    if (
      (occurences["R"] > 0 && occurences["D"] === 0) ||
      (occurences["D"] > 0 && occurences["R"] === 0)
    ) {
      return occurences["R"] > 0 ? "Radiant" : "Dire";
    }

    // check for peoples turns after
    for (let i = turnIndex + 1; i < string.length; i++) {
      // found an opposite voter
      if (string[i] !== string[turnIndex]) {
        occurences[string[i]]--;
        string = string.slice(0, i) + string.slice(i + 1);
        return recurse(string, turnIndex + 1);
      }
    }
    // check for peoples turns from the beginning
    for (let i = 0; i < string.length; i++) {
      if (string[i] !== string[turnIndex]) {
        occurences[string[i]]--;
        string = string.slice(0, i) + string.slice(i + 1);
        return recurse(string, turnIndex);
      }
    }
  }
  return recurse(senate, 0);
};
