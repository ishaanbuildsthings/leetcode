# https://leetcode.com/problems/reward-top-k-students/
# difficulty: medium
# tags: heap, functional

# Problem
# You are given two string arrays positive_feedback and negative_feedback, containing the words denoting positive and negative feedback, respectively. Note that no word is both positive and negative.

# Initially every student has 0 points. Each positive word in a feedback report increases the points of a student by 3, whereas each negative word decreases the points by 1.

# You are given n feedback reports, represented by a 0-indexed string array report and a 0-indexed integer array student_id, where student_id[i] represents the ID of the student who has received the feedback report report[i]. The ID of each student is unique.

# Given an integer k, return the top k students after ranking them in non-increasing order by their points. In case more than one student has the same points, the one with the lower ID ranks higher.

# Solution
# Standard stuff. We can use a heap to get better complexity, maybe median of medians quickselect to make it linear.

class Solution:
    def topStudents(self, positive_feedback: List[str], negative_feedback: List[str], report: List[str], student_id: List[int], k: int) -> List[int]:
        posSet = set(positive_feedback)
        negSet = set(negative_feedback)

        def getScore(report):
            return sum(
                3 if feedback in posSet else
                -1 if feedback in negSet else
                0
                for feedback in report.split(' ')
            )


        # map a student ID to their score
        scores = { student_id[i] : getScore(report[i]) for i in range(len(student_id)) }

        scoresArr = [(scores[studentId], studentId) for studentId in scores]
        scoresArr.sort(key=lambda tup: (-tup[0], tup[1])) # take an item and recreate it

        return [ scoresArr[i][1] for i in range(k) ]



