export interface Problem {
  id: number;
  name: string;
  difficulty: "easy" | "medium" | "hard";
}

export interface TopicNote {
  title: string;
  description: string;
}

export interface Topic {
  name: string;
  slug: string;
  problems: number;
  videos: number;
  difficulty: "beginner" | "intermediate" | "advanced";
  overviewTitle: string;
  overviewSubtitle: string;
  problemList: Problem[];
  notes: TopicNote[];
}

export interface FoundationLesson {
  slug: string;
  title: string;
  duration: string;
  subtitle: string;
  notes: TopicNote[];
}

export const topics: Topic[] = [
  {
    name: "Arrays & Hashing",
    slug: "arrays-hashing",
    problems: 24,
    videos: 6,
    difficulty: "beginner",
    overviewTitle: "When to use arrays & hashing",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 1, name: "Two Sum", difficulty: "easy" },
      { id: 217, name: "Contains Duplicate", difficulty: "easy" },
      { id: 242, name: "Valid Anagram", difficulty: "easy" },
      { id: 49, name: "Group Anagrams", difficulty: "medium" },
      { id: 347, name: "Top K Frequent Elements", difficulty: "medium" },
    ],
    notes: [
      {
        title: "Hash maps trade space for time",
        description:
          "Almost every array problem that asks for O(n) time uses a hash map. The question is: what are you storing, and what are you looking up?",
      },
      {
        title: "Sorting is your other best friend",
        description:
          "If the problem doesn't require preserving order, sorting first can simplify everything. Many two-pointer problems start with a sort.",
      },
      {
        title: "Think about what you need to remember",
        description:
          "The key insight for most array problems: as you iterate, what information from previous elements do you need? That's what goes in your hash map.",
      },
    ],
  },
  {
    name: "Two Pointers",
    slug: "two-pointers",
    problems: 18,
    videos: 4,
    difficulty: "beginner",
    overviewTitle: "When to use two pointers",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 125, name: "Valid Palindrome", difficulty: "easy" },
      { id: 167, name: "Two Sum II", difficulty: "medium" },
      { id: 15, name: "3Sum", difficulty: "medium" },
      { id: 11, name: "Container With Most Water", difficulty: "medium" },
    ],
    notes: [
      {
        title: "Two pointers work on sorted or structured data",
        description:
          "If the input is sorted (or you can sort it), two pointers can often replace a hash map approach with O(1) space.",
      },
      {
        title: "Move the pointer that improves your answer",
        description:
          "The core decision: which pointer do you move? Usually you move the one that gets you closer to the target.",
      },
    ],
  },
  {
    name: "Sliding Window",
    slug: "sliding-window",
    problems: 15,
    videos: 3,
    difficulty: "beginner",
    overviewTitle: "When to use sliding window",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 121, name: "Best Time to Buy and Sell Stock", difficulty: "easy" },
      { id: 3, name: "Longest Substring Without Repeating Characters", difficulty: "medium" },
      { id: 424, name: "Longest Repeating Character Replacement", difficulty: "medium" },
      { id: 76, name: "Minimum Window Substring", difficulty: "hard" },
    ],
    notes: [
      {
        title: "Fixed vs. variable window",
        description:
          "Know the difference: fixed-size windows slide both ends together. Variable windows expand the right end and shrink the left when a condition breaks.",
      },
      {
        title: "What enters and what leaves",
        description:
          "The key to every sliding window problem: when you expand, what do you add? When you shrink, what do you remove? Get this right and the rest follows.",
      },
    ],
  },
  {
    name: "Binary Search",
    slug: "binary-search",
    problems: 20,
    videos: 5,
    difficulty: "beginner",
    overviewTitle: "When to use binary search",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 704, name: "Binary Search", difficulty: "easy" },
      { id: 35, name: "Search Insert Position", difficulty: "easy" },
      { id: 367, name: "Valid Perfect Square", difficulty: "easy" },
      { id: 74, name: "Search a 2D Matrix", difficulty: "medium" },
      { id: 875, name: "Koko Eating Bananas", difficulty: "medium" },
      { id: 33, name: "Search in Rotated Sorted Array", difficulty: "medium" },
      { id: 981, name: "Time Based Key-Value Store", difficulty: "medium" },
      { id: 4, name: "Median of Two Sorted Arrays", difficulty: "hard" },
      { id: 410, name: "Split Array Largest Sum", difficulty: "hard" },
    ],
    notes: [
      {
        title: "It's about eliminating half the search space",
        description:
          "Sorted array is the textbook case, but the real condition is: can you define a monotonic predicate over the space? If something goes from false to true (or true to false), you can binary search on it.",
      },
      {
        title: "Search on the answer",
        description:
          "\"What's the minimum speed?\" \"What's the largest sum?\" — when the answer itself is what you're searching for, and you can verify a candidate in O(n), binary search the answer space.",
      },
      {
        title: "The implementation is always the same",
        description:
          "lo, hi, while lo < hi, check mid. The only thing that changes problem to problem is what your predicate is. Get the template locked in, then all your energy goes into figuring out the condition.",
      },
    ],
  },
  {
    name: "Stack",
    slug: "stack",
    problems: 16,
    videos: 3,
    difficulty: "intermediate",
    overviewTitle: "When to use a stack",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 20, name: "Valid Parentheses", difficulty: "easy" },
      { id: 155, name: "Min Stack", difficulty: "medium" },
      { id: 150, name: "Evaluate Reverse Polish Notation", difficulty: "medium" },
      { id: 84, name: "Largest Rectangle in Histogram", difficulty: "hard" },
    ],
    notes: [
      {
        title: "Stacks are for matching and nesting",
        description:
          "Parentheses, HTML tags, nested structures — anything where you need to match an opener with its closer.",
      },
      {
        title: "Monotonic stacks solve 'next greater' problems",
        description:
          "If you need to find the next greater or smaller element for each position, a monotonic stack does it in O(n).",
      },
    ],
  },
  {
    name: "Linked Lists",
    slug: "linked-lists",
    problems: 22,
    videos: 4,
    difficulty: "intermediate",
    overviewTitle: "When to use linked list techniques",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 206, name: "Reverse Linked List", difficulty: "easy" },
      { id: 21, name: "Merge Two Sorted Lists", difficulty: "easy" },
      { id: 143, name: "Reorder List", difficulty: "medium" },
      { id: 23, name: "Merge k Sorted Lists", difficulty: "hard" },
    ],
    notes: [
      {
        title: "Draw it out",
        description:
          "Linked list problems are pointer manipulation. Draw the nodes and arrows before you code. Track which pointers change and in what order.",
      },
      {
        title: "Fast and slow pointers",
        description:
          "Cycle detection, finding the middle, detecting intersections — fast/slow pointer is the core technique.",
      },
    ],
  },
  {
    name: "Trees",
    slug: "trees",
    problems: 30,
    videos: 6,
    difficulty: "intermediate",
    overviewTitle: "When to use tree techniques",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 226, name: "Invert Binary Tree", difficulty: "easy" },
      { id: 104, name: "Maximum Depth of Binary Tree", difficulty: "easy" },
      { id: 235, name: "Lowest Common Ancestor of a BST", difficulty: "medium" },
      { id: 230, name: "Kth Smallest Element in a BST", difficulty: "medium" },
      { id: 124, name: "Binary Tree Maximum Path Sum", difficulty: "hard" },
    ],
    notes: [
      {
        title: "DFS vs BFS — know when to use each",
        description:
          "DFS (recursive) for path problems, BST properties, and most tree questions. BFS for level-order problems.",
      },
      {
        title: "What information flows up vs. down",
        description:
          "The key recursive insight: does the parent need info from children (bottom-up), or do children need info from the parent (top-down)?",
      },
    ],
  },
  {
    name: "Graphs",
    slug: "graphs",
    problems: 28,
    videos: 5,
    difficulty: "advanced",
    overviewTitle: "When to use graph techniques",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 200, name: "Number of Islands", difficulty: "medium" },
      { id: 133, name: "Clone Graph", difficulty: "medium" },
      { id: 207, name: "Course Schedule", difficulty: "medium" },
      { id: 269, name: "Alien Dictionary", difficulty: "hard" },
    ],
    notes: [
      {
        title: "Model the problem as a graph first",
        description:
          "The hardest part of graph problems is recognizing it's a graph. What are the nodes? What are the edges? Once you see it, the algorithm is often standard.",
      },
      {
        title: "BFS for shortest path, DFS for connectivity",
        description:
          "Unweighted shortest path = BFS. Connected components, cycle detection, topological sort = DFS.",
      },
    ],
  },
  {
    name: "Dynamic Programming",
    slug: "dynamic-programming",
    problems: 35,
    videos: 7,
    difficulty: "advanced",
    overviewTitle: "When to use dynamic programming",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 70, name: "Climbing Stairs", difficulty: "easy" },
      { id: 198, name: "House Robber", difficulty: "medium" },
      { id: 322, name: "Coin Change", difficulty: "medium" },
      { id: 300, name: "Longest Increasing Subsequence", difficulty: "medium" },
      { id: 312, name: "Burst Balloons", difficulty: "hard" },
    ],
    notes: [
      {
        title: "Start with the recurrence",
        description:
          "Don't think about the table first. Think: if I knew the answer to smaller subproblems, how would I combine them? That's your recurrence relation.",
      },
      {
        title: "Overlapping subproblems are the signal",
        description:
          "If your brute-force recursion solves the same subproblem multiple times, that's DP. Memoize it or build the table bottom-up.",
      },
    ],
  },
  {
    name: "Greedy",
    slug: "greedy",
    problems: 22,
    videos: 4,
    difficulty: "intermediate",
    overviewTitle: "When to use greedy algorithms",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 53, name: "Maximum Subarray", difficulty: "medium" },
      { id: 55, name: "Jump Game", difficulty: "medium" },
      { id: 134, name: "Gas Station", difficulty: "medium" },
    ],
    notes: [
      {
        title: "Greedy = locally optimal leads to globally optimal",
        description:
          "The hard part is proving it works. If you can argue that making the best local choice never hurts the global solution, greedy is correct.",
      },
      {
        title: "Sort first, then be greedy",
        description:
          "Many greedy problems become obvious after sorting. Interval scheduling, activity selection, meeting rooms — sort by start or end time, then iterate.",
      },
    ],
  },
  {
    name: "Backtracking",
    slug: "backtracking",
    problems: 14,
    videos: 3,
    difficulty: "advanced",
    overviewTitle: "When to use backtracking",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 78, name: "Subsets", difficulty: "medium" },
      { id: 46, name: "Permutations", difficulty: "medium" },
      { id: 39, name: "Combination Sum", difficulty: "medium" },
      { id: 51, name: "N-Queens", difficulty: "hard" },
    ],
    notes: [
      {
        title: "It's just DFS with undo",
        description:
          "Make a choice, recurse, undo the choice. That's the entire pattern. The art is figuring out what choices to make at each step.",
      },
      {
        title: "Prune early",
        description:
          "The difference between a slow backtracker and a fast one is pruning. If you can detect a dead end early, skip it.",
      },
    ],
  },
  {
    name: "Heaps & Priority Queues",
    slug: "heaps",
    problems: 18,
    videos: 3,
    difficulty: "intermediate",
    overviewTitle: "When to use heaps",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 703, name: "Kth Largest Element in a Stream", difficulty: "easy" },
      { id: 215, name: "Kth Largest Element in an Array", difficulty: "medium" },
      { id: 355, name: "Design Twitter", difficulty: "medium" },
      { id: 295, name: "Find Median from Data Stream", difficulty: "hard" },
    ],
    notes: [
      {
        title: "Heaps are for 'top K' and streaming problems",
        description:
          "Whenever you need the smallest or largest K elements, or need to maintain order as elements arrive, think heap.",
      },
      {
        title: "Min heap vs. max heap — pick the right one",
        description:
          "For the K largest elements, use a min heap of size K (counterintuitive but correct). The top of the heap is your threshold.",
      },
    ],
  },
  {
    name: "Queues",
    slug: "queues",
    problems: 12,
    videos: 2,
    difficulty: "intermediate",
    overviewTitle: "When to use queues",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 225, name: "Implement Stack using Queues", difficulty: "easy" },
      { id: 232, name: "Implement Queue using Stacks", difficulty: "easy" },
      { id: 622, name: "Design Circular Queue", difficulty: "medium" },
      { id: 239, name: "Sliding Window Maximum", difficulty: "hard" },
    ],
    notes: [
      {
        title: "FIFO is the core idea",
        description:
          "Queues process things in order. BFS uses a queue. Any problem where you need to process elements in the order they arrived is a queue problem.",
      },
      {
        title: "Monotonic deques are powerful",
        description:
          "A deque that maintains monotonic order lets you find the min or max in a sliding window in O(1) per element. This shows up more than you'd expect.",
      },
    ],
  },
  {
    name: "Strings",
    slug: "strings",
    problems: 20,
    videos: 4,
    difficulty: "intermediate",
    overviewTitle: "String algorithm techniques",
    overviewSubtitle:
      "Before you solve any problems — understand the framework.",
    problemList: [
      { id: 14, name: "Longest Common Prefix", difficulty: "easy" },
      { id: 5, name: "Longest Palindromic Substring", difficulty: "medium" },
      { id: 647, name: "Palindromic Substrings", difficulty: "medium" },
      { id: 10, name: "Regular Expression Matching", difficulty: "hard" },
    ],
    notes: [
      {
        title: "Most string problems are array problems in disguise",
        description:
          "Sliding window, two pointers, and hash maps all work on strings. The key difference is knowing when to use string-specific tricks like prefix matching or palindrome expansion.",
      },
      {
        title: "Know your palindrome techniques",
        description:
          "Expand-around-center for palindromic substrings. DP for palindrome partitioning. These come up constantly in interviews.",
      },
    ],
  },
];

