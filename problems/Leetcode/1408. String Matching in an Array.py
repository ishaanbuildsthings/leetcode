class Solution:
    def stringMatching(self, words: List[str]) -> List[str]:
        # one idea, combine all words into one big word
        # sum(W) length
        # now for each word, slide over with a rolling hash and check if it appears as a substring of another word
        # w.length * w.length * w[i] time complexity

        # note suffix trie proides an alternate complexity

        res = []
        for w1 in words:
            for w2 in words:
                if w1 == w2:
                    continue
                if w1 in w2:
                    res.append(w1)
                    break
        return res