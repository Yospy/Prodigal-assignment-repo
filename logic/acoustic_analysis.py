from typing import List, Dict, Tuple

def calculate_overtalk_percentage(utterances: List[Dict]) -> float:

    if not utterances or len(utterances) < 2:
        return 0.0
    
    # Sort utterances by start time
    sorted_utterances = sorted(utterances, key=lambda x: x.get('stime', 0))
    
    total_call_duration = _calculate_total_call_duration(sorted_utterances)
    if total_call_duration <= 0:
        return 0.0
    
    total_overtalk = 0.0
    

    for i in range(len(sorted_utterances)):
        for j in range(i + 1, len(sorted_utterances)):
            utt1 = sorted_utterances[i]
            utt2 = sorted_utterances[j]
            

            if utt1.get('speaker', '').lower() == utt2.get('speaker', '').lower():
                continue
            
            overlap = min(utt1.get('etime', 0), utt2.get('etime', 0)) - max(utt1.get('stime', 0), utt2.get('stime', 0))
            
            if overlap > 0:
                total_overtalk += overlap
    
    return (total_overtalk / total_call_duration) * 100

def calculate_silence_percentage(utterances: List[Dict]) -> float:

    if not utterances:
        return 0.0
    

    sorted_utterances = sorted(utterances, key=lambda x: x.get('stime', 0))
    
    total_call_duration = _calculate_total_call_duration(sorted_utterances)
    if total_call_duration <= 0:
        return 0.0
    
    total_silence = 0.0
    
    for i in range(len(sorted_utterances) - 1):
        current_end = sorted_utterances[i].get('etime', 0)
        next_start = sorted_utterances[i + 1].get('stime', 0)
        
        gap = next_start - current_end
        if gap > 0:
            total_silence += gap
    
    return (total_silence / total_call_duration) * 100

def get_acoustic_metrics(utterances: List[Dict]) -> Tuple[float, float]:

    overtalk_pct = calculate_overtalk_percentage(utterances)
    silence_pct = calculate_silence_percentage(utterances)
    
    return overtalk_pct, silence_pct

def _calculate_total_call_duration(sorted_utterances: List[Dict]) -> float:

    if not sorted_utterances:
        return 0.0
    
    first_start = sorted_utterances[0].get('stime', 0)
    last_end = sorted_utterances[-1].get('etime', 0)
    
    return max(0.0, last_end - first_start)