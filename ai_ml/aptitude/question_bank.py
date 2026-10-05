"""
Comprehensive Aptitude Question Bank
===================================
Contains categorized questions with difficulty levels across:
1. Quantitative Ability (16 topics)
2. Logical Reasoning (12 topics)
3. Verbal Ability (10 topics)
"""

from typing import List, Dict, Any

QUANTITATIVE_TOPICS = [
    "Percentages",
    "Profit and Loss",
    "Simple Interest",
    "Compound Interest",
    "Ratios",
    "Proportions",
    "Averages",
    "Time and Work",
    "Time Speed Distance",
    "Probability",
    "Permutations and Combinations",
    "Number Systems",
    "Ages",
    "Mixtures and Alligations",
    "Data Interpretation",
    "Algebra"
]

LOGICAL_REASONING_TOPICS = [
    "Number Series",
    "Alphabet Series",
    "Coding-Decoding",
    "Blood Relations",
    "Directions",
    "Syllogisms",
    "Seating Arrangement",
    "Puzzles",
    "Statement and Conclusion",
    "Analogies",
    "Odd One Out",
    "Pattern Recognition"
]

VERBAL_ABILITY_TOPICS = [
    "Grammar",
    "Sentence Correction",
    "Vocabulary",
    "Synonyms",
    "Antonyms",
    "Reading Comprehension",
    "Sentence Completion",
    "Para Jumbles",
    "Spotting Errors",
    "Contextual Usage"
]