export const gettingStartedLessons: FoundationLesson[] = [
  {
    slug: "intro-to-leetcode",
    title: "Introduction to the LeetCode website",
    duration: "8 min",
    subtitle:
      "A quick tour of LeetCode — how the site works, how to submit solutions, and how to use it effectively.",
    notes: [
      {
        title: "The editor and test cases",
        description:
          "Learn how to use the built-in editor, run test cases, and understand what the expected output means before you submit.",
      },
      {
        title: "Problem difficulty ratings",
        description:
          "Easy, Medium, and Hard don't always reflect actual difficulty. Some Mediums are harder than Hards. Don't get hung up on the label.",
      },
    ],
  },
  {
    slug: "understanding-goals",
    title: "Understanding your goals",
    duration: "10 min",
    subtitle:
      "Are you prepping for interviews, learning CS fundamentals, or competing? Your goal changes how you should practice.",
    notes: [
      {
        title: "Interview prep vs. learning vs. competing",
        description:
          "Interview prep is about covering patterns efficiently. Learning is about depth. Competing is about speed. Know which mode you're in.",
      },
      {
        title: "Set a realistic timeline",
        description:
          "If your interview is in 4 weeks, you need a different plan than if you have 6 months. Be honest about where you're starting from.",
      },
    ],
  },
  {
    slug: "what-language-to-use",
    title: "What language to use",
    duration: "6 min",
    subtitle:
      "Python, Java, C++? It matters less than you think, but here's how to decide.",
    notes: [
      {
        title: "Use what you're comfortable with",
        description:
          "The best language is the one you can write fastest in. Don't learn a new language just for LeetCode unless you have months to spare.",
      },
      {
        title: "Python is the easiest for interviews",
        description:
          "Less boilerplate, built-in data structures, and cleaner syntax. If you don't have a strong preference, Python is the pragmatic choice.",
      },
    ],
  },
  {
    slug: "should-i-get-leetcode-premium",
    title: "Should I get LeetCode Premium?",
    duration: "5 min",
    subtitle:
      "Is it worth paying for? Here's an honest take on what you get and whether you actually need it.",
    notes: [
      {
        title: "What Premium gives you",
        description:
          "Access to company-tagged problems, premium-only questions, faster judge, and autocomplete. The company tags are the most useful feature by far.",
      },
      {
        title: "You don't need it to get good",
        description:
          "Every pattern and technique you need to learn is available on free problems. Premium is a nice-to-have, not a must-have.",
      },
    ],
  },
  {
    slug: "the-leetgoat-approach",
    title: "The LeetGoat approach",
    duration: "12 min",
    subtitle:
      "How I think about problem solving — first principles, not memorization. This is the philosophy behind everything on this site.",
    notes: [
      {
        title: "Understand, don't memorize",
        description:
          "If you can't explain why a solution works, you haven't learned it. Memorizing solutions is a trap — you'll fail the moment the problem changes slightly.",
      },
      {
        title: "Patterns are tools, not answers",
        description:
          "Learning 'this is a sliding window problem' is step one. Knowing why sliding window works here and how to adapt it is what actually matters.",
      },
      {
        title: "Struggle is part of the process",
        description:
          "If every problem feels easy, you're not learning. If every problem feels impossible, you're in the wrong difficulty. Find the edge of your ability and stay there.",
      },
    ],
  },
];

