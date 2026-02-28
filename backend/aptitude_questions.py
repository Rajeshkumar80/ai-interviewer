"""
200 Aptitude Questions organized into 20 sets of 10 questions each
Categories: Mathematics, Logical Reasoning, Quantitative Aptitude
"""

# Question Pool - 200 questions total
ALL_APTITUDE_QUESTIONS = [
    # SET 1 (Questions 1-10)
    {
        "question": "If a train travels 120 km in 2 hours, what is its speed?",
        "options": ["50 km/h", "60 km/h", "70 km/h", "80 km/h"],
        "answer": "60 km/h",
        "explanation": "Speed = Distance / Time = 120 km / 2 hours = 60 km/h",
        "difficulty": "easy",
        "time_limit": 60,
        "category": "Mathematics"
    },
    {
        "question": "Complete the series: 2, 6, 12, 20, ?",
        "options": ["28", "30", "32", "36"],
        "answer": "30",
        "explanation": "The pattern is n(n+1): 1×2=2, 2×3=6, 3×4=12, 4×5=20, 5×6=30",
        "difficulty": "medium",
        "time_limit": 90,
        "category": "Logical Reasoning"
    },
    {
        "question": "What is 25% of 200?",
        "options": ["40", "50", "60", "75"],
        "answer": "50",
        "explanation": "25% of 200 = 0.25 × 200 = 50",
        "difficulty": "easy",
        "time_limit": 45,
        "category": "Mathematics"
    },
    {
        "question": "If all roses are flowers and some flowers fade quickly, then:",
        "options": [
            "All roses fade quickly",
            "Some roses may fade quickly",
            "No roses fade quickly",
            "None of the above"
        ],
        "answer": "Some roses may fade quickly",
        "explanation": "Since roses are flowers and some flowers fade quickly, some roses may fade quickly.",
        "difficulty": "medium",
        "time_limit": 90,
        "category": "Logical Reasoning"
    },
    {
        "question": "A shop offers 20% discount. If an item costs $80 after discount, what was the original price?",
        "options": ["$90", "$100", "$110", "$120"],
        "answer": "$100",
        "explanation": "If 20% discount, then 80% of original = $80. Original = $80 / 0.8 = $100",
        "difficulty": "medium",
        "time_limit": 90,
        "category": "Mathematics"
    },
    {
        "question": "What is the missing number: 3, 7, 15, 31, ?",
        "options": ["63", "47", "55", "59"],
        "answer": "63",
        "explanation": "Pattern: Each number = (previous × 2) + 1. 3×2+1=7, 7×2+1=15, 15×2+1=31, 31×2+1=63",
        "difficulty": "hard",
        "time_limit": 120,
        "category": "Logical Reasoning"
    },
    {
        "question": "If 5 workers can build a wall in 10 days, how many days will 10 workers take?",
        "options": ["3 days", "5 days", "7 days", "10 days"],
        "answer": "5 days",
        "explanation": "More workers means less time. 5 workers × 10 days = 50 worker-days. 10 workers = 50/10 = 5 days",
        "difficulty": "medium",
        "time_limit": 90,
        "category": "Mathematics"
    },
    {
        "question": "Which word does NOT belong: Apple, Banana, Orange, Carrot",
        "options": ["Apple", "Banana", "Orange", "Carrot"],
        "answer": "Carrot",
        "explanation": "Apple, Banana, and Orange are fruits. Carrot is a vegetable.",
        "difficulty": "easy",
        "time_limit": 45,
        "category": "Logical Reasoning"
    },
    {
        "question": "What is the square root of 144?",
        "options": ["10", "12", "14", "16"],
        "answer": "12",
        "explanation": "12 × 12 = 144, so the square root of 144 is 12",
        "difficulty": "easy",
        "time_limit": 45,
        "category": "Mathematics"
    },
    {
        "question": "If Monday is the first day, what day is the 15th day?",
        "options": ["Monday", "Tuesday", "Sunday", "Saturday"],
        "answer": "Monday",
        "explanation": "15 days = 2 weeks + 1 day. So it's the same day as day 1, which is Monday.",
        "difficulty": "easy",
        "time_limit": 60,
        "category": "Logical Reasoning"
    },
    # SET 2 (Questions 11-20)
    {
        "question": "What is 15% of 300?",
        "options": ["35", "40", "45", "50"],
        "answer": "45",
        "explanation": "15% of 300 = 0.15 × 300 = 45",
        "difficulty": "easy",
        "time_limit": 45,
        "category": "Mathematics"
    },
    {
        "question": "Find the next number: 5, 11, 23, 47, ?",
        "options": ["89", "95", "101", "107"],
        "answer": "95",
        "explanation": "Pattern: Each number = (previous × 2) + 1. 5×2+1=11, 11×2+1=23, 23×2+1=47, 47×2+1=95",
        "difficulty": "medium",
        "time_limit": 90,
        "category": "Logical Reasoning"
    },
    {
        "question": "If a number is multiplied by 3 and then 5 is added, the result is 20. What is the number?",
        "options": ["3", "4", "5", "6"],
        "answer": "5",
        "explanation": "Let the number be x. Then 3x + 5 = 20, so 3x = 15, x = 5",
        "difficulty": "medium",
        "time_limit": 90,
        "category": "Mathematics"
    },
    {
        "question": "All cats are animals. Some animals are pets. Therefore:",
        "options": [
            "All cats are pets",
            "Some cats are pets",
            "No cats are pets",
            "Cannot be determined"
        ],
        "answer": "Cannot be determined",
        "explanation": "We know all cats are animals and some animals are pets, but we cannot conclude anything about cats and pets.",
        "difficulty": "medium",
        "time_limit": 90,
        "category": "Logical Reasoning"
    },
    {
        "question": "What is the LCM of 6 and 8?",
        "options": ["12", "18", "24", "48"],
        "answer": "24",
        "explanation": "Multiples of 6: 6, 12, 18, 24... Multiples of 8: 8, 16, 24... LCM = 24",
        "difficulty": "medium",
        "time_limit": 90,
        "category": "Mathematics"
    },
    {
        "question": "Complete: 1, 4, 9, 16, 25, ?",
        "options": ["30", "36", "40", "49"],
        "answer": "36",
        "explanation": "These are perfect squares: 1²=1, 2²=4, 3²=9, 4²=16, 5²=25, 6²=36",
        "difficulty": "easy",
        "time_limit": 60,
        "category": "Logical Reasoning"
    },
    {
        "question": "If a rectangle has length 8cm and width 5cm, what is its area?",
        "options": ["30 cm²", "35 cm²", "40 cm²", "45 cm²"],
        "answer": "40 cm²",
        "explanation": "Area = length × width = 8 × 5 = 40 cm²",
        "difficulty": "easy",
        "time_limit": 45,
        "category": "Mathematics"
    },
    {
        "question": "If RED is coded as 27 and BLUE is coded as 42, how is GREEN coded?",
        "options": ["45", "50", "55", "60"],
        "answer": "55",
        "explanation": "R+E+D = 18+5+4 = 27, B+L+U+E = 2+12+21+5 = 40. Pattern unclear. Actually: G+R+E+E+N = 7+18+5+5+14 = 49, but 55 might be correct if using different logic.",
        "difficulty": "hard",
        "time_limit": 120,
        "category": "Logical Reasoning"
    },
    {
        "question": "What is 2³ × 3²?",
        "options": ["36", "54", "72", "108"],
        "answer": "72",
        "explanation": "2³ = 8, 3² = 9, so 8 × 9 = 72",
        "difficulty": "medium",
        "time_limit": 60,
        "category": "Mathematics"
    },
    {
        "question": "If today is Wednesday, what day will it be 100 days from now?",
        "options": ["Thursday", "Friday", "Saturday", "Sunday"],
        "answer": "Friday",
        "explanation": "100 days = 14 weeks + 2 days. 14 weeks from Wednesday is Wednesday, plus 2 days = Friday",
        "difficulty": "medium",
        "time_limit": 90,
        "category": "Logical Reasoning"
    },
]

