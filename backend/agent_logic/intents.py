"""
Intent Detection System for ValtricAI
Handles deterministic recall queries and profile memory extraction.
"""

import re
from typing import Optional

# Recall patterns - what the user asked previously
RECALL_PATTERNS = [
    r"\bwhat did i (just )?ask\??",
    r"\bwhat (was|were) (my|the) (previous|last)\s+(question|message)\??", 
    r"\bremind me what i (said|asked)\b",
    r"\bwhat did i say (earlier|before|prior)\b",
    r"\bwhat did i tell you (earlier|before|prior)\b",
    r"\brepeat my (last |previous )?question\b",
    r"\bwhat was i asking\b"
]

# Name query patterns - asking for stored name
WHAT_NAME_PATTERNS = [
    r"\bwhat('?s| is) my name\??",
    r"\bdo you know my name\b", 
    r"\bwhat do you call me\b",
    r"\bremember my name\b"
]

# Company query patterns - asking for stored company
WHAT_COMPANY_PATTERNS = [
    r"\bwhat company do i work (at|for)\??",
    r"\bwhere do i work\??",
    r"\bwhat('?s| is) my company\??",
    r"\bremember my company\b"
]

# Role query patterns - asking for stored role  
WHAT_ROLE_PATTERNS = [
    r"\bwhat('?s| is) my (job|role|position)\??",
    r"\bwhat do i do for work\??",
    r"\bremember my (job|role)\b"
]

# Name declaration patterns - telling the AI their name
NAME_DECLARE_PATTERNS = [
    r"\b(my name is|call me|i am|i'm)\s+([a-z][a-z\-' ]{1,40})\b",
    r"\bi go by\s+([a-z][a-z\-' ]{1,40})\b"
]

# Company/role patterns
COMPANY_DECLARE_PATTERNS = [
    r"\bi work (at|for)\s+([a-z][a-z\-' ]{1,60})\b",
    r"\b(my company is|i'm at)\s+([a-z][a-z\-' ]{1,60})\b"
]

ROLE_DECLARE_PATTERNS = [
    r"\bi am (a |an )?([a-z][a-z\- ]{1,40})\b",
    r"\b(my role is|my job is|i'm a|i'm an)\s+([a-z][a-z\- ]{1,40})\b"
]

def is_recall(text: str) -> bool:
    """Detect if user is asking for recall of previous messages"""
    t = text.lower().strip()
    return any(re.search(p, t) for p in RECALL_PATTERNS)

def is_what_name(text: str) -> bool:
    """Detect if user is asking what their name is"""
    t = text.lower().strip()
    return any(re.search(p, t) for p in WHAT_NAME_PATTERNS)

def is_what_company(text: str) -> bool:
    """Detect if user is asking what their company is"""
    t = text.lower().strip()
    return any(re.search(p, t) for p in WHAT_COMPANY_PATTERNS)

def is_what_role(text: str) -> bool:
    """Detect if user is asking what their role is"""
    t = text.lower().strip()
    return any(re.search(p, t) for p in WHAT_ROLE_PATTERNS)

def extract_name(text: str) -> Optional[str]:
    """Extract name from user declaration like 'My name is John'"""
    for pattern in NAME_DECLARE_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            # Get the captured name group (last group in pattern)
            raw_name = match.groups()[-1].strip()
            # Clean and capitalize properly
            pretty_name = " ".join(w.capitalize() for w in re.split(r"\s+", raw_name))
            return pretty_name[:60]  # Limit length
    return None

def extract_company(text: str) -> Optional[str]:
    """Extract company from user declaration"""
    for pattern in COMPANY_DECLARE_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raw_company = match.groups()[-1].strip()
            # Clean but preserve original case for company names
            return " ".join(raw_company.split())[:60]
    return None

def extract_role(text: str) -> Optional[str]:
    """Extract role/job title from user declaration"""
    for pattern in ROLE_DECLARE_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raw_role = match.groups()[-1].strip()
            # Skip common words that aren't roles
            skip_words = {"person", "guy", "man", "woman", "human", "here", "good", "fine", "okay"}
            if raw_role.lower() not in skip_words:
                return " ".join(raw_role.split())[:40]
    return None

def has_name_declaration(text: str) -> bool:
    """Check if text contains name declaration"""
    return extract_name(text) is not None

def has_company_declaration(text: str) -> bool:
    """Check if text contains company declaration"""  
    return extract_company(text) is not None

def has_role_declaration(text: str) -> bool:
    """Check if text contains role declaration"""
    return extract_role(text) is not None