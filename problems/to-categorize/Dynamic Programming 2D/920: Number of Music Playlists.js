// https://leetcode.com/problems/number-of-music-playlists/description/
// Difficulty: Hard
// Tags: Dynamic Programming 2d

// Problem
/*
Your music player contains n different songs. You want to listen to goal songs (not necessarily different) during your trip. To avoid boredom, you will create a playlist so that:

Every song is played at least once.
A song can only be played again only if k other songs have been played.
Given n, goal, and k, return the number of possible playlists that you can create. Since the answer can be very large, return it modulo 109 + 7.
*/

// Solution, O(goal * unique songs) time, O(goal * unique songs) space
/*
This is a hard problem. It relies on a recurrence relationship that, given some prior played songs (we track how many total songs we have played, and how many unique songs we have played), if we re-play an old song, we can play (current unique songs - k) old possible songs. So we just generate the dp from this.
*/

var numMusicPlaylists = function (n, goal, k) {
  const MOD = 10 ** 9 + 7;

  // memo if total songs played, total unique songs

  // memo[current unique songs][total songs] is the answer
  const memo = new Array(goal + 1).fill().map(() => new Array(n + 1).fill(-1));

  function dp(currentUniqueSongs, totalSongs) {
    if (totalSongs === goal) {
      if (currentUniqueSongs === n) {
        return 1;
      }
      return 0;
    }

    if (currentUniqueSongs > n) {
      return 0;
    }

    if (totalSongs > goal) {
      return 0;
    }

    if (memo[totalSongs][currentUniqueSongs] !== -1) {
      return memo[totalSongs][currentUniqueSongs];
    }

    let resultForThis = 0;

    // if we play a new song
    const newSongsToChooseFrom = n - currentUniqueSongs;

    if (newSongsToChooseFrom > 0) {
      const ifNewSong =
        (newSongsToChooseFrom * dp(currentUniqueSongs + 1, totalSongs + 1)) %
        MOD;
      resultForThis += ifNewSong;
    }

    // if we play an old song
    const oldSongsToChooseFrom = currentUniqueSongs - k;

    if (oldSongsToChooseFrom > 0) {
      const ifOldSong =
        (oldSongsToChooseFrom * dp(currentUniqueSongs, totalSongs + 1)) % MOD;
      resultForThis += ifOldSong;
    }

    memo[totalSongs][currentUniqueSongs] = resultForThis % MOD;
    return resultForThis % MOD;
  }

  return dp(0, 0);
};