export const complexityLessons: FoundationLesson[] = [
  {
    slug: "what-is-big-o",
    title: "What is Big O?",
    duration: "10 min",
    subtitle:
      "Time complexity is the single most important concept in algorithm design. Here's what it actually means and why it matters.",
    notes: [
      {
        title: "Big O describes how your algorithm scales",
        description:
          "It's not about how fast your code runs on your machine. It's about how the number of operations grows as the input gets bigger. O(n) means linear growth, O(n²) means quadratic.",
      },
      {
        title: "Drop the constants, keep the dominant term",
        description:
          "O(2n) is just O(n). O(n² + n) is just O(n²). You only care about what dominates as n gets very large.",
      },
    ],
  },
  {
    slug: "space-complexity",
    title: "Space complexity",
    duration: "8 min",
    subtitle:
      "Time gets all the attention, but space complexity matters too — especially in interviews.",
    notes: [
      {
        title: "Count the extra memory you allocate",
        description:
          "Input doesn't count. What matters is the additional data structures you create: hash maps, arrays, recursion stack frames.",
      },
      {
        title: "Recursion uses stack space",
        description:
          "Every recursive call adds a frame to the call stack. A DFS on a tree of depth d uses O(d) space even if you don't create any data structures.",
      },
    ],
  },
  {
    slug: "reading-constraints",
    title: "Reading constraints",
    duration: "12 min",
    subtitle:
      "The constraints section of every LeetCode problem tells you exactly what time complexity you need. Learn to read it.",
    notes: [
      {
        title: "The 10⁷ rule",
        description:
          "A modern computer does roughly 10⁷–10⁸ simple operations per second within a typical time limit. If n = 10⁵, you need O(n log n) or better. If n = 10³, O(n²) is fine.",
      },
      {
        title: "Constraints → complexity → algorithm",
        description:
          "n ≤ 20 → brute force / backtracking. n ≤ 10³ → O(n²). n ≤ 10⁵ → O(n log n). n ≤ 10⁶ → O(n). This mapping narrows your approach before you write a single line.",
      },
    ],
  },
  {
    slug: "choosing-your-approach",
    title: "Using complexity to choose your approach",
    duration: "10 min",
    subtitle:
      "Before you code anything, the constraints tell you which algorithms are even possible. This is the most underrated skill in competitive programming.",
    notes: [
      {
        title: "Eliminate impossible approaches first",
        description:
          "If n = 10⁵ and your approach is O(n²), don't even try it. This saves you from wasting 30 minutes on a solution that will TLE.",
      },
      {
        title: "Multiple valid complexities = choose the simplest to implement",
        description:
          "If both O(n log n) and O(n) work for the given constraints, and the O(n log n) solution is simpler, go with that. Don't over-optimize in interviews.",
      },
    ],
  },
];
