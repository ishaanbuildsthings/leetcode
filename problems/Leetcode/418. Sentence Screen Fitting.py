class Solution:
    def wordsTyping(self, sentence: List[str], rows: int, cols: int) -> int:
        # brute force version, rows * columns (TLE)
        # note the nice trick we just put a space after every word even on the first word, if that space clips over the end nothing changes
        # res = 0
        # wordI = 0
        # for _ in range(rows):
        #     col = 0
        #     while col + len(sentence[wordI]) <= cols:
        #         col += len(sentence[wordI])
        #         col += 1
        #         wordI += 1
        #         if wordI == len(sentence):
        #             res += 1
        #             wordI = 0
        # return res



        # for every word, if it were the start of the sentence, what new word do we end on and how many full times did we fit the sentence?
        # O(words * cols) to compute, then just O(rows) time
        # nxt = [0] * len(sentence)
        # gain = [0] * len(sentence)
        # for i in range(len(sentence)):
        #     size = 0
        #     j = i
        #     score = 0
        #     while size + len(sentence[j]) <= cols:
        #         size += len(sentence[j])
        #         j += 1
        #         if j == len(sentence):
        #             score += 1
        #             j = 0
        #         size += 1 # add the space
        #     nxt[i] = j
        #     gain[i] = score
        
        # res = 0
        # i = 0
        # for _ in range(rows):
        #     res += gain[i]
        #     i = nxt[i]
        # return res


        # same as the above solution but now I don't want to iterate on each row, so we use jump tables
        #O(words * cols) + words * log(rows)
        # nxt = [0] * len(sentence)
        # gain = [0] * len(sentence)
        # for i in range(len(sentence)):
        #     size = 0
        #     j = i
        #     score = 0
        #     while size + len(sentence[j]) <= cols:
        #         size += len(sentence[j])
        #         j += 1
        #         if j == len(sentence):
        #             score += 1
        #             j = 0
        #         size += 1 # add the space
        #     nxt[i] = j
        #     gain[i] = score
        

        # # easier to write these two in one function

        # @cache
        # def nxtJump(power, i):
        #     if power == 0:
        #         return nxt[i]
        #     half = nxtJump(power - 1, i)
        #     full = nxtJump(power - 1, half)
        #     return full
        
        # # we are going 2^power of rows, starting at i, how many sentences do we gain
        # @cache
        # def gainJump(power, i):
        #     if power == 0:
        #         return gain[i]
        #     halfGain = gainJump(power - 1, i)
        #     half = nxtJump(power - 1, i)
        #     full = halfGain + gainJump(power - 1, half)
        #     return full
        
        # res = 0
        # wordI = 0
        # for bit in range(32):
        #     if (1 << bit) & rows:
        #         res += gainJump(bit, wordI)
        #         wordI = nxtJump(bit, wordI)
        # return res
        







