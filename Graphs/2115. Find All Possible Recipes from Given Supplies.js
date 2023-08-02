// https://leetcode.com/problems/find-all-possible-recipes-from-given-supplies/description/
// Difficulty: Medium
// Tags: topological sort, graph

// Problem
/*
You have information about n different recipes. You are given a string array recipes and a 2D string array ingredients. The ith recipe has the name recipes[i], and you can create it if you have all the needed ingredients from ingredients[i]. Ingredients to a recipe may need to be created from other recipes, i.e., ingredients[i] may contain a string that is in recipes.

You are also given a string array supplies containing all the ingredients that you initially have, and you have an infinite supply of all of them.

Return a list of all the recipes that you can create. You may return the answer in any order.

Note that two recipes may contain each other in their ingredients.
*/

// Solution, O(supplies + recipes + ingredients) time, O(supplies + recipes + ingredients) space (I think lol need to double check)
/*
For each item, we basically need to see if its dependencies are doable. So we dfs out, tracking what is doable (so we don't recompute everything). We also track a path, to detect collisions.
*/

var findAllRecipes = function (recipes, ingredients, supplies) {
  const doableDependencies = {}; // maps a supply or recipe to true/false indicating if it is doable
  for (const supply of supplies) {
    doableDependencies[supply] = true;
  }

  const recipesMapping = {}; // maps a recipe to a list of its ingredients for easy lookup
  for (let i = 0; i < recipes.length; i++) {
    recipesMapping[recipes[i]] = [...ingredients[i]];
  }

  // this basically says that each supply needs no ingredients, so our dfs function works, though we could've fixed the issue in the dfs function as well
  for (const supply of supplies) {
    recipesMapping[supply] = [];
  }

  const path = new Set(); // seen stores the recipe path chain, if we have a collision we cannot make it since we have a circular dependency

  function canMakeRecipe(recipe) {
    path.add(recipe);
    const dependencies = recipesMapping[recipe];

    // say we have an ingredient that isn't ever listed anywhere, then when we dfs to that ingredient, it has no dependencies, so we hardcode a false return
    if (dependencies === undefined) {
      return false;
    }

    for (const dependency of dependencies) {
      // if we have a path collision, we cannot make this (which will trigger a chain of parents not being made)
      if (path.has(dependency)) {
        doableDependencies[recipe] = false;
        path.delete(recipe);
        return false;
      }

      // if we know we can make that child dependency, don't recompute it
      if (doableDependencies[dependency] === true) {
        continue;
      }

      // if we know we cannot make that child dependency, we cannot make the parent
      if (doableDependencies[dependency] === false) {
        path.delete(recipe);
        doableDependencies[recipe] = false;
        return false;
      }

      // if we don't know the child, we try it
      const canMakeDependency = canMakeRecipe(dependency);

      if (!canMakeDependency) {
        doableDependencies[recipe] = false;
        path.delete(recipe);
        return false;
      }
    }

    doableDependencies[recipe] = true;
    path.delete(recipe);
    return true;
  }

  const result = [];
  for (const recipe of recipes) {
    if (canMakeRecipe(recipe)) {
      result.push(recipe);
    }
  }

  return result;
};
