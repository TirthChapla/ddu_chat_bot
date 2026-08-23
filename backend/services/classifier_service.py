"""
Query Intent & Category Classifier Service
Categorizes user queries to improve retrieval precision.
"""

import re
from typing import Dict, List, Tuple


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "attendance": [
        "attendance", "absent", "presence", "75%", "shortage", "condonation", "medical leave",
        "debarred", "detain", "detained", "lecture", "bunk", "medical certificate", "minimum attendance"
    ],
    "admissions": [
        "admission", "admit", "acpc", "eligibility", "criteria", "cutoff", "cut-off", "rank", "merit",
        "quota", "nri", "management quota", "gujcet", "jee", "apply", "form", "b.tech", "mca admission"
    ],
    "placements": [
        "placement", "package", "ctc", "lpa", "salary", "recruiter", "company", "companies",
        "job", "intern", "internship", "tpo", "t&p", "amazon", "tcs", "highest package", "average package",
        "backlog rule for placement", "eligible for placement"
    ],
    "examinations": [
        "exam", "examination", "spi", "cpi", "grade", "grading", "marks", "result", "backlog",
        "atkt", "remedial", "re-check", "rechecking", "reassessment", "re-assessment", "sessional", "cpa",
        "pass marks", "fail", "transcript", "evaluation"
    ],
    "fees_scholarships": [
        "fee", "fees", "tuition", "cost", "scholarship", "mysy", "freeship", "freeship card",
        "waiver", "tfws", "financial aid", "installment", "penalty", "late fee", "bank", "payment"
    ],
    "departments": [
        "department", "it branch", "computer engineering", "ce branch", "chemical", "mechanical",
        "civil", "ec branch", "ic branch", "pharmacy", "dental", "bds", "b.pharm", "faculty", "professor",
        "lab", "laboratory", "syllabus", "curriculum"
    ],
    "hostel": [
        "hostel", "room", "mess", "food", "dining", "curfew", "stay", "accommodation",
        "warden", "boys hostel", "girls hostel", "wifi in hostel", "hostel rent"
    ],
    "circulars_faqs": [
        "circular", "notice", "calendar", "academic calendar", "holiday", "event", "date",
        "vacation", "bonafide", "duplicate marksheet", "contact", "email", "phone", "address", "location"
    ]
}


class QueryClassifierService:
    @staticmethod
    def classify_query(query: str, explicit_category: str = None) -> Tuple[str, float]:
        """
        Classifies user query into one of the core categories.
        Returns: (category, confidence_score)
        """
        if explicit_category and explicit_category in CATEGORY_KEYWORDS:
            return explicit_category, 1.0

        query_clean = query.lower()
        scores: Dict[str, int] = {cat: 0 for cat in CATEGORY_KEYWORDS}

        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', query_clean):
                    scores[cat] += 2
                elif kw in query_clean:
                    scores[cat] += 1

        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]

        if max_score > 0:
            confidence = min(0.95, 0.6 + (max_score * 0.1))
            return best_category, confidence

        return "general", 0.5
