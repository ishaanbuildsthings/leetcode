from sortedcontainers import SortedList

class Twitter:
    def __init__(self):
        self.tweets = defaultdict(lambda: collections.deque()) # tweet is (time, id)
        self.userToFollowers = defaultdict(set)
        self.userToFollowing = defaultdict(set)
        self.time = 0

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.tweets[userId].append((self.time, tweetId))
        self.time += 1
        if len(self.tweets[userId]) > 10:
            self.tweets[userId].popleft()

    def getNewsFeed(self, userId: int) -> List[int]:
        res = SortedList() # max size 10
        imFollowing = list(self.userToFollowing[userId]) + [userId]
        for star in imFollowing:
            theirTweets = self.tweets[star]
            for time, tweetId in theirTweets:
                res.add((time, tweetId))
                if len(res) > 10:
                    res.pop(0)
        timeAndTweet = list(res)[::-1]
        tweets = [tup[1] for tup in timeAndTweet]
        return tweets


    def follow(self, followerId: int, followeeId: int) -> None:
        try:
            self.userToFollowers[followeeId].add(followerId)
        except:
            pass
        try:
            self.userToFollowing[followerId].add(followeeId)
        except:
            pass

    def unfollow(self, followerId: int, followeeId: int) -> None:
        try:
            self.userToFollowers[followeeId].remove(followerId)
        except:
            pass
        try:
            self.userToFollowing[followerId].remove(followeeId)
        except:
            pass


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)