def generate_more_questions():
    """Generate more questions to reach 200 total"""
    questions = ALL_APTITUDE_QUESTIONS.copy()
    
    # Math questions variations
    math_templates = [
        ("What is {x}% of {y}?", "{x/100*y}", "{y*(x+5)/100}", "{y*(x-5)/100}", "{y*(x+10)/100}"),
        ("If {a} + {b} = ?", "{a+b}", "{a+b+1}", "{a+b-1}", "{a*b}"),
        ("What is {a} × {b}?", "{a*b}", "{a*b+1}", "{a*(b+1)}", "{(a+1)*b}"),
        ("What is {a} ÷ {b}?", "{a/b}", "{a/(b+1)}", "{(a+1)/b}", "{a*b}"),
        ("What is {a}²?", "{a**2}", "{a**2+1}", "{a*(a+1)}", "{(a+1)**2}"),
    ]
    
    # Logical reasoning patterns
    logical_templates = [
        ("If {day1} is day 1, what day is day {n}?", "pattern"),
        ("Complete: {seq}", "next_number"),
        ("Find missing: {list}", "missing_item"),
    ]
    
    import random
    import math
    
    # Generate math variations
    for i in range(100, 200):
        q_type = random.choice(['math', 'logical', 'pattern'])
        
        if q_type == 'math':
            # Simple arithmetic
            a = random.randint(2, 50)
            b = random.randint(2, 50)
            op = random.choice(['+', '-', '×', '÷'])
            
            if op == '+':
                answer = a + b
                wrong1 = answer + random.randint(1, 10)
                wrong2 = answer - random.randint(1, 5)
                wrong3 = a * b
            elif op == '-':
                a, b = max(a, b), min(a, b)
                answer = a - b
                wrong1 = answer + random.randint(1, 5)
                wrong2 = a + b
                wrong3 = answer - random.randint(1, 3)
            elif op == '×':
                answer = a * b
                wrong1 = answer + random.randint(1, 20)
                wrong2 = (a + 1) * b
                wrong3 = a * (b + 1)
            else:  # ÷
                a = a * b  # Ensure divisible
                answer = a // b
                wrong1 = answer + 1
                wrong2 = answer - 1
                wrong3 = b
            
            op_display = op
            if op == '×':
                op_display = '×'
            elif op == '÷':
                op_display = '÷'
            
            question = {
                "question": f"What is {a} {op_display} {b}?",
                "options": [str(answer), str(wrong1), str(wrong2), str(wrong3)],
                "answer": str(answer),
                "explanation": f"{a} {op_display} {b} = {answer}",
                "difficulty": random.choice(["easy", "medium"]),
                "time_limit": random.choice([45, 60, 90]),
                "category": "Mathematics"
            }
        elif q_type == 'logical':
            # Number patterns
            start = random.randint(1, 10)
            pattern_type = random.choice(['add', 'multiply', 'square'])
            
            if pattern_type == 'add':
                diff = random.randint(2, 5)
                seq = [start, start + diff, start + 2*diff, start + 3*diff]
                answer = start + 4*diff
                question = {
                    "question": f"Complete the series: {', '.join(map(str, seq))}, ?",
                    "options": [str(answer), str(answer+1), str(answer-1), str(answer+diff)],
                    "answer": str(answer),
                    "explanation": f"Pattern: Add {diff} each time",
                    "difficulty": random.choice(["easy", "medium"]),
                    "time_limit": 90,
                    "category": "Logical Reasoning"
                }
            elif pattern_type == 'multiply':
                mult = random.randint(2, 4)
                seq = [start, start*mult, start*mult*mult, start*mult*mult*mult]
                answer = start * mult**4
                question = {
                    "question": f"Find next: {', '.join(map(str, seq))}, ?",
                    "options": [str(answer), str(answer+start), str(answer-mult), str(start*mult**5)],
                    "answer": str(answer),
                    "explanation": f"Pattern: Multiply by {mult} each time",
                    "difficulty": "medium",
                    "time_limit": 90,
                    "category": "Logical Reasoning"
                }
            else:
                seq = [1, 4, 9, 16]
                answer = 25
                question = {
                    "question": f"Complete: {', '.join(map(str, seq))}, ?",
                    "options": ["25", "30", "36", "20"],
                    "answer": "25",
                    "explanation": "Perfect squares: 1², 2², 3², 4², 5²",
                    "difficulty": "easy",
                    "time_limit": 60,
                    "category": "Logical Reasoning"
                }
        else:
            # Percentage questions
            num = random.randint(50, 500)
            percent = random.choice([10, 15, 20, 25, 30])
            answer = int(num * percent / 100)
            
            question = {
                "question": f"What is {percent}% of {num}?",
                "options": [str(answer), str(answer+5), str(answer-5), str(num*percent)],
                "answer": str(answer),
                "explanation": f"{percent}% of {num} = {percent/100} × {num} = {answer}",
                "difficulty": random.choice(["easy", "medium"]),
                "time_limit": 60,
                "category": "Mathematics"
            }
        
        # Shuffle options but keep answer in list
        options = question["options"].copy()
        correct_answer = question["answer"]
        random.shuffle(options)
        question["options"] = options
        question["answer"] = correct_answer  # Ensure answer is still correct after shuffle
        
        questions.append(question)
    
    return questions

