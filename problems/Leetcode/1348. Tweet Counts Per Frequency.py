class TweetCounts:

    def __init__(self):
        self.t = SortedList() # (timeSeconds, tweet)

    def recordTweet(self, tweetName: str, time: int) -> None:
        self.t.add((time, tweetName))

    def getTweetCountsPerFrequency(self, freq: str, tweetName: str, startTime: int, endTime: int) -> List[int]:
        left = self.t.bisect_left((startTime,))
        right = self.t.bisect_left((endTime + 1,))
        size = {'minute' : 60, 'hour' : 3600, 'day' : 86400}[freq]
        buckets = ceil((endTime - startTime + 1) / size)
        out = [0] * buckets
        for time, name in self.t[left:right]:
            if name != tweetName:
                continue
            # map this time to its chunk
            idx = (time - startTime) // size
            out[idx] += 1
        return out
        


# Your TweetCounts object will be instantiated and called as such:
# obj = TweetCounts()
# obj.recordTweet(tweetName,time)
# param_2 = obj.getTweetCountsPerFrequency(freq,tweetName,startTime,endTime)