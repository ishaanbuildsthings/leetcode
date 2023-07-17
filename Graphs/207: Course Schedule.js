// https://leetcode.com/problems/course-schedule/description/
// Difficulty: Medium
// Tags: graphs

// Problem
/*
There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1. You are given an array prerequisites where prerequisites[i] = [ai, bi] indicates that you must take course bi first if you want to take course ai.

For example, the pair [0, 1], indicates that to take course 0 you have to first take course 1.
Return true if you can finish all courses. Otherwise, return false.
*/

// Solution, O(V+E) time and O(V+E) space
/*
Since we have to take every course, the only time we can't take a course is if there is a cycle. So this question boils down to finding if there is a cycle in a directed, unconnected graph.

We first construct the proper adjacency mapping. Each course maps to a list of courses that need to be taken before it. Initially I had it reversed, so it is good to consider both ways.

Then we iterate over each course. For each course, we seaerch all paths seeing if there is a cycle. We check all neighbors to see if any of them have a cycle, and if not, we return false. We cache the results of safe nodes so we don't need to recompute. Since each node is solved once, and for each node we consider every edge, the time is V+E.
*/

var canFinish = function (numCourses, prerequisites) {
  // maps a course to a list of courses that must be taken before it
  const prereqs = {};

  for (const [post, pre] of prerequisites) {
    if (!(post in prereqs)) {
      prereqs[post] = [pre];
    } else {
      prereqs[post].push(pre);
    }
    if (!(pre in prereqs)) {
      prereqs[pre] = [];
    }
  }

  for (let course = 0; course <= numCourses - 1; course++) {
    if (!(course in prereqs)) {
      prereqs[course] = [];
    }
  }

  const safeCourses = new Set();
  const path = new Set();

  // starts at a course, iterates through all paths from that course, seeing if it can make a cycle (not necessarily returning back to the course, but if there is a cycle anywhere)
  function hasCycle(course) {
    path.add(course);

    const coursesNeededBefore = prereqs[course];

    // if we are at a base course with no prereqs, there is no path to take and therefore no cycle
    if (coursesNeededBefore.length === 0) {
      path.delete(course);
      safeCourses.add(course); // not super needed, we would just enter the recursive call anyway
      return false;
    }

    for (const neededCourse of coursesNeededBefore) {
      if (safeCourses.has(neededCourse)) {
        continue;
      }

      if (path.has(neededCourse)) {
        return true;
      }

      if (hasCycle(neededCourse)) {
        return true;
      }
    }

    path.delete(course);
    safeCourses.add(course);
    return false;
  }

  for (let course = 0; course <= numCourses - 1; course++) {
    if (hasCycle(course)) {
      return false;
    }
  }

  return true;
};

// * Solution 2, I initially had an overcomplicated solution where I didn't fully read the problem statement. I thought that we had a target number of courses to finish, resulting in more complex code:

var canFinish = function (numCourses, prerequisites) {
  // maps a course to a list of courses that must be taken before it
  const prereqs = {};

  for (const [post, pre] of prerequisites) {
    if (!(post in prereqs)) {
      prereqs[post] = [pre];
    } else {
      prereqs[post].push(pre);
    }
    if (!(pre in prereqs)) {
      prereqs[pre] = [];
    }
  }

  for (let course = 0; course <= numCourses - 1; course++) {
    if (!(course in prereqs)) {
      prereqs[course] = [];
    }
  }

  const safeCourses = new Set();
  const unsafeCourses = new Set();
  const path = new Set();

  function dfs(course) {
    path.add(course);

    const coursesNeededBefore = prereqs[course];

    // if there are no courses needed before, we can always take this course
    if (coursesNeededBefore.length === 0) {
      path.delete(course);
      return;
    }

    // we dfs down all paths of prereqs, if one of the neighbor courses yields a cycle on the path, it means the current course cannot be taken (nor any course along that path up to that point, which will be logged while the recursion bubbles up)
    for (const neededCourse of coursesNeededBefore) {
      if (path.has(neededCourse)) {
        unsafeCourses.add(course);
        path.delete(course);
        return;
      }

      // if one of the courses we need before cannot be taken, the main course can also not be taken
      if (unsafeCourses.has(neededCourse)) {
        unsafeCourses.add(course);
        path.delete(course);
        return;
      }

      // extra caching, for instance in 1->2->3->, if we determine 3 is a safe course, we shouldn't recompute for 1 and 2
      if (safeCourses.has(neededCourse)) {
        continue;
      }

      dfs(neededCourse);
    }

    path.delete(course);
    safeCourses.add(course);
  }

  // try taking every course
  for (let course = 0; course <= numCourses - 1; course++) {
    dfs(course);
  }

  console.log(`unsafe courses: ${JSON.stringify(Array.from(unsafeCourses))}`);

  const totalCourses = Object.keys(prereqs).length;

  const numberUnsafe = Array.from(unsafeCourses).length;

  return totalCourses - numberUnsafe >= numCourses;
};
