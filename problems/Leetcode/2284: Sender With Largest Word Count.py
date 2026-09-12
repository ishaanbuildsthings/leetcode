# https://leetcode.com/problems/sender-with-largest-word-count/description/
# difficulty: medium

# problem
# You have a chat log of n messages. You are given two string arrays messages and senders where messages[i] is a message sent by senders[i].

# A message is list of words that are separated by a single space with no leading or trailing spaces. The word count of a sender is the total number of words sent by the sender. Note that a sender may send more than one message.

# Return the sender with the largest word count. If there is more than one sender with the largest word count, return the one with the lexicographically largest name.

# Note:

# Uppercase letters come before lowercase letters in lexicographical order.
# "Alice" and "alice" are distinct.

# Solution, O(messages*senders*message length) time, O(senders) space
# Iterate over each message / sender for that message. For each message, count the spaces to get the number of words (which is faster cycles than splitting messages into an array and counting that, and also uses less memory). We store up to senders memory for the hashmap.

def countWords(message):
    count = 1
    for char in message:
        if char == ' ':
            count += 1
    return count

class Solution:
    def largestWordCount(self, messages: List[str], senders: List[str]) -> str:
        people = defaultdict(int) # maps people to how many messages they have sent

        for i in range(len(messages)):
            people[senders[i]] += countWords(messages[i])

        maxPerson = None
        maxMessages = 0
        for person in people.keys():
            messageCount = people[person]
            if messageCount > maxMessages or (messageCount == maxMessages and person > maxPerson):
                maxMessages = messageCount
                maxPerson = person
        return maxPerson
