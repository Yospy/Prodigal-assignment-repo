import os
import json
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def detect_profanity_llm(utterances: List[Dict]) -> Dict:
    """
    Use OpenAI to detect profanity in conversation utterances.
    Returns results in the same format as regex detection.
    """
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY')
    client = OpenAI(api_key=api_key)
    
    if not client.api_key:
        raise ValueError("OPENAI_API_KEY or OPENAI_KEY environment variable not found")
    
    system_prompt = """
Analyze debt collection transcripts for profanity/inappropriate language by agents or customers

Return ONLY this JSON:
{
  "profanity_utterances": [
    {"call_id": "x", "speaker": "Agent", "text": "actual text", "stime": 0, "etime": 5}
  ],
  "agent_profanity_call_ids": ["call_id1"],
  "borrower_profanity_call_ids": ["call_id1"]
}

Focus on truly inappropriate language in debt collection context. Return empty arrays if none found
"""
    
    # Prepare conversation text
    conversation_text = []
    for utt in utterances:
        conversation_text.append(f"Speaker: {utt['speaker']}, Text: \"{utt['text']}\", Call ID: {utt.get('call_id', 'unknown')}, Start: {utt['stime']}, End: {utt['etime']}")
    
    user_message = "Conversation to analyze:\n" + "\n".join(conversation_text)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0
        )
        
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        
        # Ensure all required keys exist
        return {
            "profanity_utterances": result.get("profanity_utterances", []),
            "agent_profanity_call_ids": result.get("agent_profanity_call_ids", []),
            "borrower_profanity_call_ids": result.get("borrower_profanity_call_ids", [])
        }
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}")
        return {"profanity_utterances": [], "agent_profanity_call_ids": [], "borrower_profanity_call_ids": []}
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {"profanity_utterances": [], "agent_profanity_call_ids": [], "borrower_profanity_call_ids": []}

def detect_privacy_violations_llm(utterances: List[Dict]) -> Dict:
    """
    Use OpenAI to detect privacy violations where agents share sensitive information
    WITHOUT proper customer identity verification.
    Returns enhanced results with verification context.
    """
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY')
    client = OpenAI(api_key=api_key)
    
    if not client.api_key:
        raise ValueError("OPENAI_API_KEY or OPENAI_KEY environment variable not found")
    
    system_prompt = """
Identify privacy violations where agents share sensitive info WITHOUT proper customer verification

VERIFICATION COMPLETE when customer provides: DOB, address, SSN, or confirms verification questions
SENSITIVE INFO: Account balances, payment amounts, account numbers, personal financial details

TEMPORAL RULE: Agent sharing at time X, customer verification at time Y:
- VIOLATION if X < Y (sharing before verification) OR no verification
- NO VIOLATION if Y < X (verification before sharing)

Return ONLY this JSON:
{
  "privacy_violations": [
    {"call_id": "x", "speaker": "Agent", "text": "actual text", "stime": 0, "etime": 5, "reasoning": "brief explanation"}
  ],
  "agent_privacy_violation_call_ids": ["call_id1"],
  "verification_summary": {
    "call_id1": {"verified": true, "violation_count": 1, "verification_time": 15, "violation_time": 5}
  }
}

Focus on temporal order - what happened first?
"""
    
    # Group utterances by call_id and sort chronologically
    calls = {}
    for utt in utterances:
        call_id = utt.get('call_id', 'unknown')
        if call_id not in calls:
            calls[call_id] = []
        calls[call_id].append(utt)
    
    # Sort utterances within each call by start time
    for call_id in calls:
        calls[call_id].sort(key=lambda x: x.get('stime', 0))
    
    all_violations = []
    all_violation_call_ids = set()
    verification_summary = {}
    
    # Process each call individually for better context
    for call_id, call_utterances in calls.items():
        try:
            # Prepare complete call conversation text
            conversation_text = []
            for utt in call_utterances:
                conversation_text.append(f"Speaker: {utt.get('speaker', 'Unknown')}, Text: \"{utt['text']}\", Start: {utt['stime']}, End: {utt['etime']}")
            
            user_message = f"Complete call conversation for Call ID {call_id} (chronologically ordered):\n" + "\n".join(conversation_text)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0
            )
            
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            # Aggregate results from this call
            call_violations = result.get("privacy_violations", [])
            for violation in call_violations:
                violation['call_id'] = call_id  # Ensure call_id is set
                all_violations.append(violation)
            
            call_violation_ids = result.get("agent_privacy_violation_call_ids", [])
            all_violation_call_ids.update(call_violation_ids)
            
            # Store verification summary for this call
            call_summary = result.get("verification_summary", {})
            verification_summary.update(call_summary)
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response for call {call_id}: {e}")
            continue
        except Exception as e:
            print(f"OpenAI API error for call {call_id}: {e}")
            continue
    
    # Return aggregated results
    return {
        "privacy_violations": all_violations,
        "agent_privacy_violation_call_ids": list(all_violation_call_ids),
        "verification_summary": verification_summary
    }