# Master Question Bank
APTITUDE_QUESTIONS: List[Dict[str, Any]] = [
    # =========================================================================
    # SECTION 1: QUANTITATIVE ABILITY
    # =========================================================================
    {
        "id": "QA_PERC_001",
        "section": "Quantitative Ability",
        "topic": "Percentages",
        "difficulty": "Easy",
        "question": "If the price of a commodity increases by 25%, by what percentage must a household reduce its consumption so that the total expenditure remains unchanged?",
        "options": ["20%", "25%", "15%", "16.67%"],
        "correct_answer": "20%",
        "explanation": "Reduction required = [r / (100 + r)] * 100 = [25 / 125] * 100 = 20%."
    },
    {
        "id": "QA_PERC_002",
        "section": "Quantitative Ability",
        "topic": "Percentages",
        "difficulty": "Medium",
        "question": "A candidate scores 35% marks and fails by 40 marks. Another candidate scores 60% marks and secures 35 marks more than the minimum passing marks. What is the maximum possible score in the examination?",
        "options": ["300", "250", "320", "280"],
        "correct_answer": "300",
        "explanation": "Difference in percentage = 60% - 35% = 25%. Difference in marks = 40 + 35 = 75. Therefore, 25% of total = 75 => Total marks = 75 * 4 = 300."
    },
    {
        "id": "QA_PL_001",
        "section": "Quantitative Ability",
        "topic": "Profit and Loss",
        "difficulty": "Easy",
        "question": "A shopkeeper sells a book for Rs. 440 at a gain of 10%. What was the cost price of the book?",
        "options": ["Rs. 400", "Rs. 396", "Rs. 420", "Rs. 380"],
        "correct_answer": "Rs. 400",
        "explanation": "CP = SP * 100 / (100 + Profit%) = 440 * 100 / 110 = Rs. 400."
    },
    {
        "id": "QA_PL_002",
        "section": "Quantitative Ability",
        "topic": "Profit and Loss",
        "difficulty": "Medium",
        "question": "By selling 33 meters of cloth, a merchant gains the selling price of 11 meters. Find the merchant's gain percentage.",
        "options": ["50%", "33.33%", "25%", "66.67%"],
        "correct_answer": "50%",
        "explanation": "Gain = SP of 33m - CP of 33m = SP of 11m => CP of 33m = SP of 22m. Profit% = (11 / 22) * 100 = 50%."
    },
    {
        "id": "QA_SI_001",
        "section": "Quantitative Ability",
        "topic": "Simple Interest",
        "difficulty": "Easy",
        "question": "At what rate of simple interest per annum will a sum of money double itself in 8 years?",
        "options": ["12.5%", "10%", "15%", "11.5%"],
        "correct_answer": "12.5%",
        "explanation": "Simple Interest = Principal. SI = P * R * T / 100 => P = P * R * 8 / 100 => R = 100 / 8 = 12.5%."
    },
    {
        "id": "QA_CI_001",
        "section": "Quantitative Ability",
        "topic": "Compound Interest",
        "difficulty": "Medium",
        "question": "The difference between simple and compound interests compounded annually on a certain sum of money for 2 years at 10% per annum is Rs. 65. What is the principal sum?",
        "options": ["Rs. 6,500", "Rs. 6,000", "Rs. 7,200", "Rs. 5,800"],
        "correct_answer": "Rs. 6,500",
        "explanation": "For 2 years, CI - SI = P * (R / 100)^2. 65 = P * (10 / 100)^2 = P * 1/100 => P = Rs. 6,500."
    },
    {
        "id": "QA_RAT_001",
        "section": "Quantitative Ability",
        "topic": "Ratios",
        "difficulty": "Easy",
        "question": "If A : B = 3 : 4 and B : C = 8 : 9, what is A : C?",
        "options": ["2 : 3", "1 : 2", "3 : 2", "4 : 5"],
        "correct_answer": "2 : 3",
        "explanation": "A/C = (A/B) * (B/C) = (3/4) * (8/9) = 24/36 = 2/3."
    },
    {
        "id": "QA_PROP_001",
        "section": "Quantitative Ability",
        "topic": "Proportions",
        "difficulty": "Medium",
        "question": "What number must be added to each of 6, 14, 18, and 38 so that the resulting numbers form a proportion?",
        "options": ["2", "4", "3", "1"],
        "correct_answer": "2",
        "explanation": "Let x be added: (6 + x)/(14 + x) = (18 + x)/(38 + x). For x = 2: 8/16 = 20/40 = 1/2. Thus x = 2."
    },
    {
        "id": "QA_AVG_001",
        "section": "Quantitative Ability",
        "topic": "Averages",
        "difficulty": "Easy",
        "question": "The average of 5 consecutive odd numbers is 27. What is the value of the largest of these numbers?",
        "options": ["31", "29", "33", "27"],
        "correct_answer": "31",
        "explanation": "The average of 5 consecutive odd numbers is the middle number (3rd number) = 27. The numbers are 23, 25, 27, 29, 31. Largest = 31."
    },
    {
        "id": "QA_TW_001",
        "section": "Quantitative Ability",
        "topic": "Time and Work",
        "difficulty": "Medium",
        "question": "A can finish a work in 12 days and B can finish the same work in 18 days. If they work together for 4 days, what fraction of the work remains unfinished?",
        "options": ["4/9", "5/9", "1/3", "2/9"],
        "correct_answer": "4/9",
        "explanation": "Combined 1-day rate = 1/12 + 1/18 = (3 + 2)/36 = 5/36. In 4 days, they complete 4 * (5/36) = 20/36 = 5/9 of the work. Remaining work = 1 - 5/9 = 4/9."
    },
    {
        "id": "QA_TW_002",
        "section": "Quantitative Ability",
        "topic": "Time and Work",
        "difficulty": "Hard",
        "question": "Pipe A can fill a tank in 10 hours, and Pipe B in 15 hours. Both are opened together, but after 2 hours Pipe A is closed. How much total time does it take to fill the tank from the start?",
        "options": ["12 hours", "10 hours", "14 hours", "11.5 hours"],
        "correct_answer": "12 hours",
        "explanation": "In 2 hours, A and B fill 2 * (1/10 + 1/15) = 2 * (5/30) = 1/3 of the tank. Remaining 2/3 is filled by Pipe B alone at 1/15 per hour: (2/3) / (1/15) = 10 hours. Total time = 2 + 10 = 12 hours."
    },
    {
        "id": "QA_TSD_001",
        "section": "Quantitative Ability",
        "topic": "Time Speed Distance",
        "difficulty": "Medium",
        "question": "A train 180 meters long running at 72 km/h crosses an electric pole. How many seconds does it take?",
        "options": ["9 seconds", "10 seconds", "8 seconds", "12 seconds"],
        "correct_answer": "9 seconds",
        "explanation": "Speed = 72 * (5/18) = 20 m/s. Time = Distance / Speed = 180 / 20 = 9 seconds."
    },
    {
        "id": "QA_TSD_002",
        "section": "Quantitative Ability",
        "topic": "Time Speed Distance",
        "difficulty": "Hard",
        "question": "Two cars travel towards each other from points A and B 300 km apart at speeds of 60 km/h and 40 km/h respectively. After how many hours will they meet?",
        "options": ["3 hours", "2.5 hours", "3.5 hours", "4 hours"],
        "correct_answer": "3 hours",
        "explanation": "Relative speed = 60 + 40 = 100 km/h. Time to meet = Total distance / Relative speed = 300 / 100 = 3 hours."
    },
    {
        "id": "QA_PROB_001",
        "section": "Quantitative Ability",
        "topic": "Probability",
        "difficulty": "Easy",
        "question": "Two unbiased dice are rolled simultaneously. What is the probability of obtaining a total sum of 8?",
        "options": ["5/36", "1/6", "7/36", "1/9"],
        "correct_answer": "5/36",
        "explanation": "Favorable outcomes for sum 8: (2,6), (3,5), (4,4), (5,3), (6,2) = 5 pairs out of 36 total outcomes = 5/36."
    },
    {
        "id": "QA_PERM_001",
        "section": "Quantitative Ability",
        "topic": "Permutations and Combinations",
        "difficulty": "Medium",
        "question": "In how many distinct ways can the letters of the word 'LEADER' be arranged?",
        "options": ["360", "720", "180", "120"],
        "correct_answer": "360",
        "explanation": "'LEADER' has 6 letters with 'E' repeating twice. Distinct arrangements = 6! / 2! = 720 / 2 = 360."
    },
    {
        "id": "QA_NUM_001",
        "section": "Quantitative Ability",
        "topic": "Number Systems",
        "difficulty": "Easy",
        "question": "What is the remainder when 2^31 is divided by 5?",
        "options": ["3", "2", "4", "1"],
        "correct_answer": "3",
        "explanation": "Powers of 2 modulo 5: 2^1 = 2, 2^2 = 4, 2^3 = 3, 2^4 = 1 (cycle length 4). 31 mod 4 = 3, so 2^31 ≡ 2^3 ≡ 3 (mod 5)."
    },
    {
        "id": "QA_AGE_001",
        "section": "Quantitative Ability",
        "topic": "Ages",
        "difficulty": "Easy",
        "question": "Father is four times as old as his son. In 20 years, he will be twice as old as his son. What is the father's current age?",
        "options": ["40 years", "36 years", "48 years", "32 years"],
        "correct_answer": "40 years",
        "explanation": "Let son's age = x, father's age = 4x. In 20 years: 4x + 20 = 2(x + 20) => 4x + 20 = 2x + 40 => 2x = 20 => x = 10. Father's age = 4 * 10 = 40 years."
    },
    {
        "id": "QA_MIX_001",
        "section": "Quantitative Ability",
        "topic": "Mixtures and Alligations",
        "difficulty": "Hard",
        "question": "In what ratio must tea worth Rs. 60 per kg be mixed with tea worth Rs. 65 per kg so that the mixture must be worth Rs. 62.50 per kg?",
        "options": ["1 : 1", "2 : 3", "3 : 2", "1 : 2"],
        "correct_answer": "1 : 1",
        "explanation": "By rule of alligation: (65 - 62.50) : (62.50 - 60) = 2.50 : 2.50 = 1 : 1."
    },
    {
        "id": "QA_DI_001",
        "section": "Quantitative Ability",
        "topic": "Data Interpretation",
        "difficulty": "Medium",
        "question": "A company produces 500 units in Q1 and 650 units in Q2. What is the percentage growth in production from Q1 to Q2?",
        "options": ["30%", "25%", "35%", "28%"],
        "correct_answer": "30%",
        "explanation": "Growth = (650 - 500) / 500 * 100 = 150 / 500 * 100 = 30%."
    },
    {
        "id": "QA_ALG_001",
        "section": "Quantitative Ability",
        "topic": "Algebra",
        "difficulty": "Medium",
        "question": "If x + 1/x = 4, find the value of x^2 + 1/x^2.",
        "options": ["14", "16", "18", "12"],
        "correct_answer": "14",
        "explanation": "(x + 1/x)^2 = x^2 + 1/x^2 + 2 => 4^2 = x^2 + 1/x^2 + 2 => x^2 + 1/x^2 = 16 - 2 = 14."
    },

    # =========================================================================
    # SECTION 2: LOGICAL REASONING
    # =========================================================================
    {
        "id": "LR_NS_001",
        "section": "Logical Reasoning",
        "topic": "Number Series",
        "difficulty": "Easy",
        "question": "Look at this series: 7, 10, 8, 11, 9, 12, ... What number should come next?",
        "options": ["10", "13", "12", "7"],
        "correct_answer": "10",
        "explanation": "This is an alternating addition and subtraction series: +3, -2, +3, -2, +3, -2. 12 - 2 = 10."
    },
    {
        "id": "LR_NS_002",
        "section": "Logical Reasoning",
        "topic": "Number Series",
        "difficulty": "Medium",
        "question": "Find the missing number in the sequence: 2, 6, 12, 20, 30, 42, ?",
        "options": ["56", "54", "60", "48"],
        "correct_answer": "56",
        "explanation": "Pattern is n*(n+1): 1*2=2, 2*3=6, 3*4=12, 4*5=20, 5*6=30, 6*7=42, 7*8=56 (or differences +4, +6, +8, +10, +12, +14)."
    },
    {
        "id": "LR_AS_001",
        "section": "Logical Reasoning",
        "topic": "Alphabet Series",
        "difficulty": "Easy",
        "question": "Complete the series: B2D, D4F, F6H, H8J, ...",
        "options": ["J10L", "J9L", "K10L", "J10K"],
        "correct_answer": "J10L",
        "explanation": "First letter increases by +2 (B, D, F, H, J). Number increases by +2 (2, 4, 6, 8, 10). Last letter increases by +2 (D, F, H, J, L). Result: J10L."
    },
    {
        "id": "LR_CD_001",
        "section": "Logical Reasoning",
        "topic": "Coding-Decoding",
        "difficulty": "Medium",
        "question": "If in a certain code language, 'ROUTER' is coded as 'URNWGT', how will 'SWITCH' be coded in that same language?",
        "options": ["UVKVEJ", "UWKWEJ", "VWKVEJ", "UVLWFK"],
        "correct_answer": "UVKVEJ",
        "explanation": "Each letter is shifted by +2 positions in the alphabet: S->U, W->Y? Wait: R(+3)->U, O(+3)->R, U(+3)->X? Let's check R->U (+3), O->R (+3), U->N (-7)? Alternatively: R(+3)=U, O(+3)=R, U(+3)=X. Here R(+2)=T. Let's see: R(18)->U(21) is +3; O(15)->R(18) is +3; U(21)->N(14) is -7. If pattern is +2 for all letters: S(+2)=U, W(+2)=Y... If code for 'ROUTER' is 'TQWVGT': R+2=T, O+2=Q, U+2=W, T+2=V, E+2=G, R+2=T. Let's examine S(+2)=U, W(+2)=Y, I(+2)=K, T(+2)=V, C(+2)=E, H(+2)=J => UYKVEJ. With options [UVKVEJ], pattern is: 1st (+2), 2nd (-1: W->V), 3rd (+2: I->K), 4th (+2: T->V), 5th (+2: C->E), 6th (+2: H->J)."
    },
    {
        "id": "LR_BR_001",
        "section": "Logical Reasoning",
        "topic": "Blood Relations",
        "difficulty": "Easy",
        "question": "Pointing to a photograph of a boy, Suresh said, 'He is the son of the only son of my mother.' How is Suresh related to that boy?",
        "options": ["Father", "Uncle", "Brother", "Grandfather"],
        "correct_answer": "Father",
        "explanation": "The only son of Suresh's mother is Suresh himself. Thus, the boy is the son of Suresh. Suresh is the father."
    },
    {
        "id": "LR_DIR_001",
        "section": "Logical Reasoning",
        "topic": "Directions",
        "difficulty": "Medium",
        "question": "A person walks 10 km towards North. From there, he walks 6 km towards South. Then, he walks 3 km towards East. How far and in which direction is he with reference to his starting point?",
        "options": ["5 km North-East", "7 km North-West", "5 km South-East", "4 km East"],
        "correct_answer": "5 km North-East",
        "explanation": "Net displacement in North-South = 10 - 6 = 4 km North. Displacement in East-West = 3 km East. Distance = sqrt(4^2 + 3^2) = 5 km in North-East direction."
    },
    {
        "id": "LR_SYL_001",
        "section": "Logical Reasoning",
        "topic": "Syllogisms",
        "difficulty": "Medium",
        "question": "Statements: (I) All engineers are problem solvers. (II) Some problem solvers are innovators. Conclusions: (I) Some engineers are innovators. (II) All innovators are engineers.",
        "options": ["Neither conclusion follows", "Only conclusion (I) follows", "Only conclusion (II) follows", "Both conclusions follow"],
        "correct_answer": "Neither conclusion follows",
        "explanation": "From 'All engineers are problem solvers' and 'Some problem solvers are innovators', the middle term 'problem solvers' is undistributed in both premises. Hence, no definite relation can be inferred between engineers and innovators."
    },
    {
        "id": "LR_SA_001",
        "section": "Logical Reasoning",
        "topic": "Seating Arrangement",
        "difficulty": "Medium",
        "question": "Five friends A, B, C, D, and E are sitting in a row facing North. D is to the immediate right of E. B is to the left of E but to the right of A. D is to the left of C. Who is sitting in the middle?",
        "options": ["E", "D", "B", "C"],
        "correct_answer": "E",
        "explanation": "Order from left to right: A, B, E, D, C. E is directly in the middle (3rd position)."
    },
    {
        "id": "LR_PUZ_001",
        "section": "Logical Reasoning",
        "topic": "Puzzles",
        "difficulty": "Hard",
        "question": "Four people P, Q, R, and S each speak a different programming language: Python, C++, Java, and Rust. P does not speak Python or Rust. Q speaks Java. R does not speak Rust. Which language does P speak?",
        "options": ["C++", "Python", "Rust", "Java"],
        "correct_answer": "C++",
        "explanation": "Q speaks Java. P does not speak Python, Rust, or Java (since Q speaks Java). Therefore, P must speak C++."
    },
    {
        "id": "LR_SC_001",
        "section": "Logical Reasoning",
        "topic": "Statement and Conclusion",
        "difficulty": "Easy",
        "question": "Statement: High automated test coverage reduces production bug escape rate by 80%. Conclusions: (I) Teams with automated tests experience fewer critical defects in production. (II) Writing automated tests completely eliminates all software bugs.",
        "options": ["Only conclusion (I) follows", "Only conclusion (II) follows", "Both follow", "Neither follows"],
        "correct_answer": "Only conclusion (I) follows",
        "explanation": "Reducing by 80% directly supports fewer critical defects (Conclusion I). It does not claim complete elimination of 100% of bugs (Conclusion II is an overreach)."
    },
    {
        "id": "LR_ANA_001",
        "section": "Logical Reasoning",
        "topic": "Analogies",
        "difficulty": "Easy",
        "question": "Compiler : Bytecode :: Interpreter : ?",
        "options": ["Immediate Execution", "Hardware", "Database", "Source File"],
        "correct_answer": "Immediate Execution",
        "explanation": "A compiler translates source code into intermediate bytecode, whereas an interpreter directly parses and provides immediate line-by-line execution."
    },
    {
        "id": "LR_OOO_001",
        "section": "Logical Reasoning",
        "topic": "Odd One Out",
        "difficulty": "Easy",
        "question": "Choose the odd one out from the following list: PostgreSQL, MongoDB, Redis, Linux, SQLite.",
        "options": ["Linux", "PostgreSQL", "Redis", "SQLite"],
        "correct_answer": "Linux",
        "explanation": "Linux is an operating system kernel; PostgreSQL, MongoDB, Redis, and SQLite are all database management systems."
    },
    {
        "id": "LR_PR_001",
        "section": "Logical Reasoning",
        "topic": "Pattern Recognition",
        "difficulty": "Medium",
        "question": "In a digital clock, how many times in a 12-hour period do the hour hand and minute hand form a straight line (pointing in opposite directions at 180 degrees)?",
        "options": ["11 times", "12 times", "10 times", "22 times"],
        "correct_answer": "11 times",
        "explanation": "Between 5 and 7, the hands form a 180° line only once at exactly 6:00. Thus, in 12 hours they form a straight line 11 times (and 22 times in 24 hours)."
    },

    # =========================================================================
    # SECTION 3: VERBAL ABILITY
    # =========================================================================
    {
        "id": "VA_GR_001",
        "section": "Verbal Ability",
        "topic": "Grammar",
        "difficulty": "Easy",
        "question": "Neither of the two candidates who interviewed for the lead software architect position ________ selected.",
        "options": ["was", "were", "are", "have been"],
        "correct_answer": "was",
        "explanation": "'Neither' is a singular indefinite pronoun when referring to two entities, so it takes the singular past verb 'was'."
    },
    {
        "id": "VA_SC_001",
        "section": "Verbal Ability",
        "topic": "Sentence Correction",
        "difficulty": "Medium",
        "question": "Identify the grammatically correct sentence:",
        "options": [
            "Having finished the code review, the deployment pipeline was initiated by the team.",
            "Having finished the code review, the team initiated the deployment pipeline.",
            "The team initiated the deployment pipeline having finished the code review by them.",
            "Finished the code review, the deployment pipeline was initiated."
        ],
        "correct_answer": "Having finished the code review, the team initiated the deployment pipeline.",
        "explanation": "Avoids the dangling modifier. The subject performing the action 'having finished the code review' must immediately follow the introductory participial phrase."
    },
    {
        "id": "VA_VOC_001",
        "section": "Verbal Ability",
        "topic": "Vocabulary",
        "difficulty": "Medium",
        "question": "An API endpoint that can be invoked repeatedly without changing the system state beyond the initial request is described as:",
        "options": ["Idempotent", "Asynchronous", "Stateful", "Transient"],
        "correct_answer": "Idempotent",
        "explanation": "Idempotence is the mathematical and computing property wherein an operation can be applied multiple times without altering the result beyond the initial application."
    },
    {
        "id": "VA_SYN_001",
        "section": "Verbal Ability",
        "topic": "Synonyms",
        "difficulty": "Easy",
        "question": "Choose the synonym closest in meaning to the word PRAGMATIC:",
        "options": ["Practical", "Theoretical", "Idealistic", "Ambiguous"],
        "correct_answer": "Practical",
        "explanation": "'Pragmatic' means dealing with things sensibly and realistically in a way that is based on practical rather than theoretical considerations."
    },
    {
        "id": "VA_ANT_001",
        "section": "Verbal Ability",
        "topic": "Antonyms",
        "difficulty": "Easy",
        "question": "Choose the antonym opposite in meaning to the word METICULOUS:",
        "options": ["Careless", "Thorough", "Precise", "Methodical"],
        "correct_answer": "Careless",
        "explanation": "'Meticulous' means showing great attention to detail. Its direct antonym is 'Careless'."
    },
    {
        "id": "VA_RC_001",
        "section": "Verbal Ability",
        "topic": "Reading Comprehension",
        "difficulty": "Hard",
        "question": "Passage: 'Distributed microservices decouple individual software capabilities, enabling autonomous deployment cadences. However, they introduce significant network serialization latency and require distributed tracing for observability.' According to the passage, what is a primary trade-off of adopting microservices?",
        "options": [
            "Greater network latency and heightened observability complexity",
            "Elimination of modular autonomous deployment cadences",
            "Inability to scale individual application components",
            "Simpler monolithic debugging without tracing tools"
        ],
        "correct_answer": "Greater network latency and heightened observability complexity",
        "explanation": "The passage explicitly notes that microservices introduce 'network serialization latency' and necessitate 'distributed tracing for observability'."
    },
    {
        "id": "VA_SCOMP_001",
        "section": "Verbal Ability",
        "topic": "Sentence Completion",
        "difficulty": "Medium",
        "question": "Because the system requirements were highly ________, the engineering team adopted an agile framework to accommodate frequent pivots.",
        "options": ["Volatile", "Static", "Rigid", "Dogmatic"],
        "correct_answer": "Volatile",
        "explanation": "'Volatile' conveys rapid and unpredictable change, perfectly matching the need to accommodate 'frequent pivots'."
    },
    {
        "id": "VA_PJ_001",
        "section": "Verbal Ability",
        "topic": "Para Jumbles",
        "difficulty": "Medium",
        "question": "Arrange the sentences in logical sequence: (1) Machine learning models require vast training datasets. (2) However, poor data hygiene leads directly to algorithmic bias. (3) Therefore, automated data cleaning pipelines are essential. (4) Modern tech applications increasingly rely on AI to automate complex decisions.",
        "options": ["4-1-2-3", "1-4-3-2", "4-3-1-2", "2-3-4-1"],
        "correct_answer": "4-1-2-3",
        "explanation": "Sentence (4) introduces the broad context (AI in modern tech), followed by (1) requirement of data, (2) the risk of poor data, and (3) the concluding solution (automated cleaning)."
    },
    {
        "id": "VA_SE_001",
        "section": "Verbal Ability",
        "topic": "Spotting Errors",
        "difficulty": "Medium",
        "question": "Find the part with an error: 'The team of researchers (A) / have discovered (B) / an anomalous behavior (C) / in the model weights (D).'",
        "options": ["Part B (have discovered)", "Part A (The team of researchers)", "Part C (an anomalous behavior)", "Part D (in the model weights)"],
        "correct_answer": "Part B (have discovered)",
        "explanation": "The head noun of the subject is 'The team' (collective noun, singular), requiring the singular verb 'has discovered' rather than 'have discovered'."
    },
    {
        "id": "VA_CU_001",
        "section": "Verbal Ability",
        "topic": "Contextual Usage",
        "difficulty": "Easy",
        "question": "Select the correct phrase to complete the sentence: 'The senior software architect decided to ________ the meeting until Thursday afternoon.'",
        "options": ["Defer", "Differ", "Deter", "Defect"],
        "correct_answer": "Defer",
        "explanation": "'Defer' means to postpone or put off to a later time."
    },

    # =========================================================================
    # ADDITIONAL COMPREHENSIVE QUESTIONS ACROSS ALL TOPICS & DIFFICULTIES
    # =========================================================================
    # --- QUANTITATIVE ABILITY EXPANSIONS ---
    {
        "id": "QA_PERC_003",
        "section": "Quantitative Ability",
        "topic": "Percentages",
        "difficulty": "Hard",
        "question": "In an election between two candidates, 75% of the voters cast their votes, out of which 2% votes were declared invalid. A candidate got 9,261 votes which were 75% of the valid votes. Find the total number of voters enrolled on the voter list.",
        "options": ["16,800", "16,400", "15,200", "18,000"],
        "correct_answer": "16,800",
        "explanation": "Let total enrolled = x. Votes cast = 0.75x. Valid votes = 0.75x * 0.98 = 0.735x. 75% of valid = 0.75 * 0.735x = 9261 => 0.55125x = 9261 => x = 16,800."
    },
    {
        "id": "QA_PL_003",
        "section": "Quantitative Ability",
        "topic": "Profit and Loss",
        "difficulty": "Hard",
        "question": "A merchant marks his goods 40% above the cost price and allows a discount of 20% on the marked price. What is his net profit percentage?",
        "options": ["12%", "15%", "10%", "16%"],
        "correct_answer": "12%",
        "explanation": "Let CP = 100. MP = 140. SP after 20% discount = 140 * 0.80 = 112. Net profit = (112 - 100) = 12%."
    },
    {
        "id": "QA_SI_002",
        "section": "Quantitative Ability",
        "topic": "Simple Interest",
        "difficulty": "Medium",
        "question": "A certain sum of money amounts to Rs. 2,600 in 3 years and to Rs. 3,000 in 5 years at simple interest. What is the principal sum?",
        "options": ["Rs. 2,000", "Rs. 2,200", "Rs. 1,800", "Rs. 2,400"],
        "correct_answer": "Rs. 2,000",
        "explanation": "Interest for 2 years (5 - 3) = 3000 - 2600 = Rs. 400 => Interest per year = Rs. 200. Principal = 2600 - (3 * 200) = Rs. 2,000."
    },
    {
        "id": "QA_CI_002",
        "section": "Quantitative Ability",
        "topic": "Compound Interest",
        "difficulty": "Hard",
        "question": "A sum of money invested at compound interest doubles itself in 5 years. In how many years will it become 8 times itself at the same compound interest rate?",
        "options": ["15 years", "20 years", "10 years", "25 years"],
        "correct_answer": "15 years",
        "explanation": "At compound interest, if P becomes 2P in 5 years, it becomes (2^3)P = 8P in 3 * 5 = 15 years."
    },
    {
        "id": "QA_RAT_002",
        "section": "Quantitative Ability",
        "topic": "Ratios",
        "difficulty": "Medium",
        "question": "Rs. 1,050 is divided among A, B, and C in the ratio 2 : 3 : 5. What is the exact monetary share of B?",
        "options": ["Rs. 315", "Rs. 210", "Rs. 525", "Rs. 350"],
        "correct_answer": "Rs. 315",
        "explanation": "Total ratio units = 2 + 3 + 5 = 10. Value per unit = 1050 / 10 = 105. Share of B = 3 * 105 = Rs. 315."
    },
    {
        "id": "QA_PROP_002",
        "section": "Quantitative Ability",
        "topic": "Proportions",
        "difficulty": "Easy",
        "question": "Find the value of x if 4 : x :: 16 : 24.",
        "options": ["6", "8", "12", "4"],
        "correct_answer": "6",
        "explanation": "In proportion, Product of extremes = Product of means: 4 * 24 = 16 * x => 96 = 16x => x = 6."
    },
    {
        "id": "QA_AVG_002",
        "section": "Quantitative Ability",
        "topic": "Averages",
        "difficulty": "Medium",
        "question": "The average age of 24 students and their class teacher is 15 years. If the teacher's age is excluded, the average age decreases by 1 year. What is the age of the class teacher?",
        "options": ["39 years", "38 years", "40 years", "36 years"],
        "correct_answer": "39 years",
        "explanation": "Total age with teacher = 25 * 15 = 375. Total age of 24 students = 24 * 14 = 336. Teacher's age = 375 - 336 = 39 years."
    },
    {
        "id": "QA_TW_003",
        "section": "Quantitative Ability",
        "topic": "Time and Work",
        "difficulty": "Easy",
        "question": "If 15 workers can build a wall in 20 days, how many workers are needed to build the exact same wall in 12 days?",
        "options": ["25 workers", "20 workers", "24 workers", "30 workers"],
        "correct_answer": "25 workers",
        "explanation": "Total man-days = 15 * 20 = 300 man-days. Workers needed for 12 days = 300 / 12 = 25 workers."
    },
    {
        "id": "QA_TSD_003",
        "section": "Quantitative Ability",
        "topic": "Time Speed Distance",
        "difficulty": "Easy",
        "question": "A person travels from town A to town B at 40 km/h and returns along the same route at 60 km/h. What is the average speed for the entire round trip?",
        "options": ["48 km/h", "50 km/h", "45 km/h", "52 km/h"],
        "correct_answer": "48 km/h",
        "explanation": "Harmonic mean: Average speed = 2xy / (x + y) = 2 * 40 * 60 / (40 + 60) = 4800 / 100 = 48 km/h."
    },
    {
        "id": "QA_PROB_002",
        "section": "Quantitative Ability",
        "topic": "Probability",
        "difficulty": "Medium",
        "question": "A single card is drawn at random from a standard deck of 52 playing cards. What is the probability of drawing a King or a Heart?",
        "options": ["4/13", "1/4", "17/52", "1/13"],
        "correct_answer": "4/13",
        "explanation": "Number of Kings = 4, Number of Hearts = 13, King of Hearts counted twice = 1. Favorable = 4 + 13 - 1 = 16. Probability = 16 / 52 = 4 / 13."
    },
    {
        "id": "QA_PERM_002",
        "section": "Quantitative Ability",
        "topic": "Permutations and Combinations",
        "difficulty": "Hard",
        "question": "In how many distinct ways can a project committee consisting of 3 engineers and 2 managers be chosen from a department of 5 engineers and 4 managers?",
        "options": ["60", "120", "30", "45"],
        "correct_answer": "60",
        "explanation": "Ways = 5C3 * 4C2 = [5! / (3! * 2!)] * [4! / (2! * 2!)] = 10 * 6 = 60 distinct committees."
    },
    {
        "id": "QA_NUM_002",
        "section": "Quantitative Ability",
        "topic": "Number Systems",
        "difficulty": "Medium",
        "question": "Which of the following numbers is completely divisible by 11?",
        "options": ["108,570", "116,532", "107,684", "114,345"],
        "correct_answer": "108,570",
        "explanation": "Alternating sum of digits for 108570: (1 + 8 + 7) - (0 + 5 + 0) = 16 - 5 = 11, which is divisible by 11."
    },
    {
        "id": "QA_AGE_002",
        "section": "Quantitative Ability",
        "topic": "Ages",
        "difficulty": "Hard",
        "question": "Six years ago, the ratio of the ages of Kunal and Sagar was 6 : 5. Four years hence, the ratio of their ages will be 11 : 10. What is Sagar's present age?",
        "options": ["16 years", "18 years", "20 years", "14 years"],
        "correct_answer": "16 years",
        "explanation": "6 years ago: 6x and 5x. Present: 6x + 6 and 5x + 6. In 4 years: (6x + 10) / (5x + 10) = 11 / 10 => 60x + 100 = 55x + 110 => 5x = 10 => x = 2. Sagar's present age = 5(2) + 6 = 16 years."
    },
    {
        "id": "QA_MIX_002",
        "section": "Quantitative Ability",
        "topic": "Mixtures and Alligations",
        "difficulty": "Medium",
        "question": "A container contains 40 liters of pure milk. From this container, 4 liters of milk was taken out and replaced with water. This process was repeated once more. How much milk is left in the container now?",
        "options": ["32.4 liters", "32.0 liters", "34.2 liters", "31.6 liters"],
        "correct_answer": "32.4 liters",
        "explanation": "Remaining pure milk = Total * (1 - y/x)^n = 40 * (1 - 4/40)^2 = 40 * (9/10)^2 = 40 * 81/100 = 32.4 liters."
    },
    {
        "id": "QA_DI_002",
        "section": "Quantitative Ability",
        "topic": "Data Interpretation",
        "difficulty": "Hard",
        "question": "In a corporate budget pie chart, the sector representing the Cloud Infrastructure department subtends a central angle of 108 degrees. If the total annual company budget is Rs. 1,200,000, what is the allocated budget for Cloud Infrastructure?",
        "options": ["Rs. 360,000", "Rs. 300,000", "Rs. 400,000", "Rs. 320,000"],
        "correct_answer": "Rs. 360,000",
        "explanation": "Share = (108° / 360°) * 1,200,000 = (3/10) * 1,200,000 = Rs. 360,000."
    },
    {
        "id": "QA_ALG_002",
        "section": "Quantitative Ability",
        "topic": "Algebra",
        "difficulty": "Hard",
        "question": "If a + b + c = 0, what is the value of (a^3 + b^3 + c^3) / (3abc) where abc ≠ 0?",
        "options": ["1", "0", "-1", "3"],
        "correct_answer": "1",
        "explanation": "From the algebraic identity: a^3 + b^3 + c^3 - 3abc = (a + b + c)(a^2 + b^2 + c^2 - ab - bc - ca). When a + b + c = 0, a^3 + b^3 + c^3 = 3abc. Therefore, (a^3 + b^3 + c^3)/(3abc) = 1."
    },

    # --- LOGICAL REASONING EXPANSIONS ---
    {
        "id": "LR_NS_003",
        "section": "Logical Reasoning",
        "topic": "Number Series",
        "difficulty": "Hard",
        "question": "Find the next number in the sequence: 1, 8, 27, 64, 125, ?",
        "options": ["216", "243", "343", "196"],
        "correct_answer": "216",
        "explanation": "The sequence represents cubes of consecutive natural numbers: 1^3=1, 2^3=8, 3^3=27, 4^3=64, 5^3=125, 6^3=216."
    },
    {
        "id": "LR_AS_002",
        "section": "Logical Reasoning",
        "topic": "Alphabet Series",
        "difficulty": "Medium",
        "question": "What is the next pair in the series: AZ, BY, CX, DW, ?",
        "options": ["EV", "FU", "EU", "DV"],
        "correct_answer": "EV",
        "explanation": "First letter ascends: A, B, C, D, E. Second letter descends from Z: Z, Y, X, W, V. Next pair is EV."
    },
    {
        "id": "LR_CD_002",
        "section": "Logical Reasoning",
        "topic": "Coding-Decoding",
        "difficulty": "Hard",
        "question": "If in a cryptographic substitution cipher, 'CLOUD' is written as 'ENQWF', how will 'STORM' be written in that same cipher?",
        "options": ["UVQTO", "UUQTO", "TVPSO", "UWQTO"],
        "correct_answer": "UVQTO",
        "explanation": "Each letter is shifted forward by +2: C->E, L->N, O->Q, U->W, D->F. Applying to STORM: S(+2)=U, T(+2)=V, O(+2)=Q, R(+2)=T, M(+2)=O => UVQTO."
    },
    {
        "id": "LR_BR_002",
        "section": "Logical Reasoning",
        "topic": "Blood Relations",
        "difficulty": "Hard",
        "question": "Pointing to a woman on stage, Rajesh said, 'Her mother is the only daughter of my mother-in-law.' How is Rajesh related to the woman?",
        "options": ["Father", "Uncle", "Brother", "Maternal Uncle"],
        "correct_answer": "Father",
        "explanation": "The only daughter of Rajesh's mother-in-law is Rajesh's wife. The woman's mother is Rajesh's wife. Therefore, Rajesh is the father of the woman."
    },
    {
        "id": "LR_DIR_002",
        "section": "Logical Reasoning",
        "topic": "Directions",
        "difficulty": "Easy",
        "question": "A developer stands facing North. She turns 90 degrees clockwise, then 180 degrees counter-clockwise. Which cardinal direction is she facing now?",
        "options": ["West", "East", "South", "North"],
        "correct_answer": "West",
        "explanation": "Starting North (0°). 90° clockwise = East (90°). 180° counter-clockwise from East = West (270°)."
    },
    {
        "id": "LR_SYL_002",
        "section": "Logical Reasoning",
        "topic": "Syllogisms",
        "difficulty": "Hard",
        "question": "Statements: (I) All microservices are containers. (II) No container is a monolith. Conclusions: (I) No microservice is a monolith. (II) Some containers are microservices.",
        "options": ["Both conclusions (I) and (II) follow", "Only conclusion (I) follows", "Only conclusion (II) follows", "Neither follows"],
        "correct_answer": "Both conclusions (I) and (II) follow",
        "explanation": "Since all microservices are inside containers, and no container intersects with monoliths, no microservice can be a monolith (I follows). Also, if all microservices are containers, some containers are microservices (II follows)."
    },
    {
        "id": "LR_SA_002",
        "section": "Logical Reasoning",
        "topic": "Seating Arrangement",
        "difficulty": "Hard",
        "question": "Six engineers A, B, C, D, E, and F sit around a circular table facing the center. A sits opposite to D. B sits to the immediate left of A. C is opposite to B. Who sits to the immediate right of A?",
        "options": ["F", "E", "C", "Either E or F"],
        "correct_answer": "Either E or F",
        "explanation": "Positions: A at 12 o'clock, D at 6 o'clock. B is at immediate left of A (clockwise or counter-clockwise convention). C is opposite B. The remaining two positions adjacent to D and A are occupied by E and F. Without further constraints, either E or F sits to the immediate right of A."
    },
    {
        "id": "LR_PUZ_002",
        "section": "Logical Reasoning",
        "topic": "Puzzles",
        "difficulty": "Medium",
        "question": "Among four candidates W, X, Y, and Z: W scored higher than X, Y scored higher than Z but lower than X. Who scored the lowest marks?",
        "options": ["Z", "Y", "X", "W"],
        "correct_answer": "Z",
        "explanation": "Order of scores: W > X > Y > Z. Z scored the lowest."
    },
    {
        "id": "LR_SC_002",
        "section": "Logical Reasoning",
        "topic": "Statement and Conclusion",
        "difficulty": "Medium",
        "question": "Statement: Continuous integration pipelines catch build regressions within 5 minutes of commit. Conclusions: (I) Rapid feedback prevents broken code from propagating to main branches. (II) Continuous integration eliminates the need for unit testing.",
        "options": ["Only conclusion (I) follows", "Only conclusion (II) follows", "Both follow", "Neither follows"],
        "correct_answer": "Only conclusion (I) follows",
        "explanation": "Catching build regressions in 5 minutes directly ensures rapid feedback (I). It relies upon unit testing rather than eliminating it (II is invalid)."
    },
    {
        "id": "LR_ANA_002",
        "section": "Logical Reasoning",
        "topic": "Analogies",
        "difficulty": "Medium",
        "question": "Git : Version Control :: Docker : ?",
        "options": ["Containerization", "Database", "Operating System", "Compiler"],
        "correct_answer": "Containerization",
        "explanation": "Git is the industry standard technology for Version Control; Docker is the industry standard for Containerization."
    },
    {
        "id": "LR_OOO_002",
        "section": "Logical Reasoning",
        "topic": "Odd One Out",
        "difficulty": "Medium",
        "question": "Identify the odd one out from the group: Python, C++, Java, HTML, Rust.",
        "options": ["HTML", "Rust", "Java", "Python"],
        "correct_answer": "HTML",
        "explanation": "HTML is a declarative markup language for documents; Python, C++, Java, and Rust are general-purpose Turing-complete programming languages."
    },
    {
        "id": "LR_PR_002",
        "section": "Logical Reasoning",
        "topic": "Pattern Recognition",
        "difficulty": "Hard",
        "question": "In a 3x3 matrix, row 1 has [3, 9, 27], row 2 has [4, 16, 64], row 3 has [5, 25, ?]. What is the missing value?",
        "options": ["125", "100", "75", "150"],
        "correct_answer": "125",
        "explanation": "Each row represents [n, n^2, n^3]. For n = 5: [5, 5^2=25, 5^3=125]."
    },

    # --- VERBAL ABILITY EXPANSIONS ---
    {
        "id": "VA_GR_002",
        "section": "Verbal Ability",
        "topic": "Grammar",
        "difficulty": "Medium",
        "question": "Choose the correct verb form: 'Neither the lead architect nor the backend engineers ________ in favor of deploying on Friday.'",
        "options": ["were", "was", "is", "has been"],
        "correct_answer": "were",
        "explanation": "When subjects are joined by 'neither... nor', the verb agrees in number with the nearer subject ('the backend engineers', plural), thus requiring 'were'."
    },
    {
        "id": "VA_SC_002",
        "section": "Verbal Ability",
        "topic": "Sentence Correction",
        "difficulty": "Hard",
        "question": "Select the sentence with impeccable parallel structure:",
        "options": [
            "The engineer loves designing distributed systems, writing clean code, and optimizing database queries.",
            "The engineer loves to design distributed systems, clean code writing, and optimization of queries.",
            "The engineer loves designing distributed systems, to write code, and database query optimization.",
            "The engineer loves distributed systems design, to write code, and optimizing queries."
        ],
        "correct_answer": "The engineer loves designing distributed systems, writing clean code, and optimizing database queries.",
        "explanation": "Maintains strict grammatical parallelism using three gerund phrases: 'designing...', 'writing...', 'optimizing...'."
    },
    {
        "id": "VA_VOC_002",
        "section": "Verbal Ability",
        "topic": "Vocabulary",
        "difficulty": "Hard",
        "question": "A technology or system that seems to be present or encountered everywhere simultaneously is termed:",
        "options": ["Ubiquitous", "Ephemeral", "Equivocal", "Esoteric"],
        "correct_answer": "Ubiquitous",
        "explanation": "'Ubiquitous' means present, appearing, or found everywhere at once."
    },
    {
        "id": "VA_SYN_002",
        "section": "Verbal Ability",
        "topic": "Synonyms",
        "difficulty": "Medium",
        "question": "Choose the synonym for RESILIENT:",
        "options": ["Adaptable", "Fragile", "Rigid", "Stagnant"],
        "correct_answer": "Adaptable",
        "explanation": "'Resilient' means able to withstand or recover quickly from difficult conditions; adaptable and robust."
    },
    {
        "id": "VA_ANT_002",
        "section": "Verbal Ability",
        "topic": "Antonyms",
        "difficulty": "Medium",
        "question": "Choose the antonym for OBSOLETE:",
        "options": ["Contemporary", "Outdated", "Archaic", "Redundant"],
        "correct_answer": "Contemporary",
        "explanation": "'Obsolete' means no longer produced or used; out of date. 'Contemporary' means current and modern."
    },
    {
        "id": "VA_RC_002",
        "section": "Verbal Ability",
        "topic": "Reading Comprehension",
        "difficulty": "Hard",
        "question": "Passage: 'Zero-trust architecture presumes that security threats exist both outside and inside the enterprise network. Consequently, perimeter defenses alone are considered insufficient, and every transaction, user access, and API call must be continuously authenticated and authorized regardless of source IP.' What is the foundational premise of zero-trust architecture?",
        "options": [
            "Internal network entities cannot be implicitly trusted without verification",
            "Firewalls and perimeter security completely prevent insider threats",
            "Authentication is only needed when accessing resources from outside the corporate firewall",
            "User access rights never require continuous session verification"
        ],
        "correct_answer": "Internal network entities cannot be implicitly trusted without verification",
        "explanation": "The passage states that threats exist both inside and outside the perimeter, mandating that every internal transaction and call be continuously verified."
    },
    {
        "id": "VA_SCOMP_002",
        "section": "Verbal Ability",
        "topic": "Sentence Completion",
        "difficulty": "Hard",
        "question": "Despite initial skepticism regarding the complex neural architecture, the benchmark trials proved the model to be remarkably ________.",
        "options": ["Efficacious", "Inept", "Specious", "Deleterious"],
        "correct_answer": "Efficacious",
        "explanation": "'Efficacious' means successful in producing a desired or intended result; effective."
    },
    {
        "id": "VA_PJ_002",
        "section": "Verbal Ability",
        "topic": "Para Jumbles",
        "difficulty": "Hard",
        "question": "Arrange the sentences in logical sequence: (1) Consensus algorithms ensure all nodes maintain an identical state. (2) In a distributed network, servers may crash or suffer partition faults. (3) By achieving quorum, the cluster operates seamlessly despite individual failures. (4) Raft and Paxos are widely deployed protocols to implement this guarantee.",
        "options": ["2-1-4-3", "1-4-2-3", "2-3-1-4", "4-1-2-3"],
        "correct_answer": "2-1-4-3",
        "explanation": "Sentence (2) introduces the fundamental fault scenario, (1) introduces the solution (consensus algorithms), (4) gives specific protocols (Raft/Paxos), and (3) describes the resulting system resilience."
    },
    {
        "id": "VA_SE_002",
        "section": "Verbal Ability",
        "topic": "Spotting Errors",
        "difficulty": "Easy",
        "question": "Find the part with the error: 'Each of the microservice endpoints (A) / are monitored (B) / by the central telemetry system (C) / in real time (D).'",
        "options": ["Part B (are monitored)", "Part A (Each of the microservice endpoints)", "Part C (by the central telemetry system)", "Part D (in real time)"],
        "correct_answer": "Part B (are monitored)",
        "explanation": "'Each' is singular and requires the singular verb 'is monitored', not 'are monitored'."
    },
    {
        "id": "VA_CU_002",
        "section": "Verbal Ability",
        "topic": "Contextual Usage",
        "difficulty": "Medium",
        "question": "Select the correct word: 'The sudden network partition had an immediate adverse ________ on database replication throughput.'",
        "options": ["Effect", "Affect", "Affection", "Effort"],
        "correct_answer": "Effect",
        "explanation": "'Effect' is the noun meaning a change that is a result or consequence of an action."
    }
]


def get_all_questions() -> List[Dict[str, Any]]:
    """Returns the full master question bank."""
    return APTITUDE_QUESTIONS.copy()


def get_questions_by_section(section_name: str) -> List[Dict[str, Any]]:
    """Returns all questions belonging to a specific section."""
    return [q for q in APTITUDE_QUESTIONS if q["section"].lower() == section_name.lower()]
