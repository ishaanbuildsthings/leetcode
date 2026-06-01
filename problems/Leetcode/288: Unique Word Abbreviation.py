# https://leetcode.com/problems/unique-word-abbreviation/description/
# difficulty: medium

# Problem
# The abbreviation of a word is a concatenation of its first letter, the number of characters between the first and last letter, and its last letter. If a word has only two characters, then it is an abbreviation of itself.

# For example:

# dog --> d1g because there is one letter between the first letter 'd' and the last letter 'g'.
# internationalization --> i18n because there are 18 letters between the first letter 'i' and the last letter 'n'.
# it --> it because any word with only two characters is an abbreviation of itself.
# Implement the ValidWordAbbr class:

# ValidWordAbbr(String[] dictionary) Initializes the object with a dictionary of words.
# boolean isUnique(string word) Returns true if either of the following conditions are met (otherwise returns false):
# There is no word in dictionary whose abbreviation is equal to word's abbreviation.
# For any word in dictionary whose abbreviation is equal to word's abbreviation, that word and word are the same.

# Solution
# Store the abbreviations, we don't need to store everything just one word

class ValidWordAbbr:

    def __init__(self, dictionary: List[str]):
        # don't need to store everything
        self.abbrvs = defaultdict(set)
        for word in dictionary:
            abbrv = self._abbrv(word)
            self.abbrvs[abbrv].add(word)

    def _abbrv(self, word):
        return (
            word if len(word) <= 2 else
            word[0] + str(len(word) - 2) + word[-1]
        )

    def isUnique(self, word: str) -> bool:
        abbrv = self._abbrv(word)
        return (
            len(self.abbrvs[abbrv]) == 0 or
            (len(self.abbrvs[abbrv]) == 1 and list(self.abbrvs[abbrv])[0] == word)
        )


# Your ValidWordAbbr object will be instantiated and called as such:
# obj = ValidWordAbbr(dictionary)
# param_1 = obj.isUnique(word)