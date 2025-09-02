import re
from typing import List, Dict, Tuple

# Example profanity list (expand as needed)
PROFANITY_WORDS = [
    'damn', 'hell', 'shit', 'fuck', 'bitch', 'bastard', 'asshole', 'crap', 'dick', 'piss', 
    'slut', 'whore', 'cunt', 'fag', 'douche', 'deadbeat', 'loser', 'liar', 'fraud', 'sue you', 'jail', 
    'arrest', 'threat', 'stupid', 'idiot', 'moron', 'retard', 'shut up', 'ruin you', 'garnish'
]
PROFANITY_REGEX = re.compile(r'\b(' + '|'.join(map(re.escape, PROFANITY_WORDS)) + r')\b', re.IGNORECASE)

SENSITIVE_PATTERNS = [
    r"\bbalance\b",# Any balance mention
    r"\baccount\b",# Any account reference
    r"\bowe\b.*\$\d+",# "You owe $X"
    r"\boutstanding\b",# Outstanding amounts/balances
    r"\$\d+", # Any dollar amount
    r"card\s*(details|number|info|information)", # Card information requests
    r"\bcvv\b",# CVV code requests
    r"expiration\s*date",# Expiration date requests
    r"credit\s*card",# Credit card references
    r"payment\s*(method|info|information|details)", # Payment method requests
    r"provide.*card",# "Please provide your card..."
    r"card\s*number",# Card number references
    r"payment.*process",# Payment processing mentions
    r"processing.*payment",# Processing acknowledgments
    r"account\s*number",# Account number references
    r"social\s*security",# SSN references
    r"\bssn\b[\s:]*\d{3}-?\d{2}-?\d{4}",# SSN with numbers
    r"\b\d{3}-\d{2}-\d{4}\b",# Standalone SSN pattern
    r"\bdebt\b",# Debt mentions
    r"\bamount\s*due\b",# Amount due
    r"\btotal\s*owed\b"# Total owed
]
SENSITIVE_REGEX = re.compile('|'.join(SENSITIVE_PATTERNS), re.IGNORECASE)

# Verification patterns
VERIFICATION_PATTERNS = [
    r'date of birth',
    r'dob',
    r'address',
    r'ssn',
]
VERIFICATION_REGEX = re.compile('|'.join(VERIFICATION_PATTERNS), re.IGNORECASE)


CUSTOMER_VERIFICATION_RESPONSES = [
    r"\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b",# 03/15/1985, 3-15-85, 3.15.85
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b",  # March 15, 1985
    r"\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4}\b",  # 15 Mar 85
    r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",# 123-45-6789, 123 45 6789
    r"\blast\s+four\s+(are\s+)?\d{4}\b",# "last four are 1234"
    r"\bending\s+(in\s+|with\s+)?\d{4}\b",# "ending in 1234"
    r"\b\d+\s+\w+\s+(street|st|avenue|ave|road|rd|lane|ln|drive|dr|court|ct|way|place|pl)\b",  # 123 Main Street
    r"\b\d{5}(?:-\d{4})?\b",# ZIP codes: 12345
    r"\b(yes|yeah|yep|correct|right|that'?s\s+right|that'?s\s+correct|exactly|absolutely)\b",  # Various confirmations
]
CUSTOMER_VERIFICATION_REGEX = re.compile('|'.join(CUSTOMER_VERIFICATION_RESPONSES), re.IGNORECASE)

"""
This module provides regex-based detection for:
- Profanity usage by agents and borrowers (with call_id extraction)
- Privacy/compliance violations (sensitive info shared without verification)

New functions:
- detect_agent_profanity_call_ids: Returns set of call_ids where agents used profanity
- detect_borrower_profanity_call_ids: Returns set of call_ids where borrowers used profanity
"""
def detect_profanity(utterances: List[Dict]) -> List[Dict]:
    """
    Returns a list of utterances containing profanity, with speaker and text.
    """
    results = []
    for utt in utterances:
        if PROFANITY_REGEX.search(utt['text']):
            results.append({
                'call_id': utt.get('call_id'),
                'speaker': utt['speaker'],
                'text': utt['text'],
                'stime': utt['stime'],
                'etime': utt['etime']
            })
    return results

def detect_privacy_violations(utterances: List[Dict]) -> List[Dict]:
    """
    Returns a list of agent utterances where sensitive info is shared (flag all, regardless of verification).
    """
    results = []
    for utt in utterances:
        if utt['speaker'].lower() == 'agent' and SENSITIVE_REGEX.search(utt['text']):
            results.append({
                'call_id': utt.get('call_id'),
                'speaker': utt['speaker'],
                'text': utt['text'],
                'stime': utt['stime'],
                'etime': utt['etime']
            })
    return results

def detect_agent_profanity_call_ids(utterances: List[Dict]) -> set:
    """
    Returns a set of call_ids where agents have used profane language.
    """
    return set(
        utt['call_id']
        for utt in utterances
        if utt['speaker'].lower() == 'agent' and PROFANITY_REGEX.search(utt['text'])
    )

def detect_borrower_profanity_call_ids(utterances: List[Dict]) -> set:
    """
    Returns a set of call_ids where borrowers have used profane language.
    """
    return set(
        utt['call_id']
        for utt in utterances
        if utt['speaker'].lower() == 'customer' and PROFANITY_REGEX.search(utt['text'])
    )

def detect_agent_privacy_violation_call_ids(utterances: List[Dict]) -> set:
    """
    Returns a set of call_ids where agents have shared sensitive information.
    """
    return set(
        utt['call_id']
        for utt in utterances
        if utt['speaker'].lower() == 'agent' and SENSITIVE_REGEX.search(utt['text'])
    )

def detect_privacy_violations_with_verification(utterances: List[Dict]) -> List[Dict]:
    """
    Enhanced privacy violation detection that checks if customer verification 
    occurred BEFORE agent sensitive information sharing.
    Returns violations only where sensitive info was shared without prior verification.
    """
    # Group utterances by call_id
    calls = {}
    for utt in utterances:
        call_id = utt.get('call_id')
        if call_id not in calls:
            calls[call_id] = []
        calls[call_id].append(utt)
    
    violations = []
    
    for call_id, call_utterances in calls.items():
        # Sort by start time for temporal analysis
        call_utterances.sort(key=lambda x: x.get('stime', 0))
        
        # Track verification status
        verification_completed_time = None
        
        for utt in call_utterances:
            speaker = utt.get('speaker', '').lower()
            text = utt.get('text', '')
            current_time = utt.get('stime', 0)
            
            # Check if customer provided verification
            if speaker == 'customer':
                if CUSTOMER_VERIFICATION_REGEX.search(text):
                    if verification_completed_time is None:
                        verification_completed_time = current_time
            
            # Check if agent shared sensitive info
            elif speaker == 'agent':
                if SENSITIVE_REGEX.search(text):
                    # Violation if no verification OR sensitive sharing happened first
                    if (verification_completed_time is None or 
                        current_time < verification_completed_time):
                        violations.append({
                            'call_id': call_id,
                            'speaker': utt['speaker'],
                            'text': text,
                            'stime': current_time,
                            'etime': utt.get('etime'),
                            'violation_reason': f"Sensitive info shared at {current_time}s, verification at {verification_completed_time if verification_completed_time is not None else 'never'}"
                        })
    
    return violations

def detect_agent_privacy_violation_call_ids_with_verification(utterances: List[Dict]) -> set:
    """
    Returns a set of call_ids where agents shared sensitive info WITHOUT proper prior verification.
    This is the enhanced version that considers temporal verification analysis.
    """
    violations = detect_privacy_violations_with_verification(utterances)
    return set(violation['call_id'] for violation in violations)
