"""
Additional Interview Questions Database
Provides diverse questions for coding, behavioral, and system design interviews
"""

ADDITIONAL_QUESTIONS = [
    # Coding Questions - Arrays/Algorithms
    {
        "id": "c18",
        "type": "coding",
        "category": "Arrays / Algorithms",
        "difficulty": "easy",
        "question": "Write a function find_max(arr) that returns the maximum value in an array of integers.",
        "solution_code": """def find_max(arr):
    if not arr:
        return None
    max_val = arr[0]
    for num in arr[1:]:
        if num > max_val:
            max_val = num
    return max_val""",
        "solution_explanation": "Iterate through array keeping track of maximum value. O(n) time, O(1) space.",
        "reference_points": ["Handle empty array", "Single pass", "Track maximum", "O(n) time"],
        "test_cases": [
            {"input": ([1, 5, 3, 9, 2],), "expected": 9},
            {"input": ([-1, -5, -3],), "expected": -1},
            {"input": ([],), "expected": None},
        ],
        "role": ["frontend", "backend", "fullstack"],
        "skill_tags": ["arrays", "algorithms", "basics"],
        "tech_stack": ["python", "javascript", "java"]
    },
    {
        "id": "c19",
        "type": "coding",
        "category": "Arrays / Algorithms",
        "difficulty": "medium",
        "question": "Implement binary_search(arr, target) that returns the index of target in sorted array, or -1 if not found.",
        "solution_code": """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1""",
        "solution_explanation": "Use divide and conquer approach. O(log n) time, O(1) space.",
        "reference_points": ["Divide and conquer", "Sorted array requirement", "O(log n) time", "Edge cases"],
        "test_cases": [
            {"input": ([1, 3, 5, 7, 9], 5), "expected": 2},
            {"input": ([1, 2, 3, 4, 5], 6), "expected": -1},
            {"input": ([], 1), "expected": -1},
        ],
        "role": ["backend", "fullstack"],
        "skill_tags": ["algorithms", "searching", "efficiency"],
        "tech_stack": ["python", "javascript", "java"]
    },
    
    # Coding Questions - Strings
    {
        "id": "c20",
        "type": "coding",
        "category": "Strings",
        "difficulty": "easy",
        "question": "Write a function count_vowels(s) that returns the number of vowels in a string.",
        "solution_code": """def count_vowels(s):
    vowels = set('aeiouAEIOU')
    return sum(1 for char in s if char in vowels)""",
        "solution_explanation": "Iterate through string and count characters that are vowels. O(n) time.",
        "reference_points": ["Set for O(1) lookup", "Case insensitive", "Single pass"],
        "test_cases": [
            {"input": ("hello world",), "expected": 3},
            {"input": ("bcdfg",), "expected": 0},
            {"input": ("",), "expected": 0},
        ],
        "role": ["frontend", "backend"],
        "skill_tags": ["strings", "basics", "iteration"],
        "tech_stack": ["python", "javascript", "java"]
    },
    {
        "id": "c21",
        "type": "coding",
        "category": "Strings",
        "difficulty": "medium",
        "question": "Implement reverse_words(s) that reverses the order of words in a sentence.",
        "solution_code": """def reverse_words(s):
    words = s.split()
    return ' '.join(reversed(words))""",
        "solution_explanation": "Split string into words, reverse the list, then join back. O(n) time.",
        "reference_points": ["String splitting", "List reversal", "Edge cases with spaces"],
        "test_cases": [
            {"input": ("hello world",), "expected": "world hello"},
            {"input": ("  multiple   spaces  ",), "expected": "spaces multiple"},
            {"input": ("",), "expected": ""},
        ],
        "role": ["frontend", "backend"],
        "skill_tags": ["strings", "manipulation", "arrays"],
        "tech_stack": ["python", "javascript", "java"]
    },

    # Coding Questions - Data Structures
    {
        "id": "c22",
        "type": "coding",
        "category": "Data Structures",
        "difficulty": "medium",
        "question": "Implement a Stack class with push, pop, and peek methods using a list.",
        "solution_code": """class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None
    
    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None
    
    def is_empty(self):
        return len(self.items) == 0""",
        "solution_explanation": "Use list's append and pop for LIFO behavior. All operations O(1) except pop from empty.",
        "reference_points": ["LIFO principle", "O(1) operations", "Empty stack handling"],
        "test_cases": [
            {"input": ("push 1, push 2, pop",), "expected": 2},
            {"input": ("push 1, peek",), "expected": 1},
            {"input": ("pop from empty",), "expected": None},
        ],
        "role": ["backend", "fullstack"],
        "skill_tags": ["data structures", "stack", "OOP"],
        "tech_stack": ["python", "javascript", "java"]
    },
    
    # Behavioral Questions
    {
        "id": "b1",
        "type": "behavioral",
        "category": "Teamwork",
        "difficulty": "medium",
        "question": "Tell me about a time you had a conflict with a team member. How did you resolve it?",
        "reference_answer": "Focus on communication, understanding different perspectives, finding common ground, and reaching a mutually beneficial solution.",
        "reference_points": ["Communication skills", "Conflict resolution", "Professionalism", "Collaboration"],
        "role": ["frontend", "backend", "fullstack", "senior"],
        "skill_tags": ["communication", "teamwork", "conflict-resolution"],
        "tech_stack": []
    },
    {
        "id": "b2",
        "type": "behavioral",
        "category": "Problem Solving",
        "difficulty": "medium",
        "question": "Describe a complex technical problem you solved recently. What was your approach?",
        "reference_answer": "Explain the problem clearly, describe your systematic approach, mention collaboration if any, and highlight the outcome.",
        "reference_points": ["Problem analysis", "Systematic approach", "Technical depth", "Results focus"],
        "role": ["frontend", "backend", "fullstack", "senior"],
        "skill_tags": ["problem-solving", "technical-skills", "analytical-thinking"],
        "tech_stack": []
    },
    {
        "id": "b3",
        "type": "behavioral",
        "category": "Learning",
        "difficulty": "easy",
        "question": "How do you stay updated with the latest technologies and best practices?",
        "reference_answer": "Mention specific resources like blogs, courses, conferences, open source contributions, and continuous learning habits.",
        "reference_points": ["Continuous learning", "Industry awareness", "Self-motivation", "Knowledge sharing"],
        "role": ["frontend", "backend", "fullstack"],
        "skill_tags": ["learning", "self-improvement", "industry-trends"],
        "tech_stack": []
    },
    
    # System Design Questions
    {
        "id": "s1",
        "type": "system_design",
        "category": "Scalability",
        "difficulty": "hard",
        "question": "Design a URL shortening service like TinyURL. How would you handle scalability?",
        "reference_answer": "Discuss database design, hash generation, caching, load balancing, and handling billions of URLs.",
        "reference_points": ["Database design", "Hash generation", "Caching strategy", "Load balancing", "API design"],
        "role": ["backend", "fullstack", "senior"],
        "skill_tags": ["system-design", "scalability", "databases", "architecture"],
        "tech_stack": ["redis", "mysql", "nginx", "kubernetes"]
    },
    {
        "id": "s2",
        "type": "system_design",
        "category": "Performance",
        "difficulty": "hard",
        "question": "Design a real-time chat application. What components would you need?",
        "reference_answer": "Cover WebSocket connections, message queues, database design, scaling, and offline handling.",
        "reference_points": ["WebSocket", "Message queuing", "Database design", "Real-time sync", "Offline support"],
        "role": ["backend", "fullstack", "senior"],
        "skill_tags": ["system-design", "real-time", "websockets", "messaging"],
        "tech_stack": ["socket.io", "redis", "mongodb", "kafka"]
    },
    
    # More Coding Questions
    {
        "id": "c23",
        "type": "coding",
        "category": "Trees",
        "difficulty": "medium",
        "question": "Implement a function to find the maximum depth of a binary tree.",
        "solution_code": """class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))""",
        "solution_explanation": "Use recursion to calculate depth. Base case: empty tree has depth 0. O(n) time.",
        "reference_points": ["Recursive approach", "Base case handling", "Tree traversal", "O(n) time"],
        "test_cases": [
            {"input": ("tree with 3 nodes",), "expected": 2},
            {"input": ("empty tree",), "expected": 0},
            {"input": ("single node",), "expected": 1},
        ],
        "role": ["backend", "fullstack"],
        "skill_tags": ["trees", "recursion", "algorithms"],
        "tech_stack": ["python", "javascript", "java"]
    },
    {
        "id": "c24",
        "type": "coding",
        "category": "Dynamic Programming",
        "difficulty": "hard",
        "question": "Write a function to solve the Fibonacci sequence using dynamic programming.",
        "solution_code": """def fibonacci(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[0], dp[1] = 0, 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]""",
        "solution_explanation": "Use bottom-up DP to avoid recursion overhead. O(n) time, O(n) space.",
        "reference_points": ["Dynamic programming", "Bottom-up approach", "Space optimization", "Time complexity"],
        "test_cases": [
            {"input": (0,), "expected": 0},
            {"input": (1,), "expected": 1},
            {"input": (10,), "expected": 55},
        ],
        "role": ["backend", "fullstack", "senior"],
        "skill_tags": ["dynamic-programming", "algorithms", "optimization"],
        "tech_stack": ["python", "javascript", "java"]
    },

    # --- NEW QUESTIONS START HERE ---

    # Frontend - React & DOM
    {
        "id": "fe1",
        "type": "coding",
        "category": "Frontend",
        "difficulty": "medium",
        "question": "Create a custom React hook `useDebounce` that delays updating a value until a specified time has passed.",
        "solution_code": """import { useState, useEffect } from 'react';

function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}""",
        "solution_explanation": "Use useEffect to set a timer that updates state. Cleanup function clears the timer if value changes before delay.",
        "reference_points": ["useEffect cleanup", "setTimeout usage", "State management", "Hook structure"],
        "test_cases": [],
        "role": ["frontend", "fullstack"],
        "skill_tags": ["react", "hooks", "javascript"],
        "tech_stack": ["react", "javascript"]
    },
    {
        "id": "fe2",
        "type": "coding",
        "category": "Frontend",
        "difficulty": "easy",
        "question": "Explain the difference between `localStorage`, `sessionStorage`, and `cookies`.",
        "solution_code": """// Explanatory code not required for concept check, but typical usage:
localStorage.setItem('key', 'val'); // Persists forever
sessionStorage.setItem('key', 'val'); // Persists for session
document.cookie = 'key=val'; // Server interaction""",
        "solution_explanation": "localStorage: no expiry. sessionStorage: clears when tab closes. Cookies: sent with requests, have expiry.",
        "reference_points": ["Persistence duration", "Server transmission", "Storage capacity", "Access scope"],
        "test_cases": [],
        "role": ["frontend", "fullstack"],
        "skill_tags": ["browser-api", "storage", "web-basics"],
        "tech_stack": ["javascript", "html"]
    },
    {
        "id": "fe3",
        "type": "coding",
        "category": "Frontend",
        "difficulty": "medium",
        "question": "Implement a function `flatten(arr)` that flattens a nested array of arbitrary depth.",
        "solution_code": """def flatten(arr):
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result""",
        "solution_explanation": "Recursively check if item is list. If so, flatten it; else append. JS equivalent uses Array.flat(Infinity) or recursion.",
        "reference_points": ["Recursion", "Type checking", "Accumulation", "Edge cases (empty)"],
        "test_cases": [
            {"input": ([1, [2, [3, 4], 5]],), "expected": [1, 2, 3, 4, 5]},
            {"input": ([],), "expected": []}
        ],
        "role": ["frontend", "backend", "fullstack"],
        "skill_tags": ["algorithms", "recursion", "arrays"],
        "tech_stack": ["javascript", "python"]
    },

    # Backend - API & DB
    {
        "id": "be1",
        "type": "system_design",
        "category": "API Design",
        "difficulty": "medium",
        "question": "Design a RESTful API for a Todo application. List endpoints, methods, and status codes.",
        "reference_answer": "GET /todos (200), POST /todos (201), GET /todos/:id (200), PUT /todos/:id (200), DELETE /todos/:id (204). Error handling 404, 400, 500.",
        "reference_points": ["Resource naming", "HTTP verbs", "Status codes", "Payload structure"],
        "role": ["backend", "fullstack"],
        "skill_tags": ["rest", "api-design", "web-standards"],
        "tech_stack": []
    },
    {
        "id": "be2",
        "type": "coding",
        "category": "Database",
        "difficulty": "medium",
        "question": "Write a SQL query to find the second highest salary from an Employee table.",
        "solution_code": """SELECT MAX(Salary) FROM Employee
WHERE Salary < (SELECT MAX(Salary) FROM Employee);
-- Or using LIMIT/OFFSET
SELECT Salary FROM Employee ORDER BY Salary DESC LIMIT 1 OFFSET 1;""",
        "solution_explanation": "Subquery finds max first, then find max less than that. Or simply order descending and skip first.",
        "reference_points": ["Subquery usage", "ORDER BY logic", "LIMIT/OFFSET", "Handling duplicates"],
        "test_cases": [],
        "role": ["backend", "data-engineer", "fullstack"],
        "skill_tags": ["sql", "database", "queries"],
        "tech_stack": ["sql", "mysql", "postgres"]
    },
    {
        "id": "be3",
        "type": "coding",
        "category": "Concurrency",
        "difficulty": "hard",
        "question": "Explain the difference between Process and Thread. When would you use Multiprocessing vs Multithreading in Python?",
        "solution_code": """# Conceptual Answer
# Process: Independent memory space, heavier. Good for CPU-bound (bypass GIL).
# Thread: Shared memory, lighter. Good for I/O-bound.""",
        "solution_explanation": "Processes don't share memory (safe), Threads do (race conditions). Python GIL limits threads on CPU tasks.",
        "reference_points": ["Memory isolation", "Context switching overhead", "GIL (Python specific)", "I/O vs CPU bound"],
        "test_cases": [],
        "role": ["backend", "python-dev"],
        "skill_tags": ["os-concepts", "python", "concurrency"],
        "tech_stack": ["python", "java", "cpp"]
    },

    # Behavioral - Leadership & Soft Skills
    {
        "id": "b4",
        "type": "behavioral",
        "category": "Leadership",
        "difficulty": "medium",
        "question": "Describe a time you had to lead a project or initiative without formal authority.",
        "reference_answer": "Focused on building consensus, demonstrating value, organizing tasks, and supporting team members to achieve the goal.",
        "reference_points": ["Influence without authority", "Initiative", "Organization", "Team support"],
        "role": ["senior", "lead", "all"],
        "skill_tags": ["leadership", "soft-skills", "initiative"],
        "tech_stack": []
    },
    {
        "id": "b5",
        "type": "behavioral",
        "category": "Failure",
        "difficulty": "medium",
        "question": "Tell me about a time you failed to meet a deadline. How did you handle it?",
        "reference_answer": "Communicated early, renegotiated scope or timeline, worked extra if needed, and implemented process changes to prevent recurrence.",
        "reference_points": ["Early communication", "Ownership", "Recovery plan", "Lessons learned"],
        "role": ["all"],
        "skill_tags": ["responsibility", "communication", "resilience"],
        "tech_stack": []
    },
    {
        "id": "b6",
        "type": "behavioral",
        "category": "Adaptability",
        "difficulty": "easy",
        "question": "Describe a situation where requirements changed last minute. How did you react?",
        "reference_answer": "Assessed impact, communicated risks, prioritized critical features, and maintained a positive attitude to deliver.",
        "reference_points": ["Flexibility", "Impact assessment", "Communication", "Professionalism"],
        "role": ["all"],
        "skill_tags": ["adaptability", "agile", "pressure-handling"],
        "tech_stack": []
    },

    # System Design - Practical
    {
        "id": "sd3",
        "type": "system_design",
        "category": "Architecture",
        "difficulty": "hard",
        "question": "Design a Rate Limiter system. Where would you place it and what algorithms would you use?",
        "reference_answer": "Placement: API Gateway/Middleware. Algos: Token Bucket, Leaky Bucket. Storage: Redis (fast counters). Handling: 429 Too Many Requests.",
        "reference_points": ["Placement (Gateway)", "Algorithms (Token Bucket)", "Distributed store (Redis)", "Return codes"],
        "role": ["backend", "senior", "devops"],
        "skill_tags": ["system-design", "scalability", "algorithms"],
        "tech_stack": ["redis", "nginx"]
    },
    {
        "id": "sd4",
        "type": "system_design",
        "category": "Reliability",
        "difficulty": "medium",
        "question": "How would you design a system to handle high traffic spikes for a ticket booking website?",
        "reference_answer": "Queue-based processing (waiting room), auto-scaling, caching static content, database read replicas, optimistic locking for inventory.",
        "reference_points": ["Queuing/Waiting room", "Caching", "Database locking", "Auto-scaling"],
        "role": ["backend", "senior"],
        "skill_tags": ["system-design", "high-availability", "concurrency"],
        "tech_stack": ["aws", "kafka", "redis"]
    },

    # More Coding - Data Structures
    {
        "id": "c25",
        "type": "coding",
        "category": "Linked Lists",
        "difficulty": "medium",
        "question": "Implement a function to detect a cycle in a linked list.",
        "solution_code": """def has_cycle(head):
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False""",
        "solution_explanation": "Floyd's Cycle-Finding Algorithm (Tortoise and Hare). Two pointers moving at different speeds meet if there is a cycle.",
        "reference_points": ["Two pointer technique", "O(n) time", "O(1) space", "Null checks"],
        "test_cases": [],
        "role": ["backend", "fullstack"],
        "skill_tags": ["linked-list", "algorithms", "pointers"],
        "tech_stack": ["python", "java", "c++"]
    },
    {
        "id": "c26",
        "type": "coding",
        "category": "Arrays",
        "difficulty": "easy",
        "question": "Given an array of integers, move all zeros to the end while maintaining the relative order of non-zero elements.",
        "solution_code": """def move_zeroes(nums):
    pos = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[pos], nums[i] = nums[i], nums[pos]
            pos += 1
    return nums""",
        "solution_explanation": "Maintain a pointer for position of next non-zero. Swap non-zero elements forward. O(n) time, O(1) space.",
        "reference_points": ["In-place modification", "Two pointers", "Order preservation", "Edge cases"],
        "test_cases": [
            {"input": ([0,1,0,3,12],), "expected": [1,3,12,0,0]},
            {"input": ([0,0,1],), "expected": [1,0,0]}
        ],
        "role": ["frontend", "backend", "fullstack"],
        "skill_tags": ["arrays", "manipulation", "basics"],
        "tech_stack": ["python", "javascript"]
    },
    {
        "id": "c27",
        "type": "coding",
        "category": "Strings",
        "difficulty": "medium",
        "question": "Longest Substring Without Repeating Characters: Find the length of the longest substring without repeating characters.",
        "solution_code": """def length_of_longest_substring(s):
    char_map = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in char_map and char_map[char] >= left:
            left = char_map[char] + 1
        char_map[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len""",
        "solution_explanation": "Sliding window approach optimized with a hash map to store last index of each char. O(n) time.",
        "reference_points": ["Sliding window", "Hash map", "O(n) time", "Index handling"],
        "test_cases": [
            {"input": ("abcabcbb",), "expected": 3},
            {"input": ("bbbbb",), "expected": 1}
        ],
        "role": ["backend", "fullstack"],
        "skill_tags": ["strings", "sliding-window", "algorithms"],
        "tech_stack": ["python", "javascript"]
    },
    {
        "id": "c28",
        "type": "coding",
        "category": "Recursion",
        "difficulty": "easy",
        "question": "Calculate the factorial of a number n.",
        "solution_code": """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)""",
        "solution_explanation": "Simple recursion: n! = n * (n-1)!. Base case: 0! = 1, 1! = 1.",
        "reference_points": ["Recursion", "Base case", "Overflow awareness (large n)"],
        "test_cases": [
            {"input": (5,), "expected": 120},
            {"input": (0,), "expected": 1}
        ],
        "role": ["all"],
        "skill_tags": ["recursion", "math", "basics"],
        "tech_stack": ["python"]
    },
    {
        "id": "c29",
        "type": "coding",
        "category": "Bit Manipulation",
        "difficulty": "medium",
        "question": "Single Number: Given a non-empty array of integers, every element appears twice except for one. Find that single one.",
        "solution_code": """def single_number(nums):
    res = 0
    for num in nums:
        res ^= num
    return res""",
        "solution_explanation": "XOR operation: a ^ a = 0, a ^ 0 = a. XORing all numbers leaves the unique one. O(n) time, O(1) space.",
        "reference_points": ["XOR properties", "O(1) space constaint", "Linear time"],
        "test_cases": [
            {"input": ([4,1,2,1,2],), "expected": 4},
            {"input": ([2,2,1],), "expected": 1}
        ],
        "role": ["backend", "embedded"],
        "skill_tags": ["bit-manipulation", "optimization", "logic"],
        "tech_stack": ["c", "cpp", "python"]
    },

    # DevOps & General
    {
        "id": "do1",
        "type": "coding",
        "category": "DevOps",
        "difficulty": "medium",
        "question": "What is the difference between Docker COPY and ADD instructions?",
        "solution_code": """# Dockerfile
# COPY: Copies local files to container (Preferred)
# ADD: Can also extract tarballs and fetch URLs (Use only if needed)""",
        "solution_explanation": "COPY is explicit for local files. ADD has magic behavior like extraction and remote fetch.",
        "reference_points": ["Explicit vs Implicit", "Tarball extraction", "Remote URL capability", "Best practices"],
        "test_cases": [],
        "role": ["devops", "backend"],
        "skill_tags": ["docker", "containers", "devops"],
        "tech_stack": ["docker"]
    },
    {
        "id": "do2",
        "type": "coding",
        "category": "DevOps",
        "difficulty": "medium",
        "question": "Explain CI/CD. What are the benefits?",
        "solution_code": """# CI: Continuous Integration (Merge often, Auto test)
# CD: Continuous Delivery/Deployment (Auto release)""",
        "solution_explanation": "CI: frequent merges, automated tests. CD: automated deployment pipeline. Benefits: speed, reliability, less manual error.",
        "reference_points": ["Automation", "Testing", "Deployment pipeline", "Feedback loop"],
        "test_cases": [],
        "role": ["devops", "lead"],
        "skill_tags": ["ci-cd", "automation", "process"],
        "tech_stack": ["jenkins", "github-actions"]
    },
    {
        "id": "g1",
        "type": "coding",
        "category": "General",
        "difficulty": "easy",
        "question": "What is HTTP? Explain the request-response cycle.",
        "solution_code": """# Client -> Request (Headers, Body) -> Server
# Server -> Process -> Response (Status, Body) -> Client""",
        "solution_explanation": "HyperText Transfer Protocol. Stateless. Client sends request, Server sends response. TCP/IP underlying.",
        "reference_points": ["Client-Server model", "Statelessness", "Headers/Body", "Status codes"],
        "test_cases": [],
        "role": ["all"],
        "skill_tags": ["http", "web-basics", "networking"],
        "tech_stack": []
    },
    
    # --- EXPANDED QUESTION BANK (Python, Java, C, C++) ---

    # PYTHON QUESTIONS
    {
        "id": "py1", "type": "coding", "category": "Python", "difficulty": "medium",
        "question": "Explain Python's Global Interpreter Lock (GIL). How does it affect threading?",
        "solution_code": "# GIL is a mutex that allows only one thread to hold control of the Python interpreter.",
        "solution_explanation": "Prevents multiple native threads from executing Python bytecodes at once. Limits CPU-bound concurrency but safe for I/O.",
        "reference_points": ["Mutex", "CPU-bound vs I/O-bound", "One thread per process"],
        "role": ["backend", "data-engineer"], "skill_tags": ["python", "concurrency"], "tech_stack": ["python"]
    },
    {
        "id": "py2", "type": "coding", "category": "Python", "difficulty": "easy",
        "question": "What are Python decorators? Write a simple example.",
        "solution_code": "def my_decorator(func):\n    def wrapper():\n        print('Before')\n        func()\n        print('After')\n    return wrapper",
        "solution_explanation": "Decorators are functions that modify the behavior of other functions. Syntactic sugar @decorator.",
        "reference_points": ["Higher-order function", "Wrapper", "@ syntax"],
        "role": ["backend", "fullstack"], "skill_tags": ["python", "decorators"], "tech_stack": ["python"]
    },
    {
        "id": "py3", "type": "coding", "category": "Python", "difficulty": "medium",
        "question": "Difference between `__str__` and `__repr__` in Python?",
        "solution_code": "# __str__: Readable string for end-users (print).\n# __repr__: Unambiguous string for developers (debugging).",
        "solution_explanation": "__str__ is for display, __repr__ is for debugging/development aiming to be unambiguous.",
        "reference_points": ["Readability vs Unambiguity", "print() uses str", "repr() uses repr"],
        "role": ["backend"], "skill_tags": ["python", "oop"], "tech_stack": ["python"]
    },
    {
        "id": "py4", "type": "coding", "category": "Python", "difficulty": "easy",
        "question": "What is the difference between a list and a tuple?",
        "solution_code": "l = [1, 2] # Mutable\nt = (1, 2) # Immutable",
        "solution_explanation": "Lists are mutable (can change), tuples are immutable (cannot change). Tuples are faster and hashable.",
        "reference_points": ["Mutability", "Syntax [] vs ()", "Performance"],
        "role": ["all"], "skill_tags": ["python", "basics"], "tech_stack": ["python"]
    },
    {
        "id": "py5", "type": "coding", "category": "Python", "difficulty": "medium",
        "question": "Explain list comprehensions with an example.",
        "solution_code": "squares = [x**2 for x in range(10) if x % 2 == 0]",
        "solution_explanation": "Concise way to create lists. More readable and often faster than loops.",
        "reference_points": ["Syntax", "Performance", "Readability"],
        "role": ["backend", "data-science"], "skill_tags": ["python", "basics"], "tech_stack": ["python"]
    },
    {
        "id": "py6", "type": "coding", "category": "Python", "difficulty": "hard",
        "question": "What are generators and the `yield` keyword?",
        "solution_code": "def count_up_to(n):\n    i = 0\n    while i < n:\n        yield i\n        i += 1",
        "solution_explanation": "Generators return an iterator that produces a sequence of values one at a time. Memory efficient.",
        "reference_points": ["Lazy evaluation", "Memory efficiency", "Iterator protocol"],
        "role": ["backend", "data-engineer"], "skill_tags": ["python", "generators"], "tech_stack": ["python"]
    },
    {
        "id": "py7", "type": "coding", "category": "Python", "difficulty": "medium",
        "question": "How is memory managed in Python?",
        "solution_code": "# Reference counting and Garbage Collection (cyclic GC).",
        "solution_explanation": "Python uses private heap space. Memory manager handles allocation. GC handles cyclic references.",
        "reference_points": ["Reference counting", "Garbage collection", "Private heap"],
        "role": ["backend", "senior"], "skill_tags": ["python", "memory"], "tech_stack": ["python"]
    },
    {
        "id": "py8", "type": "coding", "category": "Python", "difficulty": "medium",
        "question": "What is the difference between `is` and `==`?",
        "solution_code": "# 'is' checks identity (memory address).\n# '==' checks equality (value).",
        "solution_explanation": "`is` returns True if variables point to the same object. `==` checks if values are equivalent.",
        "reference_points": ["Identity vs Equality", "Memory address", "Singleton check (None)"],
        "role": ["all"], "skill_tags": ["python", "basics"], "tech_stack": ["python"]
    },
    {
        "id": "py9", "type": "coding", "category": "Python", "difficulty": "medium",
        "question": "Explain context managers and the `with` statement.",
        "solution_code": "with open('file.txt') as f:\n    data = f.read()\n# Auto-closes file",
        "solution_explanation": "Simplifies exception handling and resource management. Ensures cleanup (exit method) is called.",
        "reference_points": ["Resource management", "__enter__ and __exit__", "Exception safety"],
        "role": ["backend"], "skill_tags": ["python", "basics"], "tech_stack": ["python"]
    },
    {
        "id": "py10", "type": "coding", "category": "Python", "difficulty": "hard",
        "question": "What are metaclasses in Python?",
        "solution_code": "class Meta(type):\n    def __new__(cls, name, bases, dct):\n        return super().__new__(cls, name, bases, dct)",
        "solution_explanation": "Classes of classes. They define how a class behaves. Used for API enforcement, registries, etc.",
        "reference_points": ["Class creation", "type()", "__new__ vs __init__"],
        "role": ["senior", "architect"], "skill_tags": ["python", "metaprogramming"], "tech_stack": ["python"]
    },

    # JAVA QUESTIONS
    {
        "id": "java1", "type": "coding", "category": "Java", "difficulty": "medium",
        "question": "Difference between JDK, JRE, and JVM?",
        "solution_code": "# JDK: Dev tools (javac) + JRE.\n# JRE: Libraries + JVM.\n# JVM: Runtime environment.",
        "solution_explanation": "JDK for development, JRE for running, JVM executes bytecode.",
        "reference_points": ["Development vs Runtime", "Bytecode execution", "Components"],
        "role": ["backend", "java-dev"], "skill_tags": ["java", "basics"], "tech_stack": ["java"]
    },
    {
        "id": "java2", "type": "coding", "category": "Java", "difficulty": "medium",
        "question": "Explain the difference between an Interface and an Abstract Class.",
        "solution_code": "# Interface: Multiple inheritance support, public methods (mostly).\n# Abstract Class: Shared state/constructor, single inheritance.",
        "solution_explanation": "Interfaces define contract (can implement multiple). Abstract classes provide base implementation (single extend).",
        "reference_points": ["Multiple inheritance", "Constructor", "State"],
        "role": ["backend"], "skill_tags": ["java", "oop"], "tech_stack": ["java"]
    },
    {
        "id": "java3", "type": "coding", "category": "Java", "difficulty": "hard",
        "question": "How does Garbage Collection work in Java?",
        "solution_code": "# Mark and Sweep algorithm. Generational GC (Young, Old, Perm/Metaspace).",
        "solution_explanation": "Identifies unreachable objects and reclaims memory. Objects move from Eden -> Survivor -> Old Gen.",
        "reference_points": ["Mark and Sweep", "Generations", "Stop-the-world"],
        "role": ["backend", "senior"], "skill_tags": ["java", "memory"], "tech_stack": ["java"]
    },
    {
        "id": "java4", "type": "coding", "category": "Java", "difficulty": "medium",
        "question": "What is the contract between `hashCode()` and `equals()`?",
        "solution_code": "# If equals() is true, hashCode() MUST be same.\n# If hashCode() same, equals() MIGHT be true (collision).",
        "solution_explanation": "Critical for HashMap performance. Violating this breaks hash-based collections.",
        "reference_points": ["Map consistency", "Collision handling", "Reflexive/Symmetric/Transitive"],
        "role": ["backend"], "skill_tags": ["java", "basics"], "tech_stack": ["java"]
    },
    {
        "id": "java5", "type": "coding", "category": "Java", "difficulty": "medium",
        "question": "What are Java Streams? Give an example.",
        "solution_code": "list.stream().filter(s -> s.startsWith(\"a\")).map(String::toUpperCase).collect(Collectors.toList());",
        "solution_explanation": "Functional-style operations on streams of elements. Lazy evaluation, parallel capable.",
        "reference_points": ["Functional programming", "Intermediate vs Terminal ops", "Lazy evaluation"],
        "role": ["backend", "fullstack"], "skill_tags": ["java", "streams"], "tech_stack": ["java"]
    },
    {
        "id": "java6", "type": "coding", "category": "Java", "difficulty": "easy",
        "question": "Difference between `final`, `finally`, and `finalize`.",
        "solution_code": "# final: Constant/Immutable.\n# finally: Block in try-catch.\n# finalize: GC cleanup method (deprecated).",
        "solution_explanation": "Keywords with distinct purposes. final=modifier, finally=flow control, finalize=lifecycle.",
        "reference_points": ["Keywords distinction", "Usage context"],
        "role": ["all"], "skill_tags": ["java", "basics"], "tech_stack": ["java"]
    },
    {
        "id": "java7", "type": "coding", "category": "Java", "difficulty": "medium",
        "question": "What is the difference between Checked and Unchecked Exceptions?",
        "solution_code": "# Checked: Compile-time (IOException). Must catch/declare.\n# Unchecked: Runtime (NullPointer). Optional handling.",
        "solution_explanation": "Checked exceptions force error handling. Unchecked represent programming errors.",
        "reference_points": ["Compile-time vs Runtime", "try-catch mandatory", "RuntimeException"],
        "role": ["backend"], "skill_tags": ["java", "exceptions"], "tech_stack": ["java"]
    },
    {
        "id": "java8", "type": "coding", "category": "Java", "difficulty": "medium",
        "question": "Explain Singleton pattern in Java. Is it thread-safe?",
        "solution_code": "public class Singleton { private static Singleton instance; private Singleton(){} ... }",
        "solution_explanation": "Ensures only one instance exists. Thread safety requires synchronization or Enum implementation.",
        "reference_points": ["Design pattern", "Double-checked locking", "Enum Singleton"],
        "role": ["backend", "architect"], "skill_tags": ["java", "design-patterns"], "tech_stack": ["java"]
    },
    {
        "id": "java9", "type": "coding", "category": "Java", "difficulty": "medium",
        "question": "What is the `volatile` keyword?",
        "solution_code": "# Indicates variable value modified by different threads.",
        "solution_explanation": "Prevents caching of variable thread-locally. Reads/writes go directly to main memory. Guarantees visibility.",
        "reference_points": ["Memory visibility", "Thread safety", "Not atomic"],
        "role": ["backend", "concurrency"], "skill_tags": ["java", "multithreading"], "tech_stack": ["java"]
    },
    {
        "id": "java10", "type": "coding", "category": "Java", "difficulty": "hard",
        "question": "How does HashMap work internally?",
        "solution_code": "# Array of buckets (Linked Lists / Red-Black Trees). Key hash determines index.",
        "solution_explanation": "Uses hashCode() for bucket index. equals() for key collision. Java 8+ uses Trees for large buckets.",
        "reference_points": ["Buckets", "Collision resolution", "Time complexity O(1) -> O(log n)"],
        "role": ["senior", "backend"], "skill_tags": ["java", "collections"], "tech_stack": ["java"]
    },

    # C QUESTIONS
    {
        "id": "c1", "type": "coding", "category": "C", "difficulty": "medium",
        "question": "What is the difference between `malloc` and `calloc`?",
        "solution_code": "// malloc: allocates uninitialized memory.\n// calloc: allocates zero-initialized memory.",
        "solution_explanation": "malloc takes size. calloc takes count and size, and clears memory to zero.",
        "reference_points": ["Initialization", "Parameters", "Zeroing memory"],
        "role": ["embedded", "backend"], "skill_tags": ["c", "memory"], "tech_stack": ["c"]
    },
    {
        "id": "c2", "type": "coding", "category": "C", "difficulty": "medium",
        "question": "Explain the use of `static` keyword in C.",
        "solution_code": "// 1. Inside function: Retains value between calls.\n// 2. Global/Function: Limits scope to translation unit (file).",
        "solution_explanation": "Controls storage duration (local static) and linkage/visibility (global static).",
        "reference_points": ["Storage duration", "Scope/Linkage", "Encapsulation"],
        "role": ["embedded", "systems"], "skill_tags": ["c", "basics"], "tech_stack": ["c"]
    },
    {
        "id": "c3", "type": "coding", "category": "C", "difficulty": "hard",
        "question": "What is a segmentation fault?",
        "solution_code": "// Accessing memory the program doesn't own (e.g., dereferencing NULL, out of bounds).",
        "solution_explanation": "Hardware memory protection fault. Often caused by bad pointers.",
        "reference_points": ["Memory access violation", "Pointers", "Debugging"],
        "role": ["embedded", "systems"], "skill_tags": ["c", "debugging"], "tech_stack": ["c"]
    },
    {
        "id": "c4", "type": "coding", "category": "C", "difficulty": "medium",
        "question": "What are function pointers? Give an example.",
        "solution_code": "void (*fun_ptr)(int) = &my_fun;\nfun_ptr(10);",
        "solution_explanation": "Variables that store the address of a function. Used for callbacks and dynamic dispatch.",
        "reference_points": ["Callbacks", "Pointer syntax", "Dynamic behavior"],
        "role": ["embedded", "systems"], "skill_tags": ["c", "pointers"], "tech_stack": ["c"]
    },
    {
        "id": "c5", "type": "coding", "category": "C", "difficulty": "easy",
        "question": "Difference between structure and union.",
        "solution_code": "// Struct: Allocates memory for ALL members.\n// Union: Allocates memory for LARGEST member (shared).",
        "solution_explanation": "Struct members coexist. Union members overlap (save memory, mutually exclusive).",
        "reference_points": ["Memory allocation", "Shared memory", "Use cases"],
        "role": ["embedded"], "skill_tags": ["c", "structs"], "tech_stack": ["c"]
    },
    {
        "id": "c6", "type": "coding", "category": "C", "difficulty": "medium",
        "question": "What is the purpose of the `volatile` keyword in C?",
        "solution_code": "// Tells compiler variable may change unexpectedly (e.g., hardware register, ISR).",
        "solution_explanation": "Prevents compiler optimizations like caching value in register. Essential for embedded systems.",
        "reference_points": ["Optimization prevention", "Hardware registers", "Interrupts"],
        "role": ["embedded"], "skill_tags": ["c", "embedded"], "tech_stack": ["c"]
    },
    {
        "id": "c7", "type": "coding", "category": "C", "difficulty": "medium",
        "question": "Explain strict aliasing rule.",
        "solution_code": "// Pointers of different types cannot point to same memory (except char*).",
        "solution_explanation": "Allows compiler to assume different pointers don't overlap. Violating it leads to undefined behavior.",
        "reference_points": ["Undefined behavior", "Optimization", "Type punning"],
        "role": ["systems", "senior"], "skill_tags": ["c", "optimization"], "tech_stack": ["c"]
    },
    {
        "id": "c8", "type": "coding", "category": "C", "difficulty": "easy",
        "question": "What is a preprocessor macro?",
        "solution_code": "#define MAX(a,b) ((a) > (b) ? (a) : (b))",
        "solution_explanation": "Text substitution before compilation. Code replacement, not function call.",
        "reference_points": ["Text substitution", "Compile phases", "Side effects (multiple evaluation)"],
        "role": ["embedded", "systems"], "skill_tags": ["c", "preprocessor"], "tech_stack": ["c"]
    },
    {
        "id": "c9", "type": "coding", "category": "C", "difficulty": "medium",
        "question": "Difference between pass by value and pass by reference (using pointers).",
        "solution_code": "// Value: Copy of data.\n// Reference: Address of data (allows modification).",
        "solution_explanation": "C uses pass-by-value strictly. 'Pass by reference' is simulated using pointers.",
        "reference_points": ["Copy overhead", "Modifiability", "Pointer semantic"],
        "role": ["all"], "skill_tags": ["c", "basics"], "tech_stack": ["c"]
    },
    {
        "id": "c10", "type": "coding", "category": "C", "difficulty": "hard",
        "question": "How do you implement a memory leak detector in C?",
        "solution_code": "// Wrap malloc/free. Track allocations in a list/table. Report unfreed blocks at exit.",
        "solution_explanation": "Instrumentation of allocation functions. Requires tracking file/line number.",
        "reference_points": ["Instrumentation", "Tracking allocations", "Wrapper functions"],
        "role": ["systems", "senior"], "skill_tags": ["c", "memory", "debugging"], "tech_stack": ["c"]
    },

    # C++ QUESTIONS
    {
        "id": "cpp1", "type": "coding", "category": "C++", "difficulty": "medium",
        "question": "What are the key features of Object Oriented Programming in C++?",
        "solution_code": "// Encapsulation, Inheritance, Polymorphism, Abstraction.",
        "solution_explanation": "Core OOP pillars allow modular, reusable, and maintainable code.",
        "reference_points": ["OOP pillars", "Classes", "Virtual functions"],
        "role": ["backend", "cpp-dev"], "skill_tags": ["cpp", "oop"], "tech_stack": ["c++"]
    },
    {
        "id": "cpp2", "type": "coding", "category": "C++", "difficulty": "medium",
        "question": "Explain `virtual` functions and polymorphism.",
        "solution_code": "virtual void draw() { ... } // Derived class can override",
        "solution_explanation": "Enables runtime polymorphism (late binding). Object behaves as its actual type, not pointer type.",
        "reference_points": ["Vtable", "Runtime polymorphism", "Overriding"],
        "role": ["backend", "systems"], "skill_tags": ["cpp", "oop"], "tech_stack": ["c++"]
    },
    {
        "id": "cpp3", "type": "coding", "category": "C++", "difficulty": "hard",
        "question": "What is RAII (Resource Acquisition Is Initialization)?",
        "solution_code": "// Resource held is tied to object lifetime.\n// Constructor acquires, Destructor releases.",
        "solution_explanation": "Fundamental C++ idiom for leak-free resource management (memory, files, locks).",
        "reference_points": ["Resource management", "Destructors", "Exception safety"],
        "role": ["senior", "systems"], "skill_tags": ["cpp", "memory"], "tech_stack": ["c++"]
    },
    {
        "id": "cpp4", "type": "coding", "category": "C++", "difficulty": "medium",
        "question": "Difference between `std::vector` and `std::list`?",
        "solution_code": "// Vector: Dynamic array, contiguous memory, O(1) access.\n// List: Doubly linked list, O(1) insert/delete anywhere.",
        "solution_explanation": "Vector for cache locality and random access. List for frequent insertions/deletions.",
        "reference_points": ["Contiguous memory", "Cache locality", "Big O complexity"],
        "role": ["all"], "skill_tags": ["cpp", "stl"], "tech_stack": ["c++"]
    },
    {
        "id": "cpp5", "type": "coding", "category": "C++", "difficulty": "medium",
        "question": "What are Smart Pointers? (unique_ptr, shared_ptr)",
        "solution_code": "// unique_ptr: Exclusive ownership.\n// shared_ptr: Shared ownership (ref counted).",
        "solution_explanation": "Automate memory management using RAII. prevents leaks and dangling pointers.",
        "reference_points": ["Ownership semantics", "Reference counting", "No manual delete"],
        "role": ["modern-cpp", "backend"], "skill_tags": ["cpp", "memory"], "tech_stack": ["c++"]
    },
    {
        "id": "cpp6", "type": "coding", "category": "C++", "difficulty": "hard",
        "question": "Explain Move Semantics and r-value references (&&).",
        "solution_code": "A(A&& other) { data = other.data; other.data = nullptr; }",
        "solution_explanation": "Performance optimization. Transfers resources from temporary objects instead of copying.",
        "reference_points": ["Performance", "Copy vs Move", "std::move"],
        "role": ["senior", "optimization"], "skill_tags": ["cpp", "modern-cpp"], "tech_stack": ["c++"]
    },
    {
        "id": "cpp7", "type": "coding", "category": "C++", "difficulty": "medium",
        "question": "What is the Diamond Problem in inheritance? How to solve it?",
        "solution_code": "class B : virtual public A { ... };",
        "solution_explanation": "Ambiguity when two base classes inherit from same parent. Solved using 'virtual inheritance'.",
        "reference_points": ["Multiple inheritance", "Virtual base class", "Ambiguity"],
        "role": ["backend", "systems"], "skill_tags": ["cpp", "inheritance"], "tech_stack": ["c++"]
    },
    {
        "id": "cpp8", "type": "coding", "category": "C++", "difficulty": "easy",
        "question": "Difference between `struct` and `class` in C++.",
        "solution_code": "// Struct: Members public by default.\n// Class: Members private by default.",
        "solution_explanation": "Functionally identical otherwise. Convention: struct for POD, class for objects with invariants.",
        "reference_points": ["Access modifiers", "Default visibility"],
        "role": ["all"], "skill_tags": ["cpp", "basics"], "tech_stack": ["c++"]
    },
    {
        "id": "cpp9", "type": "coding", "category": "C++", "difficulty": "hard",
        "question": "What are Templates in C++?",
        "solution_code": "template <typename T> T add(T a, T b) { return a + b; }",
        "solution_explanation": "Generic programming. Compiler generates code for each type used. Compile-time polymorphism.",
        "reference_points": ["Generics", "Compile-time", "Code bloat"],
        "role": ["senior", "library-dev"], "skill_tags": ["cpp", "templates"], "tech_stack": ["c++"]
    },
    {
        "id": "cpp10", "type": "coding", "category": "C++", "difficulty": "medium",
        "question": "What is `const` correctness?",
        "solution_code": "void print(const MyClass& param) const { ... }",
        "solution_explanation": "Using const to prevent accidental modification properly. Applies to variables, pointers, and methods.",
        "reference_points": ["Read-only", "API design", "Compiler enforcement"],
        "role": ["all"], "skill_tags": ["cpp", "best-practices"], "tech_stack": ["c++"]
    }
    ]

def get_additional_questions():
    """Return all additional questions to extend the main question bank."""
    return ADDITIONAL_QUESTIONS