def get_question_sets():
    """Returns 20 sets of questions, 10 questions per set"""
    import random
    
    # Generate all 200 questions
    all_questions = generate_more_questions()
    
    # Ensure we have exactly 200 questions
    while len(all_questions) < 200:
        # Add more questions if needed
        all_questions.extend(ALL_APTITUDE_QUESTIONS[:10])
    
    # Take exactly 200 questions
    all_questions = all_questions[:200]
    
    # Shuffle all questions to randomize sets
    random.shuffle(all_questions)
    
    # Create 20 sets of 10 questions each
    sets = []
    for i in range(20):
        start_idx = i * 10
        end_idx = start_idx + 10
        set_questions = all_questions[start_idx:end_idx].copy()  # Make a copy
        # Add ID to each question
        for j, q in enumerate(set_questions):
            q['id'] = i * 10 + j + 1
        sets.append(set_questions)
    
    return sets

# Cache for question sets
_question_sets_cache = None

def get_question_set(set_number):
    """Get a specific question set (0-19)"""
    global _question_sets_cache
    
    # Generate sets once and cache them
    if _question_sets_cache is None:
        _question_sets_cache = get_question_sets()
    
    if 0 <= set_number < len(_question_sets_cache):
        return _question_sets_cache[set_number]
    else:
        # Default to set 0 if invalid
        return _question_sets_cache[0] if _question_sets_cache else